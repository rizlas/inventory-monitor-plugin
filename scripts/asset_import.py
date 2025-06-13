import codecs
import csv
import sys
from datetime import datetime

from dcim.models import InventoryItem
from django.core.exceptions import ObjectDoesNotExist
from extras.scripts import *

from inventory_monitor.models import Asset, AssetService, Contract

REQUIRED_FIELDS = "manufacturer,part_nmr,quantity,contract_price,sn_original,order_contract,project,service_from,service_to,service_contract,service_price"


def check_required_fields(self, reader):
    required_fields = REQUIRED_FIELDS.split(",")
    fieldnames = reader.fieldnames

    for required_field in required_fields:
        if required_field not in fieldnames:
            self.log_failure(f"Missing required field: {required_field} in csv file")
            return False

    return True


def map_params(self, record):
    object_defaults = {
        "manufacturer": "",
        "part_nmr": "",
        "quantity": 0,
        "contract_price": 0,
        "sn_original": "",
        "order_contract": None,
        "project": "",
        "service_from": None,
        "service_to": None,
        "service_contract": None,
        "service_price": 0,
    }

    object_defaults["manufacturer"] = record["manufacturer"] if record["manufacturer"] else ""
    object_defaults["part_nmr"] = record["part_nmr"] if record["part_nmr"] else ""
    object_defaults["quantity"] = int(record["quantity"]) if record["quantity"] else 0
    object_defaults["contract_price"] = float(record["contract_price"]) if record["contract_price"] else 0
    object_defaults["sn_original"] = record["sn_original"] if record["sn_original"] else ""
    object_defaults["order_contract"] = record["order_contract"] if record["order_contract"] else None
    object_defaults["project"] = record["project"] if record["project"] else ""

    if record["service_from"]:
        object_defaults["service_from"] = datetime.strptime(record["service_from"], "%d.%m.%Y").date()
    else:
        object_defaults["service_from"] = None
    if record["service_to"]:
        object_defaults["service_to"] = datetime.strptime(record["service_to"], "%d.%m.%Y").date()
    else:
        object_defaults["service_to"] = None

    object_defaults["service_contract"] = record["service_contract"] if record["service_contract"] else None
    object_defaults["service_price"] = record["service_price"] if record["service_price"] else 0
    return object_defaults


def return_asset_table_str(self, rec):
    return f"""
| Manufacturer | Part Number | Quantity | Price | SN Original | Order Contract | Project | Service From | Service To | Service Contract | Service Price |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| {rec["manufacturer"]}   | {rec["part_nmr"]} | {rec["quantity"]} | {rec["contract_price"]} | {rec["sn_original"]} | {rec["order_contract"]} | {rec["project"]} | {rec["service_from"]} | {rec["service_to"]} | {rec["service_contract"]} | {rec["service_price"]} |
    """


def record_process_table(data, headers=["Type", "Info", "Action", "Params"]):
    head = " | " + " | ".join(headers) + " | "
    sep = " | " + " | ".join(["---"] * len(headers)) + " | "
    lines = []
    for row in data:
        table_row = " | " + " | ".join([str(d) for d in row]) + " | "
        lines.append(table_row)

    mkdown_lines = "\n".join(lines)

    return f"""
{head}
{sep}
{mkdown_lines}
    """


def get_log_type(self, record_messages):
    if len(record_messages) == 0:
        return "Success"
    else:
        for msg in record_messages:
            if msg[0] == "Failure":
                return "Failure"
            elif msg[0] == "Warning":
                return "Warning"
        return "Success"


def log_result(self, log_type, messages):
    if log_type == "Warning":
        self.log_warning(record_process_table(messages))
    elif log_type == "Failure":
        self.log_failure(record_process_table(messages))
    else:
        self.log_success(record_process_table(messages))


class UpdateAssetWithInventory(Script):
    class Meta:
        name = "Update Asset with Inventory"
        description = "Checks all assets, found Inventory Item and link it together"
        commit_default = False

    def run(self, data, commit):
        for asset in Asset.objects.all():
            try:
                invs = InventoryItem.objects.filter(serial=asset.serial).order_by("-created")
                if invs:
                    inv = invs[0]
                else:
                    continue

                asset_numbers = inv.cf.get("asset_numbers")
                device = inv.device
                site = device.site if device else None
                location = device.location if device else None

                if asset.pk and hasattr(asset, "snapshot"):
                    asset.snapshot()

                change = False

                # Update assignment to device using the new GenericForeignKey system
                if device:
                    from django.contrib.contenttypes.models import ContentType

                    device_ct = ContentType.objects.get_for_model(device)

                    if asset.assigned_object_type != device_ct or asset.assigned_object_id != device.id:
                        asset.assigned_object_type = device_ct
                        asset.assigned_object_id = device.id
                        change = True
                elif asset.assigned_object_type or asset.assigned_object_id:
                    # Clear assignment if no device found
                    asset.assigned_object_type = None
                    asset.assigned_object_id = None
                    change = True

                if change:
                    asset.save()
                    self.log_success(
                        f"Inventory: {inv}, Asset Numbers: {asset_numbers}, Device: {device}, Site: {site}, Location: {location}"
                    )
            except Exception as e:
                raise e


class ImportAsset(Script):
    class Meta:
        name = "Import Asset - Inventory Monitor"
        description = "Imports/Updates assets from CSV file. If inventory item exists to asset, it will be assigned"
        commit_default = False

    assets_file = FileVar(label="Assets CSV file", description=f"Required Fields: {REQUIRED_FIELDS}", required=True)

    def run(self, data, commit):
        try:
            file = data["assets_file"]
            csvReader = csv.DictReader(codecs.iterdecode(file, "utf-8-sig"), delimiter=",")

            if check_required_fields(self, csvReader) == False:
                return

            # Generate a list comprehension
            line_cnt = 1
            for record in csvReader:
                self.log_debug(f"#### Record number {line_cnt}")
                line_cnt += 1
                record_messages = []

                rec = map_params(self, record)
                self.log_info(return_asset_table_str(self, rec))

                # TODO: Check if component serial exists (if not, create it with WARNING)
                if rec.get("sn_original") == "":
                    record_messages.append(["Failure", "Missing original SN", "Skipping record", "No serial provided"])
                    log_type = get_log_type(self, record_messages)
                    log_result(self, log_type, record_messages)

                    continue

                # Lookup for asset
                try:
                    nb_asset = Asset.objects.get(serial=rec.get("sn_original"))
                except ObjectDoesNotExist:
                    nb_asset = None

                # Contract must exists
                try:
                    csv_order_contract = rec.get("order_contract", None)
                    if not csv_order_contract:
                        record_messages.append(["Warning", "Missing order contract", "-", "No contract provided"])
                        nb_order_contract = None
                    else:
                        nb_order_contract = Contract.objects.get(name=rec.get("order_contract"))
                except ObjectDoesNotExist:
                    record_messages.append(
                        [
                            "Failure",
                            "Order contract not found",
                            "Skipping record",
                            f" Service Contract: {rec.get('order_contract')}",
                        ]
                    )
                    log_type = get_log_type(self, record_messages)
                    log_result(self, log_type, record_messages)

                    continue

                # if service contract is set, it must exists
                if rec.get("service_contract"):
                    try:
                        nb_service_contract = Contract.objects.get(name=rec.get("service_contract"))
                    except ObjectDoesNotExist:
                        record_messages.append(
                            [
                                "Failure",
                                "Service contract not found",
                                "Skipping record",
                                f"Service Contract: {rec.get('service_contract')}",
                            ]
                        )
                        log_type = get_log_type(self, record_messages)
                        log_result(self, log_type, record_messages)

                        continue
                else:
                    nb_service_contract = None

                # Create asset if it does not exist
                if not nb_asset:
                    nb_asset = Asset.objects.create(
                        vendor=rec.get("manufacturer"),
                        partnumber=rec.get("part_nmr"),
                        quantity=rec.get("quantity"),
                        price=rec.get("contract_price"),
                        serial=rec.get("sn_original"),
                        order_contract=nb_order_contract,
                        project=rec.get("project"),
                    )
                    record_messages.append(
                        ["Success", "Asset created", "Record created", f"SN original: {rec.get('sn_original')}"]
                    )
                else:
                    record_messages.append(
                        ["Warning", "Asset already exists", "-", f"SN original: {rec.get('sn_original')}"]
                    )

                # Create service if it does not exist and service contract is provided
                if nb_asset and nb_service_contract:
                    nb_asset_services = AssetService.objects.filter(asset=nb_asset)
                    # check if service exists
                    try:
                        nb_asset_service = nb_asset_services.get(
                            contract=nb_service_contract,
                            service_start=rec.get("service_from"),
                            service_end=rec.get("service_to"),
                            service_price=rec.get("service_price"),
                        )
                    except ObjectDoesNotExist:
                        nb_asset_service = None
                    if nb_asset_service:
                        record_messages.append(
                            [
                                "Warning",
                                "Service already exists",
                                "Skipping record",
                                f"From: {rec.get('service_from')}, To: {rec.get('service_to')}, Price: {rec.get('service_price')}, Contract: {nb_service_contract.name}",
                            ]
                        )
                    else:
                        nb_asset_service = AssetService.objects.create(
                            asset=nb_asset,
                            contract=nb_service_contract,
                            service_start=rec.get("service_from"),
                            service_end=rec.get("service_to"),
                            service_price=rec.get("service_price"),
                        )
                        record_messages.append(
                            [
                                "Success",
                                "Service created",
                                "Record created",
                                f"From: {rec.get('service_from')}, To: {rec.get('service_to')}, Price: {rec.get('service_price')}, Contract: {nb_service_contract.name}",
                            ]
                        )

                try:
                    inventory_item = InventoryItem.objects.get(serial=rec.get("sn_original"))
                except ObjectDoesNotExist:
                    inventory_item = None

                if inventory_item:
                    asset_numbers = inventory_item.cf.get("asset_numbers")
                    device = inventory_item.device
                    site = device.site if device else None
                    location = device.location if device else None

                    if nb_asset.pk and hasattr(nb_asset, "snapshot"):
                        nb_asset.snapshot()

                    change = False
                    asset = nb_asset
                    inv = inventory_item

                    # Update assignment to device using the new GenericForeignKey system
                    if device:
                        from django.contrib.contenttypes.models import ContentType

                        device_ct = ContentType.objects.get_for_model(device)

                        if asset.assigned_object_type != device_ct or asset.assigned_object_id != device.id:
                            asset.assigned_object_type = device_ct
                            asset.assigned_object_id = device.id
                            change = True
                    elif asset.assigned_object_type or asset.assigned_object_id:
                        # Clear assignment if no device found
                        asset.assigned_object_type = None
                        asset.assigned_object_id = None
                        change = True

                    if change:
                        asset.save()
                        record_messages.append(
                            [
                                "Success",
                                "Inventory item found and assigned",
                                "Assign",
                                f"Inventory: {inv}, Asset Numbers: {asset_numbers}, Device: {device}, Site: {site}, Location: {location}",
                            ]
                        )

                log_type = get_log_type(self, record_messages)
                log_result(self, log_type, record_messages)

        except Exception as e:
            # return line number
            self.log_failure(f"Error on line {sys.exc_info()[-1].tb_lineno}: {type(e).__name__} - {e}")
            self.log_failure(str(e))
            return

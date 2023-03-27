import codecs
import csv
from datetime import datetime

from dcim.models import InventoryItem
from django.core.exceptions import ObjectDoesNotExist
from extras.scripts import *
from inventory_monitor.models import Component, ComponentService, Contract

REQUIRED_FIELDS = "manufacturer,part_nmr,quantity,contract_price,sn_original,sn_actual,order_contract,project,service_from,service_to,service_contract,service_price"


def check_required_fields(self, reader):
    required_fields = REQUIRED_FIELDS.split(
        ",")
    fieldnames = reader.fieldnames

    for required_field in required_fields:
        if required_field not in fieldnames:
            self.log_failure(
                f"Missing required field: {required_field} in csv file")
            return False

    return True


def map_params(self, record):
    object_defaults = {
        "manufacturer": "",
        "part_nmr": "",
        "quantity": 0,
        "contract_price": 0,
        "sn_original": "",
        "sn_actual": "",
        "order_contract": None,
        "project": "",
        "service_from": None,
        "service_to": None,
        "service_contract": None,
        "service_price": 0
    }

    object_defaults['manufacturer'] = record['manufacturer'] if record['manufacturer'] else ""
    object_defaults['part_nmr'] = record['part_nmr'] if record['part_nmr'] else ""
    object_defaults['quantity'] = int(
        record['quantity']) if record['quantity'] else 0
    object_defaults['contract_price'] = float(
        record['contract_price']) if record['contract_price'] else 0
    object_defaults['sn_original'] = record['sn_original'] if record['sn_original'] else ""
    object_defaults['sn_actual'] = record['sn_actual'] if record['sn_actual'] else ""
    object_defaults['order_contract'] = record['order_contract'] if record['order_contract'] else None
    object_defaults['project'] = record['project'] if record['project'] else ""

    if record["service_from"]:
        object_defaults['service_from'] = datetime.strptime(
            record["service_from"], "%d.%m.%Y").date()  # .strftime("%Y-%m-%d")
    else:
        object_defaults['service_from'] = None
    if record["service_to"]:
        object_defaults['service_to'] = datetime.strptime(
            record["service_to"], "%d.%m.%Y").date()  # .strftime("%Y-%m-%d")
    else:
        object_defaults['service_to'] = None

    object_defaults['service_contract'] = record['service_contract'] if record['service_contract'] else None
    object_defaults['service_price'] = record['service_price'] if record['service_price'] else 0

    # If sn_actual is empty, use sn_original
    if not object_defaults['sn_actual']:
        object_defaults['sn_actual'] = object_defaults['sn_original']

    return object_defaults


def return_component_table_str(self, rec):
    return f"""
| Manufacturer | Part Number | Quantity | Price | SN Original | SN Actual | Order Contract | Project | Service From | Service To | Service Contract | Service Price |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| {rec['manufacturer']}   | {rec['part_nmr']} | {rec['quantity']} | {rec['contract_price']} | {rec['sn_original']} | {rec['sn_actual']} | {rec['order_contract']} | {rec['project']} | {rec['service_from']} | {rec['service_to']} | {rec['service_contract']} | {rec['service_price']} |
    """


def record_process_table(data, headers=["Type", "Info", "Action", "Params"]):
    head = " | " + " | ".join(headers) + " | "
    sep = " | " + " | ".join(["---"]*len(headers)) + " | "
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


class ImportComponent(Script):

    class Meta:
        name = "Import Component - Inventory Monitor"
        description = "Imports/Updates components from CSV file. If inventory item exists to component, it will be assigned"
        commit_default = False

    components_file = FileVar(
        label="Components CSV file",
        description=f"Required Fields: {REQUIRED_FIELDS}",
        required=True
    )

    def run(self, data, commit):
        try:
            file = data['components_file']
            csvReader = csv.DictReader(codecs.iterdecode(
                file, 'utf-8-sig'), delimiter=',')

            if check_required_fields(self, csvReader) == False:
                return

            # Generate a list comprehension
            line_cnt = 1
            for record in csvReader:
                self.log_debug(f"#### Record number {line_cnt}")
                line_cnt += 1
                record_messages = []

                rec = map_params(self, record)
                self.log_info(return_component_table_str(self, rec))

                # TODO: Check if component serial exists (if not, create it with WARNING)
                if rec.get('sn_original') == "":
                    record_messages.append(
                        ["Failure", "Missing original SN", "Skipping record", "No serial provided"])
                    log_type = get_log_type(self, record_messages)
                    log_result(self, log_type, record_messages)

                    # self.log_failure(record_process_table(record_messages))
                    continue

                # Lookup for component
                try:
                    nb_component = Component.objects.get(
                        serial=rec.get('sn_original'))
                except ObjectDoesNotExist:
                    nb_component = None

                # Check if component serial_actual matches
                if nb_component and nb_component.serial_actual != rec.get('sn_actual'):
                    record_messages.append(["Warning", "Actual SN does not match", "TODO - Potřeba domluvit co dělat",
                                           f"NetBox SN actual: {nb_component.serial_actual} CSV SN actual: {rec.get('sn_actual')}"])

                # Contract must exists
                try:
                    nb_order_contract = Contract.objects.get(
                        name=rec.get('order_contract'))
                except ObjectDoesNotExist:
                    record_messages.append(
                        ["Failure", "Order contract not found", "Skipping record", f" Service Contract: {rec.get('order_contract')}"])
                    log_type = get_log_type(self, record_messages)
                    log_result(self, log_type, record_messages)
                    # self.log_failure(record_process_table(record_messages))
                    continue

                # if service contract is set, it must exists
                if rec.get('service_contract'):
                    try:
                        nb_service_contract = Contract.objects.get(
                            name=rec.get('service_contract'))
                    except ObjectDoesNotExist:
                        record_messages.append(
                            ["Failure", "Service contract not found", "Skipping record", f"Service Contract: {rec.get('service_contract')}"])
                        log_type = get_log_type(self, record_messages)
                        log_result(self, log_type, record_messages)
                        # self.log_failure(record_process_table(record_messages))
                        continue
                else:
                    nb_service_contract = None

                # Create component if it does not exist
                if not nb_component:
                    nb_component = Component.objects.create(vendor=rec.get('manufacturer'),
                                                            partnumber=rec.get(
                                                                'part_nmr'),
                                                            quantity=rec.get(
                                                                'quantity'),
                                                            price=rec.get(
                                                                'contract_price'),
                                                            serial=rec.get(
                                                                'sn_original'),
                                                            serial_actual=rec.get(
                                                                'sn_actual'),
                                                            order_contract=nb_order_contract,
                                                            project=rec.get('project'))
                    record_messages.append(
                        ["Success", "Component created", "Record created", f"SN original: {rec.get('sn_original')}"])
                else:
                    record_messages.append(
                        ["Warning", "Component already exists", "-", f"SN original: {rec.get('sn_original')}"])

                # Create service if it does not exist
                if nb_component:
                    nb_component_services = ComponentService.objects.filter(
                        component_id=nb_component.id)
                    # check if service exists
                    try:
                        nb_component_service = nb_component_services.get(contract_id=nb_service_contract.id,
                                                                         service_start=rec.get(
                                                                             'service_from'),
                                                                         service_end=rec.get(
                                                                             'service_to'),
                                                                         service_price=rec.get('service_price'))
                    except ObjectDoesNotExist:
                        nb_component_service = None
                    if nb_component_service:
                        record_messages.append(["Warning", "Service already exists", "Skipping record",
                                               f"From: {rec.get('service_from')}, To: {rec.get('service_to')}, Price: {rec.get('service_price')}, Contract: {nb_service_contract.name}"])
                    else:
                        nb_component_service = ComponentService.objects.create(component_id=nb_component.id,
                                                                               contract_id=nb_service_contract.id,
                                                                               service_start=rec.get(
                                                                                   'service_from'),
                                                                               service_end=rec.get(
                                                                                   'service_to'),
                                                                               service_price=rec.get('service_price'))
                        record_messages.append(["Success", "Service created", "Record created",
                                               f"From: {rec.get('service_from')}, To: {rec.get('service_to')}, Price: {rec.get('service_price')}, Contract: {nb_service_contract.name}"])

                try:
                    inventory_item = InventoryItem.objects.get(
                        serial=rec.get('sn_original'))
                except ObjectDoesNotExist:
                    inventory_item = None

                if inventory_item:
                    asset_numbers = inventory_item.cf.get('asset_numbers')
                    # device
                    device = inventory_item.device

                    # locality
                    site = device.site
                    location = device.location

                    if nb_component.pk and hasattr(nb_component, 'snapshot'):
                        nb_component.snapshot()

                    change = False

                    if nb_component.inventory_item != inventory_item:
                        nb_component.inventory_item = inventory_item
                        change = True
                    if nb_component.device != device:
                        nb_component.device = device
                        change = True
                    if nb_component.site != site:
                        nb_component.site = site
                        change = True
                    if nb_component.location != location:
                        nb_component.location = location
                        change = True
                    if nb_component.asset_number != asset_numbers:
                        nb_component.asset_number = asset_numbers
                        if nb_component.asset_number == None:
                            nb_component.asset_number = ""
                        change = True

                    if change:
                        nb_component.save()
                        record_messages.append(["Success", "Inventory item found and assigned", "Assign",
                                                f"Inventory: {inventory_item}, Asset: {asset_numbers},  Device: {device}, Site: {site}, Location: {location}"])

                    # part descr, end of support UNSET

                log_type = get_log_type(self, record_messages)
                log_result(self, log_type, record_messages)

                # if log_type == "Warning":
                #    self.log_warning(record_process_table(record_messages))
                # elif log_type == "Failure":
                #    self.log_failure(record_process_table(record_messages))
                # else:
                #    self.log_success(record_process_table(record_messages))

        except Exception as e:
            # retrun line number
            import sys
            self.log_failure(
                f"Error on line {sys.exc_info()[-1].tb_lineno}: {type(e).__name__} - {e}")
            self.log_failure(str(e))
            return

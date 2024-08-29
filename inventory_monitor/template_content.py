from dcim.models import InventoryItem
from django.conf import settings
from netbox.plugins import PluginTemplateExtension

from inventory_monitor.models import Contractor

plugin_settings = settings.PLUGINS_CONFIG.get("inventory_monitor", {})
import_component_url = plugin_settings.get(
    "import_component_url", "/extras/scripts/component_import.ImportComponent/"
)


class DeviceProbeList(PluginTemplateExtension):
    model = "dcim.device"

    def full_width_page(self):
        return self.render(
            "inventory_monitor/device_probes_include.html",
        )


class InventoryItemDuplicates(PluginTemplateExtension):
    model = "dcim.inventoryitem"

    def right_page(self):
        obj = self.context["object"]

        inv_duplicates = (
            InventoryItem.objects.filter(serial=obj.serial)
            .exclude(id=obj.id)
            .order_by("-custom_field_data__inventory_monitor_last_probe")
        )

        return self.render(
            "inventory_monitor/inventory_item_duplicates_include.html",
            extra_context={
                "current_inv": obj,
                "inv_duplicates": inv_duplicates,
                "inv_duplicates_count": inv_duplicates.count(),
            },
        )


class ImportComponentScriptButton(PluginTemplateExtension):
    model = "inventory_monitor.component"

    def list_buttons(self):
        return self.render(
            "inventory_monitor/import_component_button.html",
            extra_context={"url": import_component_url},
        )


class TenantContractorExtension(PluginTemplateExtension):
    model = "tenancy.tenant"

    def left_page(self):
        contractor = Contractor.objects.filter(
            tenant_id=self.context["object"].pk
        ).first()

        contracts_count = contractor.contracts.count() if contractor else 0

        return self.render(
            "inventory_monitor/tenant_contractor_extension.html",
            extra_context={
                "contractor": contractor,
                "contracts_count": contracts_count,
            },
        )


template_extensions = [
    DeviceProbeList,
    InventoryItemDuplicates,
    ImportComponentScriptButton,
    TenantContractorExtension,
]

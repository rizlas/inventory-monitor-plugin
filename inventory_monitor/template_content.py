from dcim.models import InventoryItem
from django.conf import settings
from netbox.plugins import PluginTemplateExtension
from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from inventory_monitor.models import Asset, Contractor, Probe
from inventory_monitor.tables import ProbeTable

plugin_settings = settings.PLUGINS_CONFIG.get("inventory_monitor", {})
import_asset_url = plugin_settings.get(
    "import_asset_url", "/extras/scripts/asset_import.ImportAsset/"
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


class ImportAssetScriptButton(PluginTemplateExtension):
    model = "inventory_monitor.asset"

    def list_buttons(self):
        return self.render(
            "inventory_monitor/import_asset_button.html",
            extra_context={"url": import_asset_url},
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


class InventoryItemAssetExtenstion(PluginTemplateExtension):
    model = "dcim.inventoryitem"

    def right_page(self):
        assets = self.context["object"].assets.all()

        return self.render(
            "inventory_monitor/inventory_item_asset_extension.html",
            extra_context={
                "assets": assets,
            },
        )


@register_model_view(Asset, name="probes", path="probes")
class AssetProbesView(generic.ObjectChildrenView):
    queryset = Asset.objects.all()
    child_model = Probe
    table = ProbeTable  # You'll need to create this table class
    template_name = "inventory_monitor/inc/asset_probes.html"
    hide_if_empty = False
    tab = ViewTab(
        label="Probes",
        badge=lambda obj: obj.get_related_probes().count(),
        permission="inventory_monitor.view_probe",
    )

    def get_children(self, request, parent):
        return parent.get_related_probes()


template_extensions = [
    DeviceProbeList,
    InventoryItemDuplicates,
    ImportAssetScriptButton,
    TenantContractorExtension,
    InventoryItemAssetExtenstion,
]

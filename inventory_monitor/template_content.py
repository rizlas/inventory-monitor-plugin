from dcim.models import Device, InventoryItem, Location, Module, Rack, Site
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from netbox.plugins import PluginTemplateExtension
from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from inventory_monitor.models import Asset, Contractor, Probe
from inventory_monitor.tables import AssetTable, ProbeTable

plugin_settings = settings.PLUGINS_CONFIG.get("inventory_monitor", {})
# import_asset_url = plugin_settings.get(
#    "import_asset_url", "/extras/scripts/asset_import.ImportAsset/"
# )


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


# class ImportAssetScriptButton(PluginTemplateExtension):
#    model = "inventory_monitor.asset"
#
#    def list_buttons(self):
#        return self.render(
#            "inventory_monitor/import_asset_button.html",
#            extra_context={"url": import_asset_url},
#        )


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

    def full_width_page(self):
        assets = self.context["object"].assets.all()
        asset_table = AssetTable(assets)

        return self.render(
            "inventory_monitor/inc/inventory_item_asset_extension.html",
            extra_context={
                "assets": assets,
                "asset_table": asset_table,
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


class AssignedAssetsView(generic.ObjectChildrenView):
    """Generic view to display assets assigned to an object"""

    child_model = Asset
    table = AssetTable  # You'll need to create this table class if it doesn't exist
    template_name = "inventory_monitor/inc/assigned_assets.html"
    hide_if_empty = False

    def get_children(self, request, parent):
        """Get assets assigned to this object"""
        content_type = ContentType.objects.get_for_model(parent)
        return Asset.objects.filter(
            assigned_object_type=content_type, assigned_object_id=parent.pk
        )


def register_asset_view_for_models(*models):
    """Factory function to register asset views for multiple models"""
    views = []

    for model in models:
        # Create class name based on model name
        class_name = f"{model.__name__}AssetsView"

        # Create view class
        view_class = type(
            class_name,
            (AssignedAssetsView,),
            {
                "queryset": model.objects.all(),
                "tab": ViewTab(
                    label="Assets",
                    badge=lambda obj, model=model: Asset.objects.filter(
                        assigned_object_type=ContentType.objects.get_for_model(model),
                        assigned_object_id=obj.pk,
                    ).count(),
                    permission="inventory_monitor.view_asset",
                ),
            },
        )

        # Register view with model
        register_model_view(model, name="assets", path="assets")(view_class)
        views.append(view_class)

    return views


# Register asset views for all models that can have assets assigned
register_asset_view_for_models(Site, Location, Rack, Device, Module)

template_extensions = [
    DeviceProbeList,
    InventoryItemDuplicates,
    TenantContractorExtension,
    InventoryItemAssetExtenstion,
]

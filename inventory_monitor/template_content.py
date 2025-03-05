"""
Template Extensions and Views for Inventory Monitor Plugin.

This module provides NetBox UI customizations including:
- Template extensions for displaying inventory data
- Custom views for assets and probes
- Dynamic view registration for different model types
"""

from dcim.models import Device, InventoryItem, Location, Module, Rack, Site
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from netbox.plugins import PluginTemplateExtension
from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from inventory_monitor.filtersets import AssetFilterSet, ProbeFilterSet
from inventory_monitor.models import Asset, Contract, Contractor, Probe
from inventory_monitor.tables import AssetTable, ProbeTable

# Load plugin configuration settings
plugin_settings = settings.PLUGINS_CONFIG.get("inventory_monitor", {})


class DeviceProbeList(PluginTemplateExtension):
    """Display probe data for a device on its detail page."""

    model = "dcim.device"

    def full_width_page(self):
        """Render probes list in the full width section of the page."""
        return self.render(
            "inventory_monitor/inc/device_probes_include.html",
        )


class InventoryItemDuplicates(PluginTemplateExtension):
    """Show potential duplicate inventory items with the same serial number."""

    model = "dcim.inventoryitem"

    def right_page(self):
        """Display duplicate items in the right sidebar."""
        obj = self.context["object"]

        # Find inventory items with matching serial number (excluding current item)
        inv_duplicates = (
            InventoryItem.objects.filter(serial=obj.serial)
            .exclude(id=obj.id)
            .order_by("-custom_field_data__inventory_monitor_last_probe")
        )

        return self.render(
            "inventory_monitor/inc/inventory_item_duplicates_include.html",
            extra_context={
                "current_inv": obj,
                "inv_duplicates": inv_duplicates,
                "inv_duplicates_count": inv_duplicates.count(),
            },
        )


class TenantContractorExtension(PluginTemplateExtension):
    """Display contractor information on tenant detail page."""

    model = "tenancy.tenant"

    def left_page(self):
        """Show contractor details in the left sidebar."""
        # Find contractor associated with this tenant
        contractor = Contractor.objects.filter(
            tenant_id=self.context["object"].pk
        ).first()

        # Count contracts if contractor exists
        contracts_count = contractor.contracts.count() if contractor else 0

        return self.render(
            "inventory_monitor/inc/tenant_contractor_extension.html",
            extra_context={
                "contractor": contractor,
                "contracts_count": contracts_count,
            },
        )


class InventoryItemAssetExtension(PluginTemplateExtension):
    """Show assets associated with an inventory item."""

    model = "dcim.inventoryitem"

    def full_width_page(self):
        """Display asset table in full width section."""
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
    """Provides a 'Probes' tab on asset detail pages showing related probe records."""

    queryset = Asset.objects.all()
    child_model = Probe
    table = ProbeTable
    filterset = ProbeFilterSet
    template_name = "generic/object_children.html"
    hide_if_empty = False
    tab = ViewTab(
        label="Probes",
        badge=lambda obj: obj.get_related_probes().count(),
        permission="inventory_monitor.view_probe",
    )

    def get_children(self, request, parent):
        """Retrieve all probes related to this asset."""
        return parent.get_related_probes()


@register_model_view(Contract, name="assets", path="assets")
class ContractAssetsView(generic.ObjectChildrenView):
    """View to display assets ordered through this contract."""

    queryset = Contract.objects.all()
    child_model = Asset
    filterset = AssetFilterSet
    table = AssetTable
    template_name = "generic/object_children.html"
    hide_if_empty = False
    tab = ViewTab(
        label="Assets",
        badge=lambda obj: obj.assets.count(),
        permission="inventory_monitor.view_asset",
    )

    def get_children(self, request, parent):
        """Get assets where this contract is the order_contract."""
        return parent.assets.all()


class AssignedAssetsView(generic.ObjectChildrenView):
    """Base class for views that display assets assigned to any object type."""

    child_model = Asset
    table = AssetTable
    template_name = "generic/object_children.html"
    filterset = AssetFilterSet
    hide_if_empty = False

    def get_children(self, request, parent):
        """Get assets assigned to this object using the ContentType framework."""
        content_type = ContentType.objects.get_for_model(parent)
        return Asset.objects.filter(
            assigned_object_type=content_type, assigned_object_id=parent.pk
        )


def register_asset_view_for_models(*models):
    """
    Factory function to register asset views for multiple models.

    Dynamically creates view classes for each model to avoid duplicating code.
    Each view shows assets assigned to objects of that model type.

    Args:
        *models: List of models to register asset views for

    Returns:
        list: Created view classes
    """
    views = []

    for model in models:
        # Create class name based on model name
        class_name = f"{model.__name__}AssetsView"

        # Create view class dynamically
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

# Template extensions to be registered by the plugin
template_extensions = [
    DeviceProbeList,
    InventoryItemDuplicates,
    TenantContractorExtension,
    InventoryItemAssetExtension,
]

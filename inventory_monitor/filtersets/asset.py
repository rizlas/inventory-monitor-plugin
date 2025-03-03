import django_filters
from dcim.models import Device, InventoryItem, Location, Rack, Site
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from extras.filters import TagFilter
from netbox.filtersets import NetBoxModelFilterSet
from utilities.filters import (
    ContentTypeFilter,
    MultiValueNumberFilter,
)

from inventory_monitor.models import Asset, AssetType, Contract


class AssetFilterSet(NetBoxModelFilterSet):
    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )
    tag = TagFilter()
    serial = django_filters.CharFilter(lookup_expr="iexact", field_name="serial")
    serial_actual = django_filters.CharFilter(
        lookup_expr="iexact", field_name="serial_actual"
    )
    partnumber = django_filters.CharFilter(
        lookup_expr="iexact", field_name="partnumber"
    )

    assignment_status = django_filters.MultipleChoiceFilter(
        choices=Asset.assignment_status.field.choices,
    )

    assigned_object_type = ContentTypeFilter()
    assigned_object_id = MultiValueNumberFilter()

    lifecycle_status = django_filters.MultipleChoiceFilter(
        choices=Asset.lifecycle_status.field.choices,
    )

    type_id = django_filters.ModelMultipleChoiceFilter(
        required=False,
        field_name="type__id",
        queryset=AssetType.objects.all(),
        to_field_name="id",
        label="Type (ID)",
    )

    device = django_filters.ModelMultipleChoiceFilter(
        required=False,
        field_name="device__id",
        queryset=Device.objects.all(),
        to_field_name="id",
        label="Device (ID)",
    )
    location = django_filters.ModelMultipleChoiceFilter(
        required=False,
        field_name="location__id",
        queryset=Location.objects.all(),
        to_field_name="id",
        label="Device (ID)",
    )
    inventory_item = django_filters.ModelMultipleChoiceFilter(
        required=False,
        field_name="inventory_item__id",
        queryset=InventoryItem.objects.all(),
        to_field_name="id",
        label="Inventory Item (ID)",
    )
    asset_number = django_filters.CharFilter(
        lookup_expr="icontains", field_name="asset_number"
    )
    project = django_filters.CharFilter(lookup_expr="icontains")
    vendor = django_filters.CharFilter(lookup_expr="icontains", field_name="vendor")
    price = django_filters.NumberFilter(
        required=False,
        field_name="price",
        lookup_expr="exact",
    )
    price__gte = django_filters.NumberFilter(
        required=False,
        field_name="price",
        lookup_expr="gte",
    )
    price__lte = django_filters.NumberFilter(
        required=False,
        field_name="price",
        lookup_expr="lte",
    )
    quantity = django_filters.NumberFilter(
        required=False,
        field_name="quantity",
        lookup_expr="exact",
    )
    quantity__gte = django_filters.NumberFilter(
        required=False,
        field_name="quantity",
        lookup_expr="gte",
    )
    quantity__lte = django_filters.NumberFilter(
        required=False,
        field_name="quantity",
        lookup_expr="lte",
    )
    order_contract = django_filters.ModelMultipleChoiceFilter(
        field_name="order_contract__id",
        queryset=Contract.objects.all(),
        to_field_name="id",
        label="Order Contract (ID)",
    )
    warranty_start = django_filters.DateFilter(
        field_name="warranty_start", lookup_expr="contains"
    )
    warranty_start__gte = django_filters.DateFilter(
        field_name="warranty_start", lookup_expr="gte"
    )
    warranty_start__lte = django_filters.DateFilter(
        field_name="warranty_start", lookup_expr="lte"
    )
    warranty_end = django_filters.DateFilter(
        field_name="warranty_end", lookup_expr="contains"
    )
    warranty_end__gte = django_filters.DateFilter(
        field_name="warranty_end", lookup_expr="gte"
    )
    warranty_end__lte = django_filters.DateFilter(
        field_name="warranty_end", lookup_expr="lte"
    )

    class Meta:
        model = Asset
        fields = (
            "id",
            "serial",
            "serial_actual",
            "partnumber",
            "asset_number",
            "assignment_status",
            "lifecycle_status",
            "project",
            "vendor",
            "price",
            "order_contract",
            "warranty_start",
            "warranty_end",
            "inventory_item",
        )

    def search(self, queryset, name, value):
        serial = Q(serial__icontains=value)
        serial_actual = Q(serial_actual__icontains=value)
        project = Q(project__icontains=value)
        vendor = Q(vendor__icontains=value)
        order_contract = Q(order_contract__name__icontains=value)

        # Search in assigned objects
        device_type = ContentType.objects.get_for_model(Device)
        site_type = ContentType.objects.get_for_model(Site)
        location_type = ContentType.objects.get_for_model(Location)
        rack_type = ContentType.objects.get_for_model(Rack)

        device_search = Q(
            assigned_object_type=device_type,
            assigned_object_id__in=Device.objects.filter(
                name__icontains=value
            ).values_list("pk", flat=True),
        )
        site_search = Q(
            assigned_object_type=site_type,
            assigned_object_id__in=Site.objects.filter(
                name__icontains=value
            ).values_list("pk", flat=True),
        )
        location_search = Q(
            assigned_object_type=location_type,
            assigned_object_id__in=Location.objects.filter(
                name__icontains=value
            ).values_list("pk", flat=True),
        )
        rack_search = Q(
            assigned_object_type=rack_type,
            assigned_object_id__in=Rack.objects.filter(
                name__icontains=value
            ).values_list("pk", flat=True),
        )

        return queryset.filter(
            serial
            | serial_actual
            | project
            | vendor
            | order_contract
            | device_search
            | site_search
            | location_search
            | rack_search
        )

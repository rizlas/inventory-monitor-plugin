import django_filters
from django.db.models import Q
from netbox.filtersets import NetBoxModelFilterSet

from inventory_monitor.models import ABRA, Asset


class ABRAFilterSet(NetBoxModelFilterSet):
    """
    Filterset for ABRA objects providing comprehensive search and filtering capabilities.
    """

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )
    abra_id = django_filters.CharFilter()
    inventory_number = django_filters.CharFilter()
    name = django_filters.CharFilter()
    serial_number = django_filters.CharFilter()
    person_id = django_filters.CharFilter()
    person_name = django_filters.CharFilter()
    location_code = django_filters.CharFilter()
    location = django_filters.CharFilter()
    activity_code = django_filters.CharFilter()
    user_name = django_filters.CharFilter()
    user_note = django_filters.CharFilter()
    split_asset = django_filters.CharFilter()
    status = django_filters.CharFilter()
    asset_id = django_filters.ModelMultipleChoiceFilter(
        field_name="assets",
        queryset=Asset.objects.all(),
        to_field_name="id",
        label="Asset (ID)",
    )

    class Meta:
        model = ABRA
        fields = [
            "id",
            "abra_id",
            "inventory_number",
            "name",
            "serial_number",
            "person_id",
            "person_name",
            "location_code",
            "location",
            "activity_code",
            "user_name",
            "split_asset",
            "status",
            "asset_id",
        ]

    def search(self, queryset, name, value):
        """Allow searching by various fields using a single search parameter."""
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(inventory_number__icontains=value)
            | Q(name__icontains=value)
            | Q(serial_number__icontains=value)
            | Q(abra_id__icontains=value)
            | Q(person_id__icontains=value)
            | Q(person_name__icontains=value)
            | Q(location_code__icontains=value)
            | Q(location__icontains=value)
            | Q(activity_code__icontains=value)
            | Q(user_name__icontains=value)
            | Q(user_note__icontains=value)
        )

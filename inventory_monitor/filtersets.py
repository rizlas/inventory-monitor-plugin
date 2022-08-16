from netbox.filtersets import NetBoxModelFilterSet
from .models import Probe
from django.db.models import Q
import django_filters

class ProbeFilterSet(NetBoxModelFilterSet):
    serial = django_filters.CharFilter(lookup_expr="icontains")
    time__gte = django_filters.DateTimeFilter(
        field_name='time',
        lookup_expr='gte'
    )
    time__lte = django_filters.DateTimeFilter(
        field_name='time',
        lookup_expr='lte'
    )
    latest_only = django_filters.BooleanFilter(
        method='_latest_only', label='Only latest inventory')

    class Meta:
        model = Probe
        fields = ('id', 'device_name', 'part', 'name', 'serial', 'device')

    def search(self, queryset, name, value):
        device_name = Q(device_name__icontains=value)
        part = Q(part__icontains=value)
        name = Q(name__icontains=value)
        serial = Q(serial__icontains=value)
        return queryset.filter(device_name | part | name | serial)

    def _latest_only(self, queryset, name, value):
        if value == True:
            return queryset.order_by("serial", '-time').distinct("serial")
        else:
            return queryset

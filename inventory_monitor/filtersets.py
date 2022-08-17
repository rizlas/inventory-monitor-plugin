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
        fields = ('id', 'dev_name', 'part', 'name',
                  'serial', 'device', 'description')

    def search(self, queryset, name, value):
        dev_name = Q(dev_name__icontains=value)
        part = Q(part__icontains=value)
        name = Q(name__icontains=value)
        serial = Q(serial__icontains=value)
        description = Q(description__icontains=value)
        return queryset.filter(dev_name | part | name | serial | description)

    def _latest_only(self, queryset, name, value):
        if value == True:
            latest_inventory_pks = Probe.objects.all().distinct(
                'serial').order_by('serial', '-time').values('pk')
            return queryset.filter(pk__in=latest_inventory_pks)

        else:
            return queryset

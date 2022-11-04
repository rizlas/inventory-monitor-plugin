import django_filters
from extras.filters import TagFilter
from django.db.models import Q
from .models import ContractTypeChoices, Contractor, Probe, Contract, InvMonFileAttachment
from dcim.models import Device
from netbox.filtersets import NetBoxModelFilterSet, BaseFilterSet
from utilities.filters import ContentTypeFilter


# Probe


class ProbeFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    tag = TagFilter()

    serial = django_filters.CharFilter(lookup_expr="icontains")
    time__gte = django_filters.DateTimeFilter(
        field_name='time',
        lookup_expr='gte'
    )
    time__lte = django_filters.DateTimeFilter(
        field_name='time',
        lookup_expr='lte'
    )
    latest_only_per_device = django_filters.BooleanFilter(
        method='_latest_only_per_device', label='Latest inventory (per device)')

    latest_only = django_filters.BooleanFilter(
        method='_latest_only', label='Latest inventory')

    device_id = django_filters.ModelMultipleChoiceFilter(
        field_name='device__id',
        queryset=Device.objects.all(),
        to_field_name='id',
        label='Device (ID)',
    )
    device = django_filters.ModelMultipleChoiceFilter(
        field_name='device__name',
        queryset=Device.objects.all(),
        to_field_name='name',
        label='Device (name)',
    )

    class Meta:
        model = Probe
        fields = ('id', 'device_descriptor', 'site_descriptor', 'location_descriptor', 'part', 'name',
                  'serial', 'device', 'site', 'location', 'description', 'category')

    def search(self, queryset, name, value):
        device_descriptor = Q(device_descriptor__icontains=value)
        site_descriptor = Q(site_descriptor__icontains=value)
        location_descriptor = Q(location_descriptor__icontains=value)
        part = Q(part__icontains=value)
        name = Q(name__icontains=value)
        serial = Q(serial__icontains=value)
        description = Q(description__icontains=value)
        return queryset.filter(device_descriptor | part | name | serial | description | site_descriptor | location_descriptor)

    def _latest_only_per_device(self, queryset, name, value):
        if value == True:
            latest_inventory_pks = Probe.objects.all().order_by(
                'serial', 'device_id', '-time').distinct('serial', 'device_id').values('pk')
            #latest_inventory_pks = Probe.objects.all().distinct('serial').order_by('serial', '-time').values('pk')
            return queryset.filter(pk__in=latest_inventory_pks)

        else:
            return queryset

    def _latest_only(self, queryset, name, value):
        if value == True:
            latest_inventory_pks = Probe.objects.all().distinct(
                'serial').order_by('serial', '-time').values('pk')
            return queryset.filter(pk__in=latest_inventory_pks)
        else:
            return queryset


# Contractor


class ContractorFilterSet(NetBoxModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    tag = TagFilter()

    name = django_filters.CharFilter(lookup_expr="icontains")
    company = django_filters.CharFilter(lookup_expr="icontains")
    address = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Contractor
        fields = ('id', 'name', 'company', 'address')

    def search(self, queryset, name, value):
        name = Q(name__icontains=value)
        company = Q(company__icontains=value)
        address = Q(address__icontains=value)
        return queryset.filter(name | company | address)


# Contract


class ContractFilterSet(NetBoxModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    tag = TagFilter()
    name = django_filters.CharFilter(lookup_expr="icontains")
    name_internal = django_filters.CharFilter(lookup_expr="icontains")
    contractor_id = django_filters.ModelMultipleChoiceFilter(
        field_name='contractor__id',
        queryset=Contractor.objects.all(),
        to_field_name='id',
        label='Contractor (ID)',
    )
    contractor = django_filters.ModelMultipleChoiceFilter(
        field_name='contractor__name',
        queryset=Contractor.objects.all(),
        to_field_name='name',
        label='Contractor (name)',
    )
    # TODO: forms.MultipleChoiceField
    type = django_filters.MultipleChoiceFilter(
        choices=ContractTypeChoices,
        required=False
    )
    # TODO: forms.DecimalField
    price = django_filters.NumberFilter(
        required=False
    )
    signed__gte = django_filters.DateFilter(
        field_name='signed',
        lookup_expr='gte'
    )
    signed__lte = django_filters.DateFilter(
        field_name='signed',
        lookup_expr='lte'
    )
    signed = django_filters.DateFilter(
        field_name='signed',
        lookup_expr='contains'
    )
    accepted__gte = django_filters.DateFilter(
        field_name='accepted',
        lookup_expr='gte'
    )
    accepted__lte = django_filters.DateFilter(
        field_name='accepted',
        lookup_expr='lte'
    )
    accepted = django_filters.DateFilter(
        field_name='accepted',
        lookup_expr='contains'
    )
    invoicing_start__gte = django_filters.DateFilter(
        field_name='invoicing_start',
        lookup_expr='gte'
    )
    invoicing_start__lte = django_filters.DateFilter(
        field_name='invoicing_start',
        lookup_expr='lte'
    )
    invoicing_start = django_filters.DateFilter(
        field_name='invoicing_start',
        lookup_expr='contains'
    )
    invoicing_end__gte = django_filters.DateFilter(
        field_name='invoicing_end',
        lookup_expr='gte'
    )
    invoicing_end__lte = django_filters.DateFilter(
        field_name='invoicing_end',
        lookup_expr='lte'
    )
    invoicing_end = django_filters.DateFilter(
        field_name='invoicing_end',
        lookup_expr='contains'
    )
    parent_id = django_filters.ModelMultipleChoiceFilter(
        field_name='parent__id',
        queryset=Contract.objects.all(),
        to_field_name='id',
        label='Contract (ID)',
    )
    parent = django_filters.ModelMultipleChoiceFilter(
        field_name='parent__name',
        queryset=Contract.objects.all(),
        to_field_name='name',
        label='Contract (name)',
    )
    master_contracts = django_filters.BooleanFilter(
        method='_master_contracts', label='Master contracts only')

    class Meta:
        model = Contract
        fields = ('id', 'name', 'name_internal', 'contractor', 'type', 'price',
                  'signed', 'accepted', 'invoicing_start', 'invoicing_end')

    def search(self, queryset, name, value):
        name = Q(name__icontains=value)
        name_internal = Q(name_internal__icontains=value)
        return queryset.filter(name | name_internal)

    def _master_contracts(self, queryset, name, value):
        if value == True:
            return queryset.filter(parent=None)
        else:
            return queryset


class InvMonFileAttachmentFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    created = django_filters.DateTimeFilter()
    content_type = ContentTypeFilter()

    class Meta:
        model = InvMonFileAttachment
        fields = ['id', 'content_type_id', 'object_id', 'name']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(name__icontains=value)

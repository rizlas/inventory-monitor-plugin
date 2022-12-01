from dcim.api.serializers import (NestedDeviceSerializer,
                                  NestedLocationSerializer,
                                  NestedSiteSerializer)
from netbox.api.serializers import (NetBoxModelSerializer,
                                    WritableNestedSerializer)
from rest_framework import serializers

from ..models import Contract, Contractor, Invoice, Probe

# Probe


class ProbeSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:inventory_monitor-api:probe-detail'
    )
    device = NestedDeviceSerializer()
    site = NestedSiteSerializer(allow_null=True)
    location = NestedLocationSerializer(allow_null=True)

    class Meta:
        model = Probe
        fields = [
            'id',
            'url',
            'display',
            'name',
            'time',
            'serial',
            'part',
            'device_descriptor',
            'device',
            'site_descriptor',
            'site',
            'location_descriptor',
            'location',
            'description',
            'category',
            'discovered_data',
            'tags',
            'comments',
            'custom_fields',
        ]


class NestedProbeSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:inventory_monitor-api:probe-detail'
    )

    class Meta:
        model = Probe
        fields = ['id', 'url', 'display', 'name', 'serial', 'time']


# Contractor


class ContractorSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:inventory_monitor-api:contractor-detail'
    )

    class Meta:
        model = Contractor
        fields = [
            'id',
            'url',
            'display',
            'name',
            'company',
            'address',
            'tags',
            'comments',
            'custom_fields',
        ]


class NestedContractorSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:inventory_monitor-api:contractor-detail'
    )

    class Meta:
        model = Contractor
        fields = ['id', 'display', 'url', 'name', 'company', 'address']


# Contract

class NestedContractSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:inventory_monitor-api:contract-detail'
    )

    contractor = NestedContractorSerializer()

    class Meta:
        model = Contract
        fields = ['id', 'url', 'display', 'name', 'name_internal', 'contractor', 'type',
                  'price', 'signed', 'accepted', 'invoicing_start', 'invoicing_end', 'parent']


class ContractSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:inventory_monitor-api:contract-detail'
    )
    contractor = NestedContractorSerializer()
    parent = NestedContractSerializer(allow_null=True)

    class Meta:
        model = Contract
        fields = [
            'id',
            'url',
            'display',
            'name',
            'name_internal',
            'contractor',
            'type',
            'contract_type',
            'price',
            'signed',
            'accepted',
            'invoicing_start',
            'invoicing_end',
            'parent',
            'tags',
            'comments',
            'custom_fields',
        ]


class InvoiceSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:inventory_monitor-api:invoice-detail'
    )
    contract = NestedContractSerializer()

    class Meta:
        model = Invoice
        fields = [
            'id',
            'url',
            'display',
            'name',
            'name_internal',
            'project',
            'contract',
            'price',
            'invoicing_start',
            'invoicing_end',
            'tags',
            'comments',
            'custom_fields',
        ]


class NestedInvoiceSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:inventory_monitor-api:invoice-detail'
    )

    class Meta:
        model = Invoice
        fields = ['id', 'url', 'display', 'name', 'name_internal']

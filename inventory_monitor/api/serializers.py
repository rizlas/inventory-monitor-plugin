from dcim.api.serializers import (NestedDeviceSerializer,
                                  NestedLocationSerializer,
                                  NestedSiteSerializer)
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from netbox.api.fields import ContentTypeField
from netbox.api.serializers import (NetBoxModelSerializer,
                                    WritableNestedSerializer)
from rest_framework import serializers

from ..models import Contract, Contractor, InvMonFileAttachment, Probe
from drf_yasg.utils import swagger_serializer_method
from utilities.api import get_serializer_for_model
from netbox.constants import NESTED_SERIALIZER_PREFIX

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
    parent = NestedContractSerializer()

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


# File attachments


class InvMonFileAttachmentSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:inventory_monitor-api:invmonfileattachment-detail')
    content_type = ContentTypeField(
        queryset=ContentType.objects.all()
    )
    parent = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = InvMonFileAttachment
        fields = [
            'id', 'url', 'display', 'content_type', 'object_id', 'parent', 'name', 'file', 'created', 'last_updated',
        ]

    def validate(self, data):
        # Validate that the parent object exists
        try:
            data['content_type'].get_object_for_this_type(id=data['object_id'])
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                "Invalid parent object: {} ID {}".format(
                    data['content_type'], data['object_id'])
            )

        # Enforce model validation
        super().validate(data)

        return data

    @swagger_serializer_method(serializer_or_field=serializers.JSONField)
    def get_parent(self, obj):
        serializer = get_serializer_for_model(
            obj.parent, prefix=NESTED_SERIALIZER_PREFIX)
        return serializer(obj.parent, context={'request': self.context['request']}).data


class NestedInvMonFileAttachmentSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:inventory_monitor-api:invmonfileattachment-detail')
    content_type = ContentTypeField(
        queryset=ContentType.objects.all()
    )
    parent = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = InvMonFileAttachment
        fields = [
            'id', 'url', 'display', 'content_type', 'object_id', 'parent', 'name', 'file', 'created', 'last_updated',
        ]

    def validate(self, data):
        # Validate that the parent object exists
        try:
            data['content_type'].get_object_for_this_type(id=data['object_id'])
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                "Invalid parent object: {} ID {}".format(
                    data['content_type'], data['object_id'])
            )

        # Enforce model validation
        super().validate(data)

        return data

    @swagger_serializer_method(serializer_or_field=serializers.JSONField)
    def get_parent(self, obj):
        serializer = get_serializer_for_model(
            obj.parent, prefix=NESTED_SERIALIZER_PREFIX)
        return serializer(obj.parent, context={'request': self.context['request']}).data

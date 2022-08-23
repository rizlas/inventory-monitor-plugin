from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer
from ..models import Probe
from dcim.api.serializers import NestedDeviceSerializer


class ProbeSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:inventory_monitor-api:probe-detail'
    )
    device = NestedDeviceSerializer()

    class Meta:
        model = Probe
        fields = (
            'id',
            'url',
            'display',
            'name',
            'time',
            'comments',
            'tags',
            'custom_fields',
            'device_descriptor',
            'device',
            'serial',
            'part',
            'description',
            'category',
            'discovered_data',
        )

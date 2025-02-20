from dcim.api.serializers import DeviceSerializer, LocationSerializer, SiteSerializer
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers
from tenancy.api.serializers import TenantSerializer

from inventory_monitor.models import (
    RMA,
    Asset,
    AssetType,
    ComponentService,
    Contract,
    Contractor,
    Invoice,
    Probe,
)


class ProbeSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:inventory_monitor-api:probe-detail"
    )
    device = DeviceSerializer(allow_null=True, nested=True)
    site = SiteSerializer(allow_null=True, nested=True)
    location = LocationSerializer(allow_null=True, nested=True)

    class Meta:
        model = Probe
        fields = [
            "id",
            "url",
            "display",
            "name",
            "time",
            "serial",
            "part",
            "device_descriptor",
            "device",
            "site_descriptor",
            "site",
            "location_descriptor",
            "location",
            "description",
            "category",
            "discovered_data",
            "tags",
            "comments",
            "custom_fields",
            "creation_time",
        ]

        brief_fields = [
            "id",
            "url",
            "display",
            "name",
            "serial",
            "time",
            "creation_time",
        ]


class ContractorSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:inventory_monitor-api:contractor-detail"
    )
    tenant = TenantSerializer(nested=True)

    class Meta:
        model = Contractor
        fields = [
            "id",
            "url",
            "display",
            "name",
            "company",
            "address",
            "tenant",
            "tags",
            "comments",
            "custom_fields",
        ]

        brief_fields = ["id", "url", "display", "name", "company", "address"]


class ContractSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:inventory_monitor-api:contract-detail"
    )
    contractor = ContractorSerializer(nested=True)

    class Meta:
        model = Contract
        fields = [
            "id",
            "url",
            "display",
            "name",
            "name_internal",
            "contractor",
            "type",
            "contract_type",
            "price",
            "signed",
            "accepted",
            "invoicing_start",
            "invoicing_end",
            "parent",
            "tags",
            "comments",
            "custom_fields",
        ]
        brief_fields = [
            "id",
            "url",
            "display",
            "name",
            "name_internal",
        ]

    def get_fields(self):
        fields = super(ContractSerializer, self).get_fields()
        fields["parent"] = ContractSerializer(nested=True)
        return fields


class InvoiceSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:inventory_monitor-api:invoice-detail"
    )
    contract = ContractSerializer(nested=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "url",
            "display",
            "name",
            "name_internal",
            "project",
            "contract",
            "price",
            "invoicing_start",
            "invoicing_end",
            "tags",
            "comments",
            "custom_fields",
        ]

        brief_fields = ["id", "url", "display", "name", "name_internal"]


class AssetTypeSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:inventory_monitor-api:assettype-detail"
    )

    class Meta:
        model = AssetType
        fields = [
            "id",
            "url",
            "name",
            "slug",
            "description",
            "color",  # Add color field
            "display",
            "custom_fields",
            "created",
            "last_updated",
            "tags",  # Add tags field
        ]

        brief_fields = [
            "id",
            "url",
            "name",
            "slug",
            "color",
            "display",
        ]


class AssetSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:inventory_monitor-api:asset-detail"
    )
    order_contract = ContractSerializer(nested=True)
    type = AssetTypeSerializer(nested=True)

    class Meta:
        model = Asset
        fields = (
            "id",
            "url",
            "display",
            "serial",
            "serial_actual",
            "partnumber",
            "device",
            "asset_number",
            "project",
            "assignment_status",
            "lifecycle_status",
            "location",
            "site",
            "vendor",
            "quantity",
            "price",
            "order_contract",
            "inventory_item",
            "warranty_start",
            "warranty_end",
            "type",
            "comments",
            "tags",
            "created",
            "last_updated",
        )
        brief_fields = (
            "id",
            "url",
            "display",
            "serial",
            "type",
            "assignment_status",
            "lifecycle_status",
        )


class ComponentServiceSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:inventory_monitor-api:componentservice-detail"
    )
    contract = ContractSerializer(nested=True)
    asset = AssetSerializer(nested=True)

    class Meta:
        model = ComponentService
        fields = [
            "id",
            "url",
            "display",
            "service_start",
            "service_end",
            "service_param",
            "service_price",
            "service_category",
            "service_category_vendor",
            "asset",
            "contract",
            "tags",
            "comments",
            "custom_fields",
        ]

        brief_fields = [
            "id",
            "url",
            "display",
            "service_start",
            "service_end",
            "service_price",
            "asset",
            "contract",
        ]


class RMASerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:inventory_monitor-api:rma-detail"
    )
    asset = AssetSerializer(nested=True)

    class Meta:
        model = RMA
        fields = [
            "id",
            "url",
            "display",
            "rma_number",
            "asset",
            "original_serial",
            "replacement_serial",
            "status",
            "date_issued",
            "date_shipped",
            "tracking_number",
            "issue_description",
            "vendor_response",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        ]

        brief_fields = [
            "id",
            "url",
            "display",
            "rma_number",
            "asset",
            "status",
            "date_issued",
            "date_shipped",
        ]

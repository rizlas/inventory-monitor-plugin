from dcim.models import Device, InventoryItem, Location, Module, Rack, Site
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from utilities.forms.fields import (
    CommentField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet, TabbedGroups
from utilities.forms.widgets.datetime import DatePicker

from inventory_monitor.models import Asset, AssetType, Contract
from inventory_monitor.models.asset import (
    ASSIGNED_OBJECT_MODELS,
    AssignmentStatusChoices,
    LifecycleStatusChoices,
)


class AssetForm(NetBoxModelForm):
    fieldsets = (
        FieldSet(
            "serial",
            "serial_actual",
            "partnumber",
            "asset_number",
            "type",
            "project",
            "price",
            "vendor",
            "quantity",
            name=_("Asset"),
        ),
        FieldSet("assignment_status", name=_("Assignment Status")),
        FieldSet("lifecycle_status", name=_("Lifecycle Status")),
        FieldSet(
            TabbedGroups(
                FieldSet("site", name=_("Site")),
                FieldSet("location", name=_("Location")),
                FieldSet("rack", name=_("Rack")),
                FieldSet("device", name=_("Device")),
                FieldSet("module", name=_("Module")),
            ),
            name=_("Component Assignment"),
        ),
        FieldSet("inventory_item", name=_("Inventory Item")),
        FieldSet(
            "order_contract",
            name=_("Order Contract"),
        ),
        FieldSet("warranty_start", "warranty_end", name=_("Dates")),
        FieldSet("tags", name=_("Misc")),
    )
    comments = CommentField(label="Comments")
    serial = forms.CharField(
        required=True,
        label="Serial",
        widget=forms.TextInput(attrs={"placeholder": "Serial"}),
    )
    serial_actual = forms.CharField(
        required=True,
        label="Serial Actual",
        widget=forms.TextInput(attrs={"placeholder": "Serial Actual"}),
    )
    partnumber = forms.CharField(
        required=False,
        label="Part Number",
    )
    type = DynamicModelChoiceField(
        queryset=AssetType.objects.all(), required=False, label="Type"
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label="Site",
        selector=True,
    )
    location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        label="Location",
        selector=True,
    )
    rack = DynamicModelChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        label="Rack",
        selector=True,
    )
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label="Device",
        selector=True,
    )
    module = DynamicModelChoiceField(
        queryset=Module.objects.all(),
        required=False,
        label="Module",
        selector=True,
    )

    inventory_item = DynamicModelChoiceField(
        queryset=InventoryItem.objects.all(),
        required=False,
        label="Inventory Item",
        selector=True,
    )
    asset_number = forms.CharField(
        required=False,
        label="Inventory / Asset Number",
    )
    project = forms.CharField(
        required=False,
        label="Project",
    )
    vendor = forms.CharField(
        required=False,
        label="Vendor",
    )
    quantity = forms.IntegerField(required=True, label="Items", initial=1, min_value=1)
    price = forms.DecimalField(
        required=True,
        label="Price",
        initial=0,
        min_value=0,
        decimal_places=2,
    )
    order_contract = DynamicModelChoiceField(
        queryset=Contract.objects.all(),
        required=False,
        label="Order Contract",
    )
    warranty_start = forms.DateField(
        required=False, label=("Warranty Start"), widget=DatePicker()
    )
    warranty_end = forms.DateField(
        required=False,
        label=("Warranty End"),
        widget=DatePicker(),
    )

    class Meta:
        model = Asset
        fields = (
            "serial",
            "serial_actual",
            "partnumber",
            "type",
            "asset_number",
            "lifecycle_status",
            "assignment_status",
            "site",
            "location",
            "rack",
            "device",
            "module",
            "inventory_item",
            "project",
            "vendor",
            "quantity",
            "price",
            "order_contract",
            "warranty_start",
            "warranty_end",
            "comments",
            "tags",
        )

    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance")
        initial = kwargs.get("initial", {}).copy()
        assigned_object_type = initial.get("assigned_object_type")
        assigned_object_id = initial.get("assigned_object_id")

        if instance:
            # When editing set the initial value for assigned_object selection
            for assigned_object_model in ContentType.objects.filter(
                ASSIGNED_OBJECT_MODELS
            ):
                if (
                    type(instance.assigned_object)
                    is assigned_object_model.model_class()
                ):
                    initial[assigned_object_model.model] = instance.assigned_object
                    break
        elif assigned_object_type and assigned_object_id:
            # When adding the InventoryItem from a assigned_object page
            if (
                content_type := ContentType.objects.filter(ASSIGNED_OBJECT_MODELS)
                .filter(pk=assigned_object_type)
                .first()
            ):
                if (
                    assigned_object := content_type.model_class()
                    .objects.filter(pk=assigned_object_id)
                    .first()
                ):
                    initial[content_type.model] = assigned_object

        kwargs["initial"] = initial

        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()

        # Handle object assignment
        selected_objects = [
            field
            for field in (
                "site",
                "location",
                "rack",
                "device",
                "module",
            )
            if self.cleaned_data[field]
        ]
        if len(selected_objects) > 1:
            raise forms.ValidationError(
                _("An InventoryItem can only be assigned to a single assigned_object.")
            )
        elif selected_objects:
            self.instance.assigned_object = self.cleaned_data[selected_objects[0]]
        else:
            self.instance.assigned_object = None


class AssetFilterForm(NetBoxModelFilterSetForm):
    model = Asset

    fieldsets = (
        FieldSet("q", "filter_id", "tag", name=_("Misc")),
        FieldSet("assignment_status", name=_("Assignment Status")),
        FieldSet("lifecycle_status", name=_("Lifecycle Status")),
        FieldSet(
            "order_contract",
            # "site",
            # "location",
            # "device",
            "inventory_item",
            name=_("Linked"),
        ),
        FieldSet(
            "warranty_start",
            "warranty_start__gte",
            "warranty_start__lte",
            "warranty_end",
            "warranty_end__gte",
            "warranty_end__lte",
            name=_("Dates"),
        ),
        FieldSet(
            "serial",
            "serial_actual",
            "partnumber",
            "asset_number",
            "type_id",
            "project",
            "vendor",
            name=_("Asset"),
        ),
        FieldSet("quantity", "quantity__gte", "quantity__lte", name=_("Items")),
        FieldSet("price", "price__gte", "price__lte", name=_("Price")),
    )

    serial = forms.CharField(required=False)
    tag = TagFilterField(model)
    serial_actual = forms.CharField(required=False)
    partnumber = forms.CharField(required=False)
    assignment_status = forms.ChoiceField(
        choices=AssignmentStatusChoices, required=False
    )
    lifecycle_status = forms.ChoiceField(choices=LifecycleStatusChoices, required=False)
    type_id = DynamicModelMultipleChoiceField(
        queryset=AssetType.objects.all(), required=False, label=_("Type")
    )
    # device = DynamicModelMultipleChoiceField(
    #    queryset=Device.objects.all(), required=False, label=_("Device")
    # )
    inventory_item = DynamicModelMultipleChoiceField(
        queryset=InventoryItem.objects.all(), required=False, label=_("Inventory Item")
    )
    # site = DynamicModelMultipleChoiceField(
    #    queryset=Site.objects.all(), required=False, label=_("Site")
    # )
    # location = DynamicModelMultipleChoiceField(
    #    queryset=Location.objects.all(), required=False, label=_("Location")
    # )
    quantity = forms.IntegerField(required=False, label="Items")
    quantity__gte = forms.IntegerField(required=False, label=("Items: From"))
    quantity__lte = forms.IntegerField(required=False, label=("Items: Till"))
    asset_number = forms.CharField(
        required=False,
        label="Asset Number",
    )
    project = forms.CharField(
        required=False,
        label="Project",
    )
    vendor = forms.CharField(
        required=False,
        label="Vendor",
    )
    price = forms.DecimalField(required=False)
    price__gte = forms.DecimalField(
        required=False,
        label=("Price: From"),
    )
    price__lte = forms.DecimalField(
        required=False,
        label=("Price: Till"),
    )
    order_contract = DynamicModelMultipleChoiceField(
        queryset=Contract.objects.all(), required=False, label=_("Order Contract")
    )
    warranty_start = forms.DateField(
        required=False, label=("Warranty Start"), widget=DatePicker()
    )
    warranty_start__gte = forms.DateField(
        required=False, label=("Warranty Start: From"), widget=DatePicker()
    )
    warranty_start__lte = forms.DateField(
        required=False, label=("Warranty Start: Till"), widget=DatePicker()
    )
    warranty_end = forms.DateField(
        required=False, label=("Warranty End"), widget=DatePicker()
    )
    warranty_end__gte = forms.DateField(
        required=False, label=("Warranty End: From"), widget=DatePicker()
    )
    warranty_end__lte = forms.DateField(
        required=False, label=("Warranty End: Till"), widget=DatePicker()
    )

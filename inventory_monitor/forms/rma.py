from django import forms
from django.utils.translation import gettext as _
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from utilities.forms.fields import CommentField, DynamicModelChoiceField, TagFilterField
from utilities.forms.rendering import FieldSet
from utilities.forms.widgets.datetime import DatePicker

from inventory_monitor.models import RMA, Asset


class RMAForm(NetBoxModelForm):
    fieldsets = (
        FieldSet(
            "rma_number",
            "asset",
            "status",
            "original_serial",
            "replacement_serial",
            "tracking_number",
            name="RMA Information",
        ),
        FieldSet("date_issued", "date_shipped", name="Dates"),
        FieldSet("issue_description", "vendor_response", name="Description"),
        FieldSet("tags", name="Tags"),
    )

    asset = DynamicModelChoiceField(queryset=Asset.objects.all())
    comments = CommentField()

    class Meta:
        model = RMA
        fields = (
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
            "comments",
        )
        widgets = {
            "date_issued": DatePicker(),
            "date_shipped": DatePicker(),
            "issue_description": forms.Textarea(attrs={"rows": 3}),
            "vendor_response": forms.Textarea(attrs={"rows": 3}),
        }


class RMAFilterForm(NetBoxModelFilterSetForm):
    model = RMA
    fieldsets = (
        FieldSet(
            "q",
            "filter_id",
            "tag",
        ),
        FieldSet(
            "rma_number",
            "asset_id",
            "status",
            "date_issued",
            "date_shipped",
            "tracking_number",
            name="RMA",
        ),
    )

    rma_number = forms.CharField(required=False)
    asset_id = DynamicModelChoiceField(queryset=Asset.objects.all(), required=False)
    tag = TagFilterField(model)
    date_issued = forms.DateField(required=False, widget=DatePicker())
    date_shipped = forms.DateField(required=False, widget=DatePicker())

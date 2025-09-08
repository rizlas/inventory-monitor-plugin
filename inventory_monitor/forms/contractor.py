from django import forms
from django.utils.translation import gettext as _
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm, NetBoxModelBulkEditForm
from tenancy.models import Tenant
from utilities.forms.fields import (
    CommentField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet

from inventory_monitor.models import Contractor


class ContractorForm(NetBoxModelForm):
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=True)

    comments = CommentField(label="Comments")

    class Meta:
        model = Contractor
        fields = ("name", "company", "address", "tenant", "tags", "comments")


class ContractorFilterForm(NetBoxModelFilterSetForm):
    model = Contractor
    tag = TagFilterField(model)
    name = forms.CharField(required=False)
    company = forms.CharField(required=False)
    address = forms.CharField(required=False)
    tenant_id = DynamicModelMultipleChoiceField(queryset=Tenant.objects.all(), required=False, label="Tenant")

    fieldsets = (
        FieldSet("q", "filter_id", "tag", name=_("Misc")),
        FieldSet("name", "company", "address", name=_("Common")),
        FieldSet("tenant_id", name=_("Linked")),
    )


class ContractorBulkEditForm(NetBoxModelBulkEditForm):
    name = forms.CharField(max_length=100, required=False)
    company = forms.CharField(max_length=100, required=False)
    address = forms.CharField(max_length=200, required=False)
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)

    model = Contractor
    nullable_fields = ("name", "company", "address", "tenant")

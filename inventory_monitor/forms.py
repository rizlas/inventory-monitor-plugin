from dcim.models import Device, Location, Site
from django import forms
from django.utils.translation import gettext as _
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from utilities.forms import (BOOLEAN_WITH_BLANK_CHOICES, DatePicker,
                             DateTimePicker, DynamicModelMultipleChoiceField,
                             StaticSelect)
from utilities.forms.fields import CommentField, DynamicModelChoiceField

from .models import Contract, Contractor, ContractTypeChoices, Probe, InvMonFileAttachment


# Probe


class ProbeForm(NetBoxModelForm):
    comments = CommentField(
        label="Comments"
    )

    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False
    )
    location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        required=False
    )

    class Meta:
        model = Probe
        fields = ('name', 'serial', 'time',  'category', 'part', 'device_descriptor', 'device',
                  'site_descriptor', 'site', 'location_descriptor', 'location', 'description', 'tags', 'comments',)


class ProbeFilterForm(NetBoxModelFilterSetForm):
    model = Probe

    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label=_('Device')
    )
    serial = forms.CharField(
        required=False
    )
    device_descriptor = forms.CharField(
        required=False
    )
    category = forms.CharField(
        required=False
    )
    description = forms.CharField(
        required=False
    )
    time__gte = forms.DateTimeField(
        required=False,
        label=('Time From'),
        widget=DateTimePicker()
    )
    time__lte = forms.DateTimeField(
        required=False,
        label=('Time Till'),
        widget=DateTimePicker()
    )
    latest_only_per_device = forms.NullBooleanField(
        required=False,
        label='Latest inventory only (per device)',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    latest_only = forms.NullBooleanField(
        required=False,
        label='Latest inventory only',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )


# Contractor


class ContractorForm(NetBoxModelForm):
    comments = CommentField(
        label="Comments"
    )

    class Meta:
        model = Contractor
        fields = ('name', 'company', 'address', 'tags', 'comments', 'tags')


class ContractorFilterForm(NetBoxModelFilterSetForm):
    model = Contractor

    name = forms.CharField(
        required=False
    )
    company = forms.CharField(
        required=False
    )
    address = forms.CharField(
        required=False
    )


# Contract


class ContractForm(NetBoxModelForm):
    comments = CommentField(
        label="Comments"
    )

    contractor = DynamicModelChoiceField(
        queryset=Contractor.objects.all(),
        required=True
    )

    parent = DynamicModelChoiceField(
        queryset=Contract.objects.all(),
        query_params={"parent_id": "null"},
        required=False,
        label=("Parent Contract")
    )

    signed = forms.DateField(
        required=False,
        label=('Signed'),
        widget=DatePicker()
    )

    accepted = forms.DateField(
        required=False,
        label=('Accepted'),
        widget=DatePicker()
    )

    invoicing_start = forms.DateField(
        required=False,
        label=('Invoicing Start'),
        widget=DatePicker()
    )

    invoicing_end = forms.DateField(
        required=False,
        label=('Invoicing End'),
        widget=DatePicker()
    )

    class Meta:
        model = Contract
        fields = ('name', 'name_internal', 'contractor', 'type', 'price', 'signed',
                  'accepted', 'invoicing_start',  'invoicing_end', 'parent', 'comments', 'tags')


class ContractFilterForm(NetBoxModelFilterSetForm):
    model = Contract

    name = forms.CharField(
        required=False
    )

    name_internal = forms.CharField(
        required=False
    )
    master_contracts = forms.NullBooleanField(
        required=False,
        label='Master contracts only',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    contractor_id = DynamicModelMultipleChoiceField(
        queryset=Contractor.objects.all(),
        required=False,
        label=_('Contractor')
    )

    parent_id = DynamicModelMultipleChoiceField(
        queryset=Contract.objects.all(),
        query_params={"parent_id": "null"},
        required=False,
        label=_('Parent Contract')
    )

    type = forms.MultipleChoiceField(
        choices=ContractTypeChoices,
        required=False
    )

    price = forms.DecimalField(
        required=False
    )

    accepted__gte = forms.DateField(
        required=False,
        label=('Accepted From'),
        widget=DatePicker()
    )
    accepted__lte = forms.DateField(
        required=False,
        label=('Accepted Till'),
        widget=DatePicker()
    )
    accepted = forms.DateField(
        required=False,
        label=('Accepted'),
        widget=DatePicker()
    )

    signed__gte = forms.DateField(
        required=False,
        label=('Signed From'),
        widget=DatePicker()
    )
    signed__lte = forms.DateField(
        required=False,
        label=('Signed Till'),
        widget=DatePicker()
    )
    signed = forms.DateField(
        required=False,
        label=('Signed'),
        widget=DatePicker()
    )

    invoicing_start__gte = forms.DateField(
        required=False,
        label=('Invoicing Start: From'),
        widget=DatePicker()
    )
    invoicing_start__lte = forms.DateField(
        required=False,
        label=('Invoicing Start: Till'),
        widget=DatePicker()
    )
    invoicing_start = forms.DateField(
        required=False,
        label=('Invoicing Start'),
        widget=DatePicker()
    )

    invoicing_end__gte = forms.DateField(
        required=False,
        label=('Invoicing End: From'),
        widget=DatePicker()
    )
    invoicing_end__lte = forms.DateField(
        required=False,
        label=('Invoicing End: Till'),
        widget=DatePicker()
    )
    invoicing_end = forms.DateField(
        required=False,
        label=('Invoicing End'),
        widget=DatePicker()
    )


class InvMonFileAttachmentForm(NetBoxModelForm):

    class Meta:
        model = InvMonFileAttachment
        fields = [
            'name', 'file',
        ]

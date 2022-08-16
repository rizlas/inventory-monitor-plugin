from dcim.models import Device
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms.fields import CommentField, DynamicModelChoiceField
from .models import Probe
from django import forms
from utilities.forms import DynamicModelMultipleChoiceField, DateTimePicker
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES, StaticSelect


class ProbeForm(NetBoxModelForm):
    comments = CommentField()
    device = DynamicModelChoiceField(
        queryset=Device.objects.all()
    )

    class Meta:
        model = Probe
        fields = ('name', 'serial', 'time', 'device_name',
                  'device', 'comments', 'tags')


class ProbeFilterForm(NetBoxModelFilterSetForm):
    model = Probe

    device = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
    )

    serial = forms.CharField(
        required=False
    )
    device_name = forms.CharField(
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

    latest_only = forms.NullBooleanField(
        required=False,
        label='Only latest inventory',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )

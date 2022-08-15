from dcim.models import Device
from netbox.forms import NetBoxModelForm
from utilities.forms.fields import CommentField, DynamicModelChoiceField
from .models import Probe


class ProbeForm(NetBoxModelForm):
    comments = CommentField()
    device = DynamicModelChoiceField(
        queryset=Device.objects.all()
    )

    class Meta:
        model = Probe
        fields = ('name', 'serial', 'time', 'device_name', 'device', 'comments', 'tags')



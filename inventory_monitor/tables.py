from os import link
import django_tables2 as tables

from netbox.tables import NetBoxTable, ChoiceFieldColumn
from .models import Probe


class ProbeTable(NetBoxTable):
    name = tables.Column(linkify=True)

    class Meta(NetBoxTable.Meta):
        model = Probe
        fields = ('pk', 'id', 'time', 'name', 'device_name',
                  'part', 'serial', 'device', 'comment', 'actions')
        default_columns = ('id', 'time', 'name', 'serial')

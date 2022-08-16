import django_tables2 as tables

from netbox.tables import NetBoxTable
from .models import Probe


class ProbeTable(NetBoxTable):
    name = tables.Column(linkify=True)

    class Meta(NetBoxTable.Meta):
        model = Probe
        fields = ('pk', 'id', 'time', 'name', 'dev_name',
                  'part', 'serial', 'device', 'comments', 'actions')
        default_columns = ('id', 'time', 'name', 'serial')

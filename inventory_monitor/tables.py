import django_tables2 as tables

from netbox.tables import NetBoxTable
from .models import Probe


class ProbeTable(NetBoxTable):
    name = tables.Column(linkify=True)
    device = tables.Column(linkify=True)
    changes_count = tables.Column()
    discovered_data = tables.JSONColumn()

    class Meta(NetBoxTable.Meta):
        model = Probe
        fields = ('pk', 'id', 'time', 'name', 'dev_name', 'description',
                  'part', 'serial', 'device', 'comments', 'changes_count', 'actions', 'item_class')
        default_columns = ('id', 'time', 'name', 'serial',
                           'part', 'dev_name', 'device', 'changes_count')

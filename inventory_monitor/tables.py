import django_tables2 as tables
from netbox.tables import ChoiceFieldColumn, NetBoxTable

from .models import Contract, Contractor, Invoice, Probe

# Probe


class ProbeTable(NetBoxTable):
    name = tables.Column(linkify=True)
    device = tables.Column(linkify=True)
    site = tables.Column(linkify=True)
    location = tables.Column(linkify=True)
    changes_count = tables.Column()
    discovered_data = tables.JSONColumn()

    class Meta(NetBoxTable.Meta):
        model = Probe
        fields = ('pk', 'id', 'time', 'name', 'device_descriptor', 'site_descriptor', 'location_descriptor', 'description',
                  'part', 'serial', 'device', 'site', 'location', 'comments', 'changes_count', 'actions', 'category')
        default_columns = ('id', 'time', 'name', 'serial', 'part', 'device_descriptor', 'device',
                           'site_descriptor', 'site', 'location_descriptor', 'locations', 'changes_count')


# Contractor


class ContractorTable(NetBoxTable):
    name = tables.Column(linkify=True)
    contracts_count = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = Contractor
        fields = ('pk', 'id', 'name', 'company', 'address',
                  'comments', 'contracts_count', 'actions')
        default_columns = ('id', 'name', 'company', 'contracts_count')


# Contract


class ContractTable(NetBoxTable):
    name = tables.Column(linkify=True)
    contractor = tables.Column(linkify=True)
    subcontracts_count = tables.Column()
    invoices_count = tables.Column()
    contract_type = tables.Column(orderable=False)
    attachments_count = tables.Column()
    parent = tables.Column(linkify=True)
    type = ChoiceFieldColumn()

    class Meta(NetBoxTable.Meta):
        model = Contract
        fields = ('pk', 'id', 'name', 'name_internal', 'contractor', 'type', 'contract_type', 'price', 'signed',
                  'accepted', 'invoicing_start',  'invoicing_end', 'parent', 'comments', 'invoices_count', 'subcontracts_count', 'attachments_count', 'actions')
        default_columns = ('id', 'name', 'name_internal', 'contractor', 'type', 'contract_type', 'price',
                           'signed', 'accepted', 'invoicing_start',  'invoicing_end', 'parent', 'attachments_count')


# Invoice


class InvoiceTable(NetBoxTable):
    name = tables.Column(linkify=True)
    contract = tables.Column(linkify=True)
    attachments_count = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = Invoice
        fields = ('pk', 'id', 'name', 'name_internal', 'project', 'contract', 'price',
                  'invoicing_start',  'invoicing_end', 'comments', 'attachments_count', 'actions')
        default_columns = ('id', 'name', 'name_internal', 'contract',
                           'price', 'invoicing_start',  'invoicing_end', 'attachments_count')

from dcim.models import InventoryItem
from dcim.tables.devices import InventoryItemTable
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, OuterRef, Subquery
from django.shortcuts import get_object_or_404
from netbox.views import generic

from . import filtersets, forms, models, tables

# Probe


class ProbeView(generic.ObjectView):
    queryset = models.Probe.objects.all()

    def get_extra_context(self, request, instance):
        probes_sub_count_serial = models.Probe.objects.filter(serial=OuterRef(
            'serial')).values('serial').annotate(changes_count=Count('*'))
        probe_table = tables.ProbeTable(models.Probe.objects.filter(serial=instance.serial).annotate(
            changes_count=Subquery(probes_sub_count_serial.values("changes_count"))))
        probe_table.configure(request)

        inventory_items = InventoryItem.objects.filter(
            custom_field_data__inventory_monitor_probe=instance.id)
        inventory_items_table = InventoryItemTable(inventory_items)
        inventory_items_table.configure(request)

        return {'probe_table': probe_table, 'inventory_items_table': inventory_items_table}


class ProbeListView(generic.ObjectListView):
    sub_count_serial = models.Probe.objects.filter(serial=OuterRef(
        'serial')).values('serial').annotate(changes_count=Count('*'))
    queryset = models.Probe.objects.prefetch_related('tags', 'device').annotate(
        changes_count=Subquery(sub_count_serial.values("changes_count")))

    table = tables.ProbeTable
    filterset = filtersets.ProbeFilterSet
    filterset_form = forms.ProbeFilterForm


class ProbeEditView(generic.ObjectEditView):
    queryset = models.Probe.objects.all()
    form = forms.ProbeForm


class ProbeDeleteView(generic.ObjectDeleteView):
    queryset = models.Probe.objects.all()


class ProbeBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Probe.objects.all()
    filterset = filtersets.ProbeFilterSet
    table = tables.ProbeTable


# Contractor


class ContractorView(generic.ObjectView):
    queryset = models.Contractor.objects.all()

    def get_extra_context(self, request, instance):
        contracts = models.Contract.objects.filter(contractor=instance)
        contracts_table = tables.ContractTable(contracts)
        contracts_table.configure(request)

        return {'contracts_table': contracts_table}


class ContractorListView(generic.ObjectListView):
    queryset = models.Contractor.objects.prefetch_related(
        'tags').annotate(contracts_count=Count('contracts'))

    filterset = filtersets.ContractorFilterSet
    filterset_form = forms.ContractorFilterForm
    table = tables.ContractorTable


class ContractorEditView(generic.ObjectEditView):
    queryset = models.Contractor.objects.all()
    form = forms.ContractorForm


class ContractorDeleteView(generic.ObjectDeleteView):
    queryset = models.Contractor.objects.all()


# Contract


class ContractView(generic.ObjectView):
    queryset = models.Contract.objects.all()

    def get_extra_context(self, request, instance):
        subcontracts = models.Contract.objects.filter(parent=instance)
        subcontracts_table = tables.ContractTable(subcontracts)
        subcontracts_table.configure(request)

        return {'subcontracts_table': subcontracts_table}


class ContractListView(generic.ObjectListView):
    queryset = models.Contract.objects.all().annotate(
        subcontracts_count=Count('subcontracts'))
    filterset = filtersets.ContractFilterSet
    filterset_form = forms.ContractFilterForm
    table = tables.ContractTable


class ContractEditView(generic.ObjectEditView):
    queryset = models.Contract.objects.all().annotate(
        subcontracts_count=Count('subcontracts'))
    form = forms.ContractForm


class ContractDeleteView(generic.ObjectDeleteView):
    queryset = models.Contract.objects.all()


# File attachments


class InvMonFileAttachmentEditView(generic.ObjectEditView):
    queryset = models.InvMonFileAttachment.objects.all()
    form = forms.InvMonFileAttachmentForm
    template_name = 'inventory_monitor/invmon_file_attachment_edit.html'

    def alter_object(self, instance, request, args, kwargs):
        if not instance.pk:
            # Assign the parent object based on URL kwargs
            content_type = get_object_or_404(
                ContentType, pk=request.GET.get('content_type'))
            instance.parent = get_object_or_404(
                content_type.model_class(), pk=request.GET.get('object_id'))
        return instance

    def get_return_url(self, request, obj=None):
        return obj.parent.get_absolute_url() if obj else super().get_return_url(request)

    def get_extra_addanother_params(self, request):
        return {
            'content_type': request.GET.get('content_type'),
            'object_id': request.GET.get('object_id'),
        }


class InvMonFileAttachmentDeleteView(generic.ObjectDeleteView):
    queryset = models.InvMonFileAttachment.objects.all()

    def get_return_url(self, request, obj=None):
        return obj.parent.get_absolute_url() if obj else super().get_return_url(request)

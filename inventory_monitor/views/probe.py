from django.db.models import Count, OuterRef, Subquery
from netbox.views import generic

from inventory_monitor import filtersets, forms, models, tables


class ProbeView(generic.ObjectView):
    queryset = models.Probe.objects.all()


class ProbeListView(generic.ObjectListView):
    sub_count_serial = (
        models.Probe.objects.filter(serial=OuterRef("serial"))
        .values("serial")
        .annotate(changes_count=Count("*"))
    )
    queryset = models.Probe.objects.prefetch_related("tags", "device").annotate(
        changes_count=Subquery(sub_count_serial.values("changes_count"))
    )

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

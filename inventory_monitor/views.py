from netbox.views import generic
from . import forms, models, tables


class ProbeView(generic.ObjectView):
    queryset = models.Probe.objects.all()

    def get_extra_context(self, request, instance):
        table = tables.ProbeTable(
            models.Probe.objects.filter(serial=instance.serial))
        table.configure(request)

        return {
            'probe_table': table,
        }


class ProbeListView(generic.ObjectListView):
    queryset = models.Probe.objects.all()
    table = tables.ProbeTable


class ProbeEditView(generic.ObjectEditView):
    queryset = models.Probe.objects.all()
    form = forms.ProbeForm


class ProbeDeleteView(generic.ObjectDeleteView):
    queryset = models.Probe.objects.all()

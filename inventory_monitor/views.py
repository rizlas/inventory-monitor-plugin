from netbox.views import generic
from . import forms, models, tables

class ProbeView(generic.ObjectView):
    queryset = models.Probe.objects.all()


class ProbeListView(generic.ObjectListView):
    queryset = models.Probe.objects.all()
    table = tables.ProbeTable


class ProbeEditView(generic.ObjectEditView):
    queryset = models.Probe.objects.all()
    form = forms.ProbeForm


class ProbeDeleteView(generic.ObjectDeleteView):
    queryset = models.Probe.objects.all()

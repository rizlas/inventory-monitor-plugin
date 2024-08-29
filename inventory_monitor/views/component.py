from django.contrib.postgres.aggregates.general import ArrayAgg
from django.db.models import Count
from netbox.views import generic

from inventory_monitor import filtersets, forms, models, tables


class ComponentView(generic.ObjectView):
    queryset = models.Component.objects.all()


class ComponentListView(generic.ObjectListView):
    queryset = (
        models.Component.objects.all()
        .prefetch_related("services")
        .prefetch_related("tags")
        .annotate(services_count=Count("services"))
        .annotate(services_to=ArrayAgg("services__service_end"))
        .annotate(services_contracts=ArrayAgg("services__contract__name"))
    )
    filterset = filtersets.ComponentFilterSet
    filterset_form = forms.ComponentFilterForm
    table = tables.ComponentTable


class ComponentEditView(generic.ObjectEditView):
    queryset = models.Component.objects.all()
    form = forms.ComponentForm


class ComponentDeleteView(generic.ObjectDeleteView):
    queryset = models.Component.objects.all()

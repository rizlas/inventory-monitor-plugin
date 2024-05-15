from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, OuterRef, Subquery
from netbox.views import generic

from inventory_monitor import filtersets, forms, models, tables
from inventory_monitor.helpers import get_content_type_or_none

try:
    from netbox_attachments.models import NetBoxAttachment

    attachments_model_exists = True
except ModuleNotFoundError:
    attachments_model_exists = False


class ContractorView(generic.ObjectView):
    queryset = models.Contractor.objects.all()

    def get_extra_context(self, request, instance):
        if attachments_model_exists:
            try:
                contract_content_type = get_content_type_or_none(
                    app_label="inventory_monitor", model="contract"
                )
                subquery_attachments_count = (
                    NetBoxAttachment.objects.filter(
                        object_id=OuterRef("id"), content_type=contract_content_type
                    )
                    .values("object_id")
                    .annotate(attachments_count=Count("*"))
                )
                contracts = (
                    models.Contract.objects.filter(contractor=instance)
                    .annotate(subcontracts_count=Count("subcontracts", distinct=True))
                    .annotate(invoices_count=Count("invoices", distinct=True))
                    .annotate(
                        attachments_count=Subquery(
                            subquery_attachments_count.values(
                                "attachments_count")
                        )
                    )
                )
            except (ContentType.DoesNotExist, ValueError) as e:
                contracts = models.Contract.objects.filter(contractor=instance)
        else:
            contracts = models.Contract.objects.filter(contractor=instance)

        contracts_table = tables.ContractTable(contracts)
        contracts_table.configure(request)

        return {"contracts_table": contracts_table}


class ContractorListView(generic.ObjectListView):
    queryset = models.Contractor.objects.prefetch_related("tags").annotate(
        contracts_count=Count("contracts")
    )

    filterset = filtersets.ContractorFilterSet
    filterset_form = forms.ContractorFilterForm
    table = tables.ContractorTable


class ContractorEditView(generic.ObjectEditView):
    queryset = models.Contractor.objects.all()
    form = forms.ContractorForm


class ContractorDeleteView(generic.ObjectDeleteView):
    queryset = models.Contractor.objects.all()

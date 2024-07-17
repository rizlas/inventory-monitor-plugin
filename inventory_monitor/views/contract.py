from core.models import ObjectType
from django.db.models import Count, OuterRef, Subquery, Value
from netbox.views import generic

from inventory_monitor import filtersets, forms, models, tables
from inventory_monitor.helpers import get_object_type_or_none

try:
    from netbox_attachments.models import NetBoxAttachment

    attachments_model_exists = True
except ModuleNotFoundError:
    attachments_model_exists = False


class ContractView(generic.ObjectView):
    if attachments_model_exists:
        try:
            contract_object_type = get_object_type_or_none(
                app_label="inventory_monitor", model="contract"
            )
            subquery_attachments_count = (
                NetBoxAttachment.objects.filter(
                    object_id=OuterRef("id"), object_type=contract_object_type
                )
                .values("object_id")
                .annotate(attachments_count=Count("*"))
            )
            queryset = (
                models.Contract.objects.all()
                .annotate(subcontracts_count=Count("subcontracts", distinct=True))
                .annotate(invoices_count=Count("invoices", distinct=True))
                .annotate(
                    attachments_count=Subquery(
                        subquery_attachments_count.values("attachments_count")
                    )
                )
            )
        except (ObjectType.DoesNotExist, ValueError) as e:
            models.Contract.objects.all().annotate(
                subcontracts_count=Count("subcontracts", distinct=True)
            ).annotate(invoices_count=Count("invoices", distinct=True)).annotate(
                attachments_count=Value(0)
            )
    else:
        queryset = (
            models.Contract.objects.all()
            .annotate(subcontracts_count=Count("subcontracts", distinct=True))
            .annotate(invoices_count=Count("invoices", distinct=True))
            .annotate(attachments_count=Value(0))
        )

    def get_extra_context(self, request, instance):
        if attachments_model_exists:
            try:
                contract_object_type = get_object_type_or_none(
                    app_label="inventory_monitor", model="contract"
                )
                subquery_contract_attachments_count = (
                    NetBoxAttachment.objects.filter(
                        object_id=OuterRef("id"), object_type=contract_object_type
                    )
                    .values("object_id")
                    .annotate(attachments_count=Count("*"))
                )

                subcontracts = (
                    models.Contract.objects.filter(parent=instance)
                    .annotate(subcontracts_count=Count("subcontracts", distinct=True))
                    .annotate(invoices_count=Count("invoices", distinct=True))
                    .annotate(
                        attachments_count=Subquery(
                            subquery_contract_attachments_count.values(
                                "attachments_count"
                            )
                        )
                    )
                )

                invoice_object_type = get_object_type_or_none(
                    app_label="inventory_monitor", model="invoice"
                )

                subquery_attachments_count = (
                    NetBoxAttachment.objects.filter(
                        object_id=OuterRef("id"), object_type=invoice_object_type
                    )
                    .values("object_id")
                    .annotate(attachments_count=Count("*"))
                )

                invoices = instance.invoices.all().annotate(
                    attachments_count=Subquery(
                        subquery_attachments_count.values("attachments_count")
                    )
                )
            except (ObjectType.DoesNotExist, ValueError) as e:
                subcontracts = (
                    models.Contract.objects.filter(parent=instance)
                    .annotate(subcontracts_count=Count("subcontracts", distinct=True))
                    .annotate(invoices_count=Count("invoices", distinct=True))
                    .annotate(attachments_count=Value(0))
                )

                invoices = instance.invoices.all().annotate(attachments_count=Value(0))
        else:
            subcontracts = (
                models.Contract.objects.filter(parent=instance)
                .annotate(subcontracts_count=Count("subcontracts", distinct=True))
                .annotate(invoices_count=Count("invoices", distinct=True))
                .annotate(attachments_count=Value(0))
            )

            invoices = instance.invoices.all().annotate(attachments_count=Value(0))

        subcontracts_table = tables.ContractTable(subcontracts)
        subcontracts_table.configure(request)
        invoices_table = tables.InvoiceTable(invoices)
        invoices_table.configure(request)

        return {
            "subcontracts_table": subcontracts_table,
            "invoices_table": invoices_table,
        }


class ContractListView(generic.ObjectListView):
    if attachments_model_exists:
        try:
            contract_object_type = get_object_type_or_none(
                app_label="inventory_monitor", model="contract"
            )
            subquery_attachments_count = (
                NetBoxAttachment.objects.filter(
                    object_id=OuterRef("id"), object_type=contract_object_type
                )
                .values("object_id")
                .annotate(attachments_count=Count("*"))
            )
            queryset = (
                models.Contract.objects.all()
                .annotate(subcontracts_count=Count("subcontracts", distinct=True))
                .annotate(invoices_count=Count("invoices", distinct=True))
                .annotate(
                    attachments_count=Subquery(
                        subquery_attachments_count.values("attachments_count")
                    )
                )
            )
        except (ObjectType.DoesNotExist, ValueError) as e:
            queryset = (
                models.Contract.objects.all()
                .annotate(subcontracts_count=Count("subcontracts", distinct=True))
                .annotate(invoices_count=Count("invoices", distinct=True))
                .annotate(attachments_count=Value(0))
            )
    else:
        queryset = (
            models.Contract.objects.all()
            .annotate(subcontracts_count=Count("subcontracts", distinct=True))
            .annotate(invoices_count=Count("invoices", distinct=True))
            .annotate(attachments_count=Value(0))
        )

    filterset = filtersets.ContractFilterSet
    filterset_form = forms.ContractFilterForm
    table = tables.ContractTable


class ContractEditView(generic.ObjectEditView):
    queryset = models.Contract.objects.all().annotate(
        subcontracts_count=Count("subcontracts")
    )
    form = forms.ContractForm


class ContractDeleteView(generic.ObjectDeleteView):
    queryset = models.Contract.objects.all()

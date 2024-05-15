from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, OuterRef, Subquery, Value
from netbox.views import generic

from inventory_monitor import filtersets, forms, models, tables
from inventory_monitor.helpers import get_content_type_or_none

try:
    from netbox_attachments.models import NetBoxAttachment

    attachments_model_exists = True
except ModuleNotFoundError:
    attachments_model_exists = False


class InvoiceView(generic.ObjectView):
    queryset = models.Invoice.objects.all()


class InvoiceListView(generic.ObjectListView):
    if attachments_model_exists:
        try:
            invoice_content_type = get_content_type_or_none(
                app_label="inventory_monitor", model="invoice"
            )
            subquery_attachments_count = (
                NetBoxAttachment.objects.filter(
                    object_id=OuterRef("id"), content_type=invoice_content_type
                )
                .values("object_id")
                .annotate(attachments_count=Count("*"))
            )
            queryset = models.Invoice.objects.all().annotate(
                attachments_count=Subquery(
                    subquery_attachments_count.values("attachments_count")
                )
            )
        except (ContentType.DoesNotExist, ValueError) as e:
            queryset = models.Invoice.objects.all().annotate(attachments_count=Value(0))
    else:
        queryset = models.Invoice.objects.all().annotate(attachments_count=Value(0))

    filterset = filtersets.InvoiceFilterSet
    filterset_form = forms.InvoiceFilterForm
    table = tables.InvoiceTable


class InvoiceEditView(generic.ObjectEditView):
    queryset = models.Invoice.objects.all()
    form = forms.InvoiceForm


class InvoiceDeleteView(generic.ObjectDeleteView):
    queryset = models.Invoice.objects.all()

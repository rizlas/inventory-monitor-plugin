from dcim.models import InventoryItem
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, OuterRef, Subquery, Value
from extras.plugins import PluginTemplateExtension

from .models import Probe

try:
    from netbox_attachments.models import NetBoxAttachment
    attachments_model_exists = True
except ModuleNotFoundError:
    attachments_model_exists = False


#from django.conf import settings
#plugin_settings = settings.PLUGINS_CONFIG.get('inventory_monitor', {})


class DeviceProbeList(PluginTemplateExtension):
    model = 'dcim.device'

    def right_page(self):
        obj = self.context['object']

        # Latest inventory overall
        # latest_inventory_pks = Probe.objects.all()\
        #    .distinct('serial')\
        #    .order_by('serial', '-time')\
        #    .values('pk')

        # Latest inventory per device
        latest_inventory_pks = Probe.objects.all().order_by(
            'serial', 'device_id', '-time').distinct('serial', 'device_id').values('pk')

        sub_count_serial = Probe.objects.filter(serial=OuterRef('serial'))\
            .values('serial')\
            .annotate(changes_count=Count('*'))

        device_probes = Probe.objects.filter(device=obj, pk__in=latest_inventory_pks)\
            .prefetch_related('tags', 'device')\
            .annotate(changes_count=Subquery(sub_count_serial.values("changes_count")))

        return self.render(
            'inventory_monitor/device_probes_include.html',
            extra_context={
                'device_probes': device_probes.order_by('-time')[:10],
                'total_device_probes_count': device_probes.count(),
            }
        )


class InventoryItemDuplicates(PluginTemplateExtension):
    model = 'dcim.inventoryitem'

    def right_page(self):
        obj = self.context['object']

        inv_duplicates = InventoryItem.objects.filter(serial=obj.serial)\
            .exclude(id=obj.id).order_by('-custom_field_data__inventory_monitor_last_probe')

        return self.render(
            'inventory_monitor/inventory_item_duplicates_include.html',
            extra_context={
                'current_inv': obj,
                'inv_duplicates': inv_duplicates,
                'inv_duplicates_count': inv_duplicates.count(),
            }
        )


class InvoicesList(PluginTemplateExtension):
    model = 'inventory_monitor.contract'

    def full_width_page(self):
        object = self.context['object']

        if attachments_model_exists:
            invoice_content_type = ContentType.objects.get(
                app_label='inventory_monitor', model='invoice')

            subquery_attachments_count = NetBoxAttachment.objects.filter(object_id=OuterRef(
                'id'), content_type=invoice_content_type).values('object_id').annotate(attachments_count=Count('*'))

            invoices = object.invoices.all().annotate(attachments_count=Subquery(
                subquery_attachments_count.values("attachments_count")))
        else:
            invoices = object.invoices.all().annotate(attachments_count=Value(0))

        return self.render(
            'inventory_monitor/invoices_include.html',
            extra_context={
                'object': object,
                'invoices': invoices,
            }
        )


template_extensions = [DeviceProbeList, InventoryItemDuplicates, InvoicesList]

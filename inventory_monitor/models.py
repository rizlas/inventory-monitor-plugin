from django.contrib.contenttypes.fields import (GenericForeignKey,
                                                GenericRelation)
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel
from netbox.models.features import (CustomFieldsMixin, CustomLinksMixin,
                                    CustomValidationMixin,
                                    ExportTemplatesMixin, JournalingMixin,
                                    TagsMixin, WebhooksMixin)
from utilities.choices import ChoiceSet
from utilities.querysets import RestrictedQuerySet

from .utils import invmon_file_upload


class ContractTypeChoices(ChoiceSet):
    key = 'Contract.type'

    CHOICES = [
        ('supply', 'Supply Contract', 'green'),
        ('order', 'Order', 'red'),
        ('service', 'Service Contract', 'orange'),
        ('other', 'Other', 'blue')
    ]


class Probe(CustomFieldsMixin, CustomLinksMixin, CustomValidationMixin, ExportTemplatesMixin, JournalingMixin, TagsMixin, WebhooksMixin, models.Model):
    objects = RestrictedQuerySet.as_manager()

    time = models.DateTimeField()

    device_descriptor = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    site_descriptor = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    location_descriptor = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    part = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    name = models.CharField(
        max_length=255
    )

    serial = models.CharField(
        max_length=255
    )

    device = models.ForeignKey(
        to='dcim.Device',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    site = models.ForeignKey(
        to='dcim.Site',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    location = models.ForeignKey(
        to='dcim.Location',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    description = models.TextField(
        blank=True
    )

    comments = models.TextField(
        blank=True
    )

    discovered_data = models.JSONField(
        default=dict,
        blank=True
    )
    category = models.CharField(
        blank=True,
        null=True,
        max_length=255
    )

    class Meta:
        ordering = ('name', 'serial', 'time', 'part', 'description', 'device_descriptor', 'device',
                    'site_descriptor', 'site', 'location_descriptor', 'location', 'category', 'discovered_data',)

    def __str__(self):
        return f'{self.serial} - {self.name}'

    def get_absolute_url(self):
        return reverse('plugins:inventory_monitor:probe', args=[self.pk])


class Contractor(NetBoxModel):
    objects = RestrictedQuerySet.as_manager()

    name = models.CharField(
        max_length=255,
        blank=False,
        null=False
    )

    company = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    address = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    comments = models.TextField(
        blank=True
    )

    files = GenericRelation(
        to='inventory_monitor.InvMonFileAttachment',
    )

    class Meta:
        ordering = ('name', 'company', 'address', 'comments',)

    def __str__(self):
        if self.company:
            return f'{self.name}: {self.company}'
        else:
            return f'{self.name}'

    def get_absolute_url(self):
        return reverse('plugins:inventory_monitor:contractor', args=[self.pk])


class Contract(NetBoxModel):
    objects = RestrictedQuerySet.as_manager()

    name = models.CharField(
        max_length=255,
        blank=False,
        null=False
    )

    name_internal = models.CharField(
        max_length=255,
        blank=False,
        null=False
    )

    contractor = models.ForeignKey(
        to='inventory_monitor.contractor',  # Contractor,
        on_delete=models.PROTECT,
        related_name="contracts",
        blank=True,
        null=True,
    )

    type = models.CharField(
        max_length=50,
        choices=ContractTypeChoices
    )

    price = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )

    signed = models.DateField(
        blank=True,
        null=True,
    )

    accepted = models.DateField(
        blank=True,
        null=True,
    )

    invoicing_start = models.DateField(
        blank=True,
        null=True,
    )

    invoicing_end = models.DateField(
        blank=True,
        null=True,
    )

    parent = models.ForeignKey(
        to='self',
        on_delete=models.CASCADE,
        related_name='subcontracts',
        null=True,
        blank=True,
        verbose_name='Parent contract'
    )

    comments = models.TextField(
        blank=True
    )

    files = GenericRelation(
        to='inventory_monitor.InvMonFileAttachment',
    )

    @property
    def contract_type(self):
        if self.parent:
            return "subcontract"
        else:
            return "contract"

    class Meta:
        ordering = ('name', 'name_internal', 'contractor', 'type', 'price',
                    'signed', 'accepted', 'invoicing_start', 'invoicing_end')

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} - {self.name}"
        else:
            return f"{self.name}"

    def get_type_color(self):
        return ContractTypeChoices.colors.get(self.type)

    def get_absolute_url(self):
        return reverse('plugins:inventory_monitor:contract', args=[self.pk])

    def clean(self):
        super().clean()

        # Validate - subcontract cannot set parent which is subcontract
        if self.parent and self.parent.parent:
            raise ValidationError(
                {'parent': "Parent cannot be a subcontract"}
            )

        # Validate - if parent contract has different contractor
        if self.parent and self.parent.contractor != self.contractor:
            raise ValidationError(
                {'contractor': f"Contractor must be same as Parent contractor: {self.parent.contractor}"}
            )

        # Validate invoicing_start and invoicing_end
        if self.invoicing_start and self.invoicing_end and self.invoicing_start > self.invoicing_end:
            raise ValidationError(
                {'invoicing_start': f"Invoicing Start cannot be set after Invoicing End"}
            )


class InvMonFileAttachment(NetBoxModel):
    """
    An uploaded file which is associated with an object.
    """
    content_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.PositiveBigIntegerField()
    parent = GenericForeignKey(
        ct_field='content_type',
        fk_field='object_id'
    )
    file = models.FileField(
        upload_to=invmon_file_upload,
    )
    name = models.CharField(
        max_length=50,
        blank=True
    )

    objects = RestrictedQuerySet.as_manager()

    clone_fields = ('content_type', 'object_id')

    class Meta:
        ordering = ('name', 'pk')  # name may be non-unique

    def __str__(self):
        if self.name:
            return self.name
        filename = self.file.name.rsplit('/', 1)[-1]
        return filename.split('_', 2)[2]

    def delete(self, *args, **kwargs):

        _name = self.file.name

        super().delete(*args, **kwargs)

        # Delete file from disk
        self.file.delete(save=False)

        # Deleting the file erases its name. We restore the image's filename here in case we still need to reference it
        # before the request finishes. (For example, to display a message indicating the ImageAttachment was deleted.)
        self.file.name = _name

    @property
    def size(self):
        """
        Wrapper around `file.size` to suppress an OSError in case the file is inaccessible. Also opportunistically
        catch other exceptions that we know other storage back-ends to throw.
        """
        expected_exceptions = [OSError]

        try:
            from botocore.exceptions import ClientError
            expected_exceptions.append(ClientError)
        except ImportError:
            pass

        try:
            return self.file.size
        except tuple(expected_exceptions):
            return None

    def to_objectchange(self, action):
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.parent
        return objectchange

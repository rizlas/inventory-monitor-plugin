from django.db import models
from netbox.models import NetBoxModel
from django.urls import reverse


class Probe(NetBoxModel):
    time = models.DateTimeField()

    dev_name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    # TODO: site name? - history value
    # TODO: location name? - history value
    # TODO: Site - relation
    # TODO: Location - relation

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

    description = models.TextField(
        blank=True
    )

    comments = models.TextField(
        blank=True
    )

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return f'{self.serial} - {self.name}'

    def get_absolute_url(self):
        return reverse('plugins:inventory_monitor:probe', args=[self.pk])

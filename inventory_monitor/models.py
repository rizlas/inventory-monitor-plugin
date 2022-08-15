from django.contrib.postgres.fields import ArrayField
from django.db import models
from netbox.models import NetBoxModel

class Probe(NetBoxModel):
    time = models.DateTimeField(
        
    )

    device_name = models.CharField(
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

    comment = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    device = models.ForeignKey(
        to='dcim.Device',
        on_delete=models.PROTECT,
        related_name='+',
        blank=True,
        null=True
    )


    class Meta:
        ordering = ('name',)

    def __str__(self):
        return f'{self.serial} - {self.name}'

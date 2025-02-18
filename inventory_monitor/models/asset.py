from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from netbox.models import NetBoxModel
from utilities.choices import ChoiceSet
from utilities.querysets import RestrictedQuerySet

from inventory_monitor.models.probe import Probe


class AssignmentStatusChoices(ChoiceSet):
    key = "inventory_monitor.asset.assignment_status"

    RESERVED = "reserved"
    DEPLOYED = "deployed"
    LOANED = "loaned"
    STOCKED = "stocked"

    CHOICES = [
        (RESERVED, "Reserved", "cyan"),
        (DEPLOYED, "Deployed", "green"),
        (LOANED, "Loaned", "blue"),
        (STOCKED, "Stocked", "gray"),
    ]


class LifecycleStatusChoices(ChoiceSet):
    key = "inventory_monitor.asset.lifecycle_status"

    NEW = "new"
    IN_STOCK = "in_stock"
    IN_USE = "in_use"
    IN_MAINTENANCE = "in_maintenance"
    RETIRED = "retired"
    DISPOSED = "disposed"

    CHOICES = [
        (NEW, "New", "green"),
        (IN_STOCK, "In Stock", "blue"),
        (IN_USE, "In Use", "cyan"),
        (IN_MAINTENANCE, "In Maintenance", "orange"),
        (RETIRED, "Retired", "red"),
        (DISPOSED, "Disposed", "gray"),
    ]


class Asset(NetBoxModel):
    objects = RestrictedQuerySet.as_manager()
    serial = models.CharField(max_length=255, blank=False, null=False)
    serial_actual = models.CharField(max_length=255, blank=False, null=False)
    partnumber = models.CharField(max_length=64, blank=True, null=True)
    device = models.ForeignKey(
        to="dcim.device",
        on_delete=models.PROTECT,
        related_name="assets",
        blank=True,
        null=True,
    )
    # TODO: Asset Number
    asset_number = models.CharField(max_length=255, blank=True, null=True)
    project = models.CharField(max_length=32, blank=True, null=True)
    site = models.ForeignKey(
        to="dcim.site",  # Locality,
        on_delete=models.PROTECT,
        related_name="assets",
        blank=True,
        null=True,
    )
    location = models.ForeignKey(
        to="dcim.location",
        on_delete=models.PROTECT,
        related_name="assets",
        blank=True,
        null=True,
    )
    inventory_item = models.ForeignKey(
        to="dcim.inventoryitem",
        on_delete=models.PROTECT,
        related_name="assets",
        blank=True,
        null=True,
    )
    vendor = models.CharField(max_length=32, blank=True, null=True)
    quantity = models.PositiveIntegerField(
        blank=False,
        null=False,
        default=1,
        validators=[MinValueValidator(0)],
    )
    price = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        default=0,
    )
    order_contract = models.ForeignKey(
        to="inventory_monitor.contract",  # Contractor,
        on_delete=models.PROTECT,
        related_name="assets",
        blank=True,
        null=True,
    )
    warranty_start = models.DateField(
        blank=True,
        null=True,
    )
    warranty_end = models.DateField(
        blank=True,
        null=True,
    )
    comments = models.TextField(blank=True)
    assignment_status = models.CharField(
        max_length=30,
        choices=AssignmentStatusChoices,
        default=AssignmentStatusChoices.STOCKED,
        blank=False,
        null=False,
    )
    lifecycle_status = models.CharField(
        max_length=30,
        choices=LifecycleStatusChoices,
        default=LifecycleStatusChoices.NEW,
        blank=False,
        null=False,
    )

    class Meta:
        db_table = "inventory_monitor_asset"
        ordering = (
            "serial",
            "serial_actual",
            "partnumber",
            "device",
            "asset_number",
            "project",
            "site",
            "location",
            "inventory_item",
            "vendor",
            "quantity",
            "price",
            "order_contract",
            "warranty_start",
            "warranty_end",
        )

    def get_related_probes(self):
        """
        Get all probe records related to this asset through various serial number matches:
        - serial_actual (current serial)
        - serial (original serial)
        - RMA serial numbers (from related RMAs)

        Returns:
        - QuerySet of Probe objects ordered by time descending
        """

        serials = {self.serial_actual, self.serial}
        rma_original_serials = set(self.rmas.values_list("original_serial", flat=True))
        rma_replacement_serials = set(
            self.rmas.values_list("replacement_serial", flat=True)
        )

        # add rma_original_serials and rma_replacement_serials to serials
        serials.update(rma_original_serials)
        serials.update(rma_replacement_serials)
        # get rid of None values
        serials = [s for s in serials if s]

        return Probe.objects.filter(serial__in=serials).order_by("-time")

    def __str__(self):
        return f"{self.serial}"

    def get_absolute_url(self):
        return reverse("plugins:inventory_monitor:asset", args=[self.pk])

    def clean(self):
        super().clean()

    def get_assignment_status_color(self):
        return AssignmentStatusChoices.colors.get(self.assignment_status, "gray")

    def get_lifecycle_status_color(self):
        return LifecycleStatusChoices.colors.get(self.lifecycle_status, "gray")

    def get_warranty_status(self):
        """Returns the warranty status and color for progress bar"""
        today = timezone.now().date()
        warning_days = 14

        def format_days_message(days, message_type=None):
            if message_type is None:
                message_type = "ago" if days < 0 else "in"
            days = abs(days)
            day_text = "day" if days == 1 else "days"
            return f"{message_type} {days} {day_text}"

        def get_expiration_status(days_until):
            if days_until <= 0:
                return {
                    "color": "danger",
                    "message": f"Expired {format_days_message(days_until)}",
                }
            if days_until <= warning_days:
                return {
                    "color": "warning",
                    "message": f"Expires {format_days_message(days_until)}",
                }
            return {
                "color": "success",
                "message": f"Valid until {self.warranty_end.strftime('%Y-%m-%d')}",
            }

        # No dates set
        if not self.warranty_start and not self.warranty_end:
            return None

        # Only end date set
        if not self.warranty_start and self.warranty_end:
            days_until = (self.warranty_end - today).days
            return get_expiration_status(days_until)

        # Future warranty
        if self.warranty_start and today < self.warranty_start:
            days_until = (self.warranty_start - today).days
            return {
                "color": "info",
                "message": f"Starts {format_days_message(days_until)}",
            }

        # Both dates set
        if self.warranty_start and self.warranty_end:
            total_duration = (self.warranty_end - self.warranty_start).days
            days_until_expiration = (self.warranty_end - today).days

            # Simple logic for very short durations (2 days or less)
            if total_duration <= 2:
                if days_until_expiration <= 0:
                    return {
                        "color": "danger",
                        "message": f"Expired {format_days_message(days_until_expiration)}",
                    }
                return {
                    "color": "warning",
                    "message": f"Expires {format_days_message(days_until_expiration)}",
                }

            # Normal duration segment
            return get_expiration_status(days_until_expiration)

        # Active without end date
        return {
            "color": "success",
            "message": "Active",
        }

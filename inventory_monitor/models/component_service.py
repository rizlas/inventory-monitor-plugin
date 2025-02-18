from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from netbox.models import NetBoxModel
from utilities.querysets import RestrictedQuerySet


class ComponentService(NetBoxModel):
    objects = RestrictedQuerySet.as_manager()
    service_start = models.DateField(
        blank=True,
        null=True,
    )
    service_end = models.DateField(
        blank=True,
        null=True,
    )
    service_param = models.CharField(max_length=32, blank=True, null=True)
    service_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        default=0,
    )
    service_category = models.CharField(max_length=255, blank=True, null=True)
    service_category_vendor = models.CharField(max_length=255, blank=True, null=True)
    asset = models.ForeignKey(
        to="inventory_monitor.asset",
        on_delete=models.PROTECT,
        related_name="services",
        blank=True,
        null=True,
    )
    contract = models.ForeignKey(
        to="inventory_monitor.contract",
        on_delete=models.PROTECT,
        related_name="services",
        blank=True,
        null=True,
    )
    comments = models.TextField(blank=True)

    class Meta:
        ordering = (
            "service_start",
            "service_end",
            "service_param",
            "service_price",
            "service_category",
            "service_category_vendor",
            "asset",
            "contract",
        )

    def __str__(self):
        return f"{self.pk}"

    def get_absolute_url(self):
        return reverse("plugins:inventory_monitor:componentservice", args=[self.pk])

    def clean(self):
        super().clean()

    def get_service_status(self):
        """Returns the service status and color for progress bar"""
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
                "message": f"Valid until {self.service_end.strftime('%Y-%m-%d')}",
            }

        # No dates set
        if not self.service_start and not self.service_end:
            return None

        # Only end date set
        if not self.service_start and self.service_end:
            days_until = (self.service_end - today).days
            return get_expiration_status(days_until)

        # Future service
        if self.service_start and today < self.service_start:
            days_until = (self.service_start - today).days
            return {
                "color": "info",
                "message": f"Starts {format_days_message(days_until)}",
            }

        # Both dates set
        if self.service_start and self.service_end:
            total_duration = (self.service_end - self.service_start).days
            days_until_expiration = (self.service_end - today).days

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

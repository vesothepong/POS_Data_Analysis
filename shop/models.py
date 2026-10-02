import datetime
import re

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone


ORDER_TYPE_CHOICES = [
    ("dine_in", "Dine In"),
    ("takeaway", "Takeaway"),
]

PAYMENT_METHOD_CHOICES = [
    ("cash", "Cash at Counter"),
    ("card", "Credit / Debit Card"),
    ("qr", "QR Scan / Mobile Pay"),
]


class Order(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    customer_name = models.CharField(max_length=100, default="Walk-in Guest", blank=True)
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES, default="dine_in")
    table_number = models.CharField(max_length=50, blank=True, default="")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default="cash")
    ticket_number = models.CharField(max_length=20, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        ordering = ["-created_at"]

    @classmethod
    def get_next_ticket_number(cls, for_datetime=None, exclude_pk=None):
        """Calculate the next sequential ticket number for the specified local day (e.g. W-001, W-002).
        Resets back to 1 at the start of each new day."""
        tz = timezone.get_current_timezone()
        if for_datetime is not None:
            if not timezone.is_aware(for_datetime):
                for_datetime = timezone.make_aware(for_datetime, tz)
            target_date = timezone.localtime(for_datetime).date()
        else:
            target_date = timezone.localdate()

        day_start = timezone.make_aware(datetime.datetime.combine(target_date, datetime.time.min), tz)
        day_end = timezone.make_aware(datetime.datetime.combine(target_date, datetime.time.max), tz)

        qs = cls.objects.filter(
            created_at__gte=day_start,
            created_at__lte=day_end,
        )
        if exclude_pk:
            qs = qs.exclude(pk=exclude_pk)

        if transaction.get_connection().in_atomic_block:
            try:
                qs = qs.select_for_update()
            except Exception:
                pass

        ticket_list = list(qs.values_list("ticket_number", flat=True))

        max_seq = 0
        for t in ticket_list:
            if t:
                m = re.search(r"(\d+)$", str(t))
                if m:
                    try:
                        num = int(m.group(1))
                        if num > max_seq:
                            max_seq = num
                    except ValueError:
                        pass

        seq = max(max_seq, len(ticket_list)) + 1
        return f"W-{seq:03d}"

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = self.get_next_ticket_number(
                for_datetime=self.created_at,
                exclude_pk=self.pk,
            )
            if kwargs.get("update_fields") is not None:
                update_fields = set(kwargs["update_fields"])
                update_fields.add("ticket_number")
                kwargs["update_fields"] = update_fields

        super().save(*args, **kwargs)

    def __str__(self):
        cust = self.customer.username if self.customer else (self.customer_name or "Walk-in Guest")
        return f"Order #{self.id} ({cust}) - {self.get_order_type_display()}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Product", on_delete=models.PROTECT, related_name="order_items")
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    # Links to the SalesRecord created for this line, so a purchase is traceable into Sales Data / Analytics / Forecasting.
    sales_record = models.OneToOneField("sales.SalesRecord", on_delete=models.SET_NULL, null=True, blank=True, related_name="order_item")

    @property
    def subtotal(self):
        return self.quantity * self.price

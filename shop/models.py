from django.conf import settings
from django.db import models


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

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.ticket_number:
            self.ticket_number = f"W-{self.id:03d}"
            Order.objects.filter(pk=self.pk).update(ticket_number=self.ticket_number)

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

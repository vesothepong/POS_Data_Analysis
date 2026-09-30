from django.conf import settings
from django.db import models


class Order(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.id} ({self.customer})"


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

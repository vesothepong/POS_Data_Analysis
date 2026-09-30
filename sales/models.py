from django.db import models


class SalesRecord(models.Model):
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="sales")
    sale_date = models.DateField()
    quantity_sold = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    source_file = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sale_date", "product_id"]


class UploadRecord(models.Model):
    file_name = models.CharField(max_length=255)
    rows_processed = models.PositiveIntegerField(default=0)
    rows_rejected = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=30, default="Completed")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True)

from django.db import models


class Forecast(models.Model):
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="forecasts")
    forecast_month = models.DateField()
    predicted_quantity = models.PositiveIntegerField()
    model_name = models.CharField(max_length=100, default="Linear Regression")
    mae = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-forecast_month", "product_id"]

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [("products", "0001_initial")]
    operations = [
        migrations.CreateModel(name="Forecast", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("forecast_month", models.DateField()),
            ("predicted_quantity", models.PositiveIntegerField()),
            ("model_name", models.CharField(default="Linear Regression", max_length=100)),
            ("mae", models.FloatField(blank=True, null=True)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
            ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="forecasts", to="products.product")),
        ], options={"ordering": ["-forecast_month", "product_id"]}),
    ]

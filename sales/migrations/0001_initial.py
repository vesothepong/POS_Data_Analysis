import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [("products", "0001_initial")]
    operations = [
        migrations.CreateModel(name="UploadRecord", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("file_name", models.CharField(max_length=255)),
            ("rows_processed", models.PositiveIntegerField(default=0)),
            ("rows_rejected", models.PositiveIntegerField(default=0)),
            ("status", models.CharField(default="Completed", max_length=30)),
            ("uploaded_at", models.DateTimeField(auto_now_add=True)),
            ("message", models.TextField(blank=True)),
        ]),
        migrations.CreateModel(name="SalesRecord", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("sale_date", models.DateField()),
            ("quantity_sold", models.PositiveIntegerField()),
            ("price", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
            ("total_amount", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
            ("source_file", models.CharField(blank=True, max_length=255)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
            ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="sales", to="products.product")),
        ], options={"ordering": ["sale_date", "product_id"]}),
    ]

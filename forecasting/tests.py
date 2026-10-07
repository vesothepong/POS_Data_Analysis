import io

import pandas as pd
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from products.models import Product

from .models import Forecast


class ForecastFlowTests(TestCase):
    def setUp(self):
        self.client.force_login(get_user_model().objects.create_user("boss", password="pw12345!", is_staff=True, is_superuser=True))
        rows = [[f"2025-0{m}-10", "Tee", q, 5] for m, q in zip(range(1, 6), [100, 120, 130, 150, 160])]
        buf = io.BytesIO()
        pd.DataFrame(rows, columns=["Date", "Product", "Quantity Sold", "Price"]).to_excel(buf, index=False)
        self.client.post(reverse("upload_sales"), {"file": SimpleUploadedFile("s.xlsx", buf.getvalue())})
        self.product = Product.objects.get(name="Tee")
        self.product.stock_quantity, self.product.reorder_level = 80, 10
        self.product.save()

    def test_forecast_reorder_and_status(self):
        r = self.client.post(reverse("forecast"), {"product": self.product.id})
        self.assertEqual(r.status_code, 200)
        f = Forecast.objects.get(product=self.product)
        self.assertEqual(f.predicted_quantity, 177)
        self.assertEqual(r.context["reorder"], 97)
        self.assertEqual(r.context["status"], "Need Reorder")
        self.client.post(reverse("forecast"), {"product": self.product.id})  # regenerate replaces, no duplicate
        self.assertEqual(Forecast.objects.filter(product=self.product).count(), 1)

    def test_forecast_all_and_accuracy(self):
        self.client.post(reverse("forecast"), {"product": "all"})
        self.assertEqual(Forecast.objects.count(), 1)
        r = self.client.get(reverse("accuracy"))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.context["results"]), 1)

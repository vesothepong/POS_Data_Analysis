import io

import pandas as pd
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import SalesRecord, UploadRecord


def xlsx(rows, cols=("Date", "Product", "Quantity Sold", "Price")):
    buf = io.BytesIO()
    pd.DataFrame(rows, columns=list(cols)).to_excel(buf, index=False)
    return SimpleUploadedFile("sales.xlsx", buf.getvalue())


class UploadTests(TestCase):
    def setUp(self):
        self.client.force_login(get_user_model().objects.create_user("boss", password="pw12345!", is_staff=True, is_superuser=True))

    def test_upload_dedupes_and_rejects(self):
        rows = [["2025-01-05", "Tee", 10, 5], ["2025-01-05", "Tee", 10, 5], ["bad", "Tee", 1, 1], ["2025-02-05", "Tee", 12, 5]]
        self.client.post(reverse("upload_sales"), {"file": xlsx(rows)})
        self.assertEqual(SalesRecord.objects.count(), 2)
        up = UploadRecord.objects.latest("id")
        self.assertEqual((up.rows_processed, up.rows_rejected, up.status), (2, 1, "Completed"))
        self.client.post(reverse("upload_sales"), {"file": xlsx(rows)})  # re-upload adds nothing
        self.assertEqual(SalesRecord.objects.count(), 2)
        self.assertEqual(UploadRecord.objects.latest("id").status, "Rejected")

    def test_missing_columns_rejected(self):
        r = self.client.post(reverse("upload_sales"), {"file": xlsx([["2025-01-01", "A", 1]], cols=("Date", "Product", "Quantity Sold"))})
        self.assertContains(r, "Missing required columns")
        self.assertEqual(SalesRecord.objects.count(), 0)

    def test_filters(self):
        self.client.post(reverse("upload_sales"), {"file": xlsx([["2025-01-05", "Tee", 10, 5], ["2025-02-05", "Cap", 3, 2]])})
        r = self.client.get(reverse("sales") + "?month=2025-02")
        self.assertEqual(r.context["count"], 1)
        r = self.client.get(reverse("sales") + "?date_from=2025-01-01&date_to=2025-01-31")
        self.assertEqual(r.context["count"], 1)
        r = self.client.get(reverse("sales") + "?year=2025&month=garbage")
        self.assertEqual(r.status_code, 200)

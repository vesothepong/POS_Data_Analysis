import io

import pandas as pd
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse


class DashboardTests(TestCase):
    def setUp(self):
        self.client.force_login(get_user_model().objects.create_user("boss", password="pw12345!", is_staff=True))

    def test_admin_can_open_every_page_when_empty(self):
        for name in ("dashboard", "products", "sales", "upload_sales", "inventory", "forecast", "analytics", "accuracy", "reports"):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)
        self.assertEqual(self.client.get(reverse("api_analytics")).status_code, 200)
        self.assertEqual(self.client.get(reverse("api_dashboard")).status_code, 200)

    def test_all_reports_and_exports_after_upload(self):
        rows = [[f"2025-0{m}-10", "Tee", q, 5] for m, q in zip(range(1, 7), [100, 120, 130, 150, 160, 170])]
        buf = io.BytesIO()
        pd.DataFrame(rows, columns=["Date", "Product", "Quantity Sold", "Price"]).to_excel(buf, index=False)
        self.client.post(reverse("upload_sales"), {"file": SimpleUploadedFile("s.xlsx", buf.getvalue())})
        self.client.post(reverse("forecast"), {"product": "all"})
        for kind in ("sales", "inventory", "performance", "forecast", "reorder", "revenue"):
            self.assertEqual(self.client.get(reverse("reports") + f"?type={kind}").status_code, 200, kind)
            for fmt in ("csv", "xlsx"):
                self.assertEqual(self.client.get(reverse("report_export", args=[kind, fmt])).status_code, 200, (kind, fmt))
        self.assertEqual(self.client.get(reverse("report_export", args=["nope", "csv"])).status_code, 404)
        for name in ("analytics", "accuracy", "inventory"):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)

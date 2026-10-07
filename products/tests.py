from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Product


class ProductTests(TestCase):
    def setUp(self):
        self.client.force_login(get_user_model().objects.create_user("boss", password="pw12345!", is_staff=True, is_superuser=True))

    def test_crud(self):
        self.client.post(reverse("product_create"), {"name": "Cap", "category": "Acc", "price": "5", "stock_quantity": 3, "reorder_level": 2})
        p = Product.objects.get(name="Cap")
        self.client.post(reverse("product_edit", args=[p.id]), {"name": "Cap", "category": "Acc", "price": "6", "stock_quantity": 9, "reorder_level": 2})
        p.refresh_from_db()
        self.assertEqual(p.stock_quantity, 9)
        self.assertEqual(self.client.get(reverse("product_delete", args=[p.id])).status_code, 200)
        self.client.post(reverse("product_delete", args=[p.id]))
        self.assertFalse(Product.objects.exists())

    def test_stock_update_validation_and_status(self):
        p = Product.objects.create(name="Cap", stock_quantity=5, reorder_level=10)
        self.client.post(reverse("inventory_update", args=[p.id]), {"stock_quantity": "-3"})
        p.refresh_from_db()
        self.assertEqual(p.stock_quantity, 5)
        self.client.post(reverse("inventory_update", args=[p.id]), {"stock_quantity": "0"})
        r = self.client.get(reverse("inventory") + "?status=Out of Stock")
        self.assertEqual(len(r.context["rows"]), 1)
        self.assertEqual(self.client.get(reverse("inventory_detail", args=[p.id])).status_code, 200)

    def test_image_upload(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        # 1x1 GIF image bytes
        tiny_gif = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
        image = SimpleUploadedFile("test_img.gif", tiny_gif, content_type="image/gif")
        res = self.client.post(reverse("product_create"), {
            "name": "Hoodie", "category": "Clothing", "price": "45",
            "stock_quantity": 20, "reorder_level": 5, "image": image
        })
        self.assertEqual(res.status_code, 302)
        p = Product.objects.get(name="Hoodie")
        self.assertTrue(bool(p.image))
        self.assertTrue(p.image.name.startswith("products/"))
        self.assertIsNotNone(p.image_url)

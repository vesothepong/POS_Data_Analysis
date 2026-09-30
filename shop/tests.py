from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from products.models import Product
from sales.models import SalesRecord

from .models import Order


class StorefrontFlowTests(TestCase):
    def setUp(self):
        U = get_user_model()
        self.admin = U.objects.create_user("boss", password="pw12345!", is_staff=True)
        self.customer = U.objects.create_user("shopper", password="pw12345!")
        self.product = Product.objects.create(name="Tee", category="Clothing", price="10.00", stock_quantity=5, reorder_level=2)

    def test_customer_cannot_see_admin_pages(self):
        self.client.force_login(self.customer)
        self.assertEqual(self.client.get(reverse("dashboard")).status_code, 403)

    def test_admin_can_still_browse_shop(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(reverse("catalog")).status_code, 200)

    def test_anonymous_home_goes_to_login_customer_and_admin_split(self):
        self.assertEqual(self.client.get(reverse("home")).status_code, 302)
        self.client.force_login(self.customer)
        self.assertEqual(self.client.get(reverse("home"))["Location"], reverse("catalog"))
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(reverse("home"))["Location"], reverse("dashboard"))

    def test_add_to_cart_checkout_creates_sales_record_and_decrements_stock(self):
        self.client.force_login(self.customer)
        self.client.post(reverse("add_to_cart", args=[self.product.id]), {"quantity": 3})
        r = self.client.get(reverse("cart"))
        self.assertEqual(r.context["total"], 30.0)
        self.client.post(reverse("checkout"))
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 2)
        self.assertEqual(SalesRecord.objects.filter(product=self.product).count(), 1)
        order = Order.objects.get(customer=self.customer)
        self.assertEqual(order.items.first().quantity, 3)
        self.assertEqual(float(order.total_amount), 30.0)
        # cart cleared after checkout
        self.assertEqual(self.client.get(reverse("cart")).context["items"], [])

    def test_cannot_buy_more_than_stock(self):
        self.client.force_login(self.customer)
        self.client.post(reverse("add_to_cart", args=[self.product.id]), {"quantity": 999})
        r = self.client.get(reverse("cart"))
        self.assertEqual(r.context["items"][0]["quantity"], 5)  # capped to stock

    def test_checkout_empty_cart_redirects_with_message(self):
        self.client.force_login(self.customer)
        r = self.client.post(reverse("checkout"), follow=True)
        self.assertContains(r, "cart is empty")

    def test_admin_sees_customer_orders(self):
        self.client.force_login(self.customer)
        self.client.post(reverse("add_to_cart", args=[self.product.id]), {"quantity": 1})
        self.client.post(reverse("checkout"))
        self.client.force_login(self.admin)
        r = self.client.get(reverse("customer_orders"))
        self.assertContains(r, "shopper")


class RegistrationTests(TestCase):
    def test_register_creates_customer_and_logs_in(self):
        r = self.client.post(reverse("register"), {"username": "newuser", "email": "n@example.com",
                                                    "password1": "Sup3rSecret!", "password2": "Sup3rSecret!"})
        user = get_user_model().objects.get(username="newuser")
        self.assertFalse(user.is_staff)
        self.assertRedirects(r, reverse("catalog"))

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

    def test_admin_sees_walkin_guest_order_without_customer_account(self):
        # Walk-in guest order has customer=None
        order = Order.objects.create(
            customer=None,
            customer_name="Table 4 Guest",
            order_type="dine_in",
            table_number="Table 4",
            payment_method="cash",
            total_amount="10.00",
        )
        self.client.force_login(self.admin)
        r = self.client.get(reverse("customer_orders"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Table 4 Guest")
        self.assertContains(r, "DINE IN")



class RegistrationTests(TestCase):
    def test_register_creates_customer_and_logs_in(self):
        r = self.client.post(reverse("register"), {"username": "newuser", "email": "n@example.com",
                                                    "password1": "Sup3rSecret!", "password2": "Sup3rSecret!"})
        user = get_user_model().objects.get(username="newuser")
        self.assertFalse(user.is_staff)
        self.assertRedirects(r, reverse("catalog"))


class WalkInPOSTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Artisan Cappuccino",
            category="Beverages",
            price="4.50",
            stock_quantity=50,
            reorder_level=10,
        )

    def test_guest_can_browse_and_order_walkin(self):
        # 1. Unauthenticated guest can view catalog (status 200)
        r = self.client.get(reverse("catalog"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Walk-in Order Ticket")
        self.assertContains(r, "Artisan Cappuccino")

        # 2. Add via AJAX
        r_add = self.client.post(
            reverse("add_to_cart", args=[self.product.id]),
            {"quantity": 2},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(r_add.status_code, 200)
        data = r_add.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["cart"]["count"], 2)
        self.assertEqual(data["cart"]["total"], 9.00)

        # 3. Checkout via AJAX as Dine-In with table number and card payment
        r_checkout = self.client.post(
            reverse("checkout"),
            {
                "order_type": "dine_in",
                "customer_name": "Walk-in Guest",
                "table_number": "Table 7",
                "payment_method": "card",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(r_checkout.status_code, 200)
        co_data = r_checkout.json()
        self.assertTrue(co_data["success"])
        self.assertTrue(co_data["ticket_number"].startswith("W-"))
        self.assertEqual(co_data["order_type"], "dine_in")
        self.assertEqual(co_data["table_number"], "Table 7")
        self.assertEqual(co_data["payment_method"], "card")
        self.assertEqual(co_data["total"], 9.00)

        # 4. Product stock decremented & SalesRecord created
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 48)
        sales = SalesRecord.objects.filter(product=self.product)
        self.assertEqual(sales.count(), 1)
        self.assertEqual(sales.first().source_file, "Walk-in order")

        # 5. Order history for this guest session shows the order
        r_hist = self.client.get(reverse("order_history"))
        self.assertEqual(r_hist.status_code, 200)
        self.assertContains(r_hist, co_data["ticket_number"])
        self.assertContains(r_hist, "TABLE 7")


class DailyOrderTicketTests(TestCase):
    def test_same_day_sequential_tickets(self):
        o1 = Order.objects.create(customer_name="Customer 1", total_amount="5.00")
        o2 = Order.objects.create(customer_name="Customer 2", total_amount="5.00")
        o3 = Order.objects.create(customer_name="Customer 3", total_amount="5.00")

        self.assertEqual(o1.ticket_number, "W-001")
        self.assertEqual(o2.ticket_number, "W-002")
        self.assertEqual(o3.ticket_number, "W-003")

    def test_daily_ticket_number_resets_next_day(self):
        import datetime
        from django.utils import timezone

        tz = timezone.get_current_timezone()
        day1 = timezone.make_aware(datetime.datetime(2026, 10, 1, 10, 0, 0), tz)
        day2 = timezone.make_aware(datetime.datetime(2026, 10, 2, 8, 30, 0), tz)

        # Day 1 orders
        o1 = Order.objects.create(customer_name="Day1 Guest 1", total_amount="10.00")
        Order.objects.filter(pk=o1.pk).update(created_at=day1, ticket_number="W-001")
        o2 = Order.objects.create(customer_name="Day1 Guest 2", total_amount="15.00")
        Order.objects.filter(pk=o2.pk).update(created_at=day1, ticket_number="W-002")

        # Third order on Day 1 should be W-003
        self.assertEqual(Order.get_next_ticket_number(for_datetime=day1), "W-003")

        # On Day 2, it must reset to W-001 (not W-003)
        self.assertEqual(Order.get_next_ticket_number(for_datetime=day2), "W-001")

        # Create order on Day 2
        o_day2 = Order.objects.create(customer_name="Day2 Guest 1", total_amount="20.00", created_at=day2)
        Order.objects.filter(pk=o_day2.pk).update(created_at=day2, ticket_number="W-001")

        # Next order on Day 2 should be W-002
        self.assertEqual(Order.get_next_ticket_number(for_datetime=day2), "W-002")

    def test_ticket_number_not_overwritten_on_update(self):
        order = Order.objects.create(customer_name="Guest", total_amount="12.00")
        orig_ticket = order.ticket_number
        order.total_amount = "15.00"
        order.save()
        order.refresh_from_db()
        self.assertEqual(order.ticket_number, orig_ticket)




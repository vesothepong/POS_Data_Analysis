from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from products.models import Product, Topping
from sales.models import SalesRecord

from .models import Order, OrderItemTopping


class StorefrontFlowTests(TestCase):
    def setUp(self):
        U = get_user_model()
        self.admin = U.objects.create_user("boss", password="pw12345!", is_staff=True, is_superuser=True)
        self.customer = U.objects.create_user("shopper", password="pw12345!")
        self.product = Product.objects.create(name="Tee", category="Clothing", price="10.00", stock_quantity=5, reorder_level=2)

    def test_admin_can_browse_and_use_pos(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(reverse("catalog")).status_code, 200)

    def test_anonymous_home_goes_to_login_and_admin_to_dashboard(self):
        self.assertEqual(self.client.get(reverse("home")).status_code, 302)
        self.assertEqual(self.client.get(reverse("home"))["Location"], reverse("login"))
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(reverse("home"))["Location"], reverse("dashboard"))

    def test_add_to_cart_checkout_creates_sales_record_and_decrements_stock(self):
        self.client.force_login(self.admin)
        self.client.post(reverse("add_to_cart", args=[self.product.id]), {"quantity": 3})
        r = self.client.get(reverse("cart"))
        self.assertEqual(r.context["total"], 30.0)
        self.client.post(reverse("checkout"))
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 2)
        self.assertEqual(SalesRecord.objects.filter(product=self.product).count(), 1)
        order = Order.objects.get(customer=self.admin)
        self.assertEqual(order.items.first().quantity, 3)
        self.assertEqual(float(order.total_amount), 30.0)
        # cart cleared after checkout
        self.assertEqual(self.client.get(reverse("cart")).context["items"], [])

    def test_cannot_buy_more_than_stock(self):
        self.client.force_login(self.admin)
        self.client.post(reverse("add_to_cart", args=[self.product.id]), {"quantity": 999})
        r = self.client.get(reverse("cart"))
        self.assertEqual(r.context["items"][0]["quantity"], 5)  # capped to stock

    def test_checkout_empty_cart_redirects_with_message(self):
        self.client.force_login(self.admin)
        r = self.client.post(reverse("checkout"), follow=True)
        self.assertContains(r, "cart is empty")

    def test_admin_sees_walkin_orders(self):
        self.client.force_login(self.admin)
        self.client.post(reverse("add_to_cart", args=[self.product.id]), {"quantity": 1})
        self.client.post(reverse("checkout"), {"customer_name": "Table 2 Guest"})
        r = self.client.get(reverse("customer_orders"))
        self.assertContains(r, "Table 2 Guest")

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
    def test_register_creates_admin_and_logs_in(self):
        r = self.client.post(reverse("register"), {"username": "newadmin", "email": "admin@example.com",
                                                    "role": "admin",
                                                    "password1": "Sup3rSecret!1", "password2": "Sup3rSecret!1"})
        user = get_user_model().objects.get(username="newadmin")
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertEqual(user.profile.role, "admin")
        self.assertRedirects(r, reverse("dashboard"))

    def test_register_creates_staff_and_logs_in_to_pos(self):
        r = self.client.post(reverse("register"), {"username": "newstaff", "email": "staff@example.com",
                                                    "role": "staff",
                                                    "password1": "Sup3rSecret!1", "password2": "Sup3rSecret!1"})
        user = get_user_model().objects.get(username="newstaff")
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertEqual(user.profile.role, "staff")
        self.assertRedirects(r, reverse("catalog"))


class WalkInPOSTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Artisan Cappuccino",
            category="Drink",
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

        # 6. Subsequent visit to catalog must NOT auto-open the receipt modal
        r_catalog = self.client.get(reverse("catalog"))
        self.assertEqual(r_catalog.status_code, 200)
        self.assertIsNone(r_catalog.context["receipt_order"])
        self.assertNotContains(r_catalog, 'data-auto-open="true"')


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


class POSToppingFlowTests(TestCase):
    def setUp(self):
        self.drink = Product.objects.create(
            name="Brown Sugar Boba Milk",
            category="Drink",
            price="4.00",
            stock_quantity=20,
            reorder_level=5,
        )
        self.topping_boba = Topping.objects.create(
            name="Extra Boba",
            price="0.50",
            stock_quantity=50,
            applicable_category="Drink",
        )
        self.topping_pudding = Topping.objects.create(
            name="Custard Pudding",
            price="0.75",
            stock_quantity=30,
            applicable_category="Drink",
        )

    def test_add_to_cart_with_toppings_calculates_correct_price(self):
        # Add item with boba and pudding (4.00 + 0.50 + 0.75 = 5.25 each x 2 = 10.50)
        r = self.client.post(
            reverse("add_to_cart", args=[self.drink.id]),
            {"quantity": 2, "toppings": f"{self.topping_boba.id},{self.topping_pudding.id}"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["cart"]["count"], 2)
        self.assertEqual(data["cart"]["total"], 10.50)

    def test_add_same_product_with_different_toppings_creates_distinct_lines(self):
        # Line 1: Drink with Extra Boba (4.00 + 0.50 = 4.50)
        self.client.post(
            reverse("add_to_cart", args=[self.drink.id]),
            {"quantity": 1, "toppings": str(self.topping_boba.id)},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        # Line 2: Plain Drink (4.00)
        self.client.post(
            reverse("add_to_cart", args=[self.drink.id]),
            {"quantity": 1},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        r = self.client.get(reverse("cart"), HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        cart_data = r.json()["cart"]
        self.assertEqual(cart_data["count"], 2)
        self.assertEqual(len(cart_data["items"]), 2)
        self.assertEqual(cart_data["total"], 8.50)

    def test_checkout_with_toppings_decrements_stock_and_creates_records(self):
        # Add 2x Customized Drink: 4.00 + 0.50 + 0.75 = 5.25 x 2 = 10.50
        self.client.post(
            reverse("add_to_cart", args=[self.drink.id]),
            {"quantity": 2, "toppings": f"{self.topping_boba.id},{self.topping_pudding.id}"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        r = self.client.post(
            reverse("checkout"),
            {"order_type": "dine_in", "customer_name": "Bob", "table_number": "Table 1", "payment_method": "cash"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(r.status_code, 200)
        co_data = r.json()
        self.assertTrue(co_data["success"])
        self.assertEqual(co_data["total"], 10.50)

        # Verify product stock decremented by 2
        self.drink.refresh_from_db()
        self.assertEqual(self.drink.stock_quantity, 18)

        # Verify toppings stock decremented by 2
        self.topping_boba.refresh_from_db()
        self.assertEqual(self.topping_boba.stock_quantity, 48)
        self.topping_pudding.refresh_from_db()
        self.assertEqual(self.topping_pudding.stock_quantity, 28)

        # Verify OrderItem and OrderItemTopping records
        order = Order.objects.get(id=co_data["order_id"])
        self.assertEqual(order.items.count(), 1)
        item = order.items.first()
        self.assertEqual(item.quantity, 2)
        self.assertEqual(float(item.price), 5.25)
        self.assertEqual(item.toppings.count(), 2)
        self.assertIn("Extra Boba", item.toppings_summary)
        self.assertIn("Custard Pudding", item.toppings_summary)




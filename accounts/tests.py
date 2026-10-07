from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import Profile


class RoleAndAccessTests(TestCase):
    def setUp(self):
        U = get_user_model()
        self.admin = U.objects.create_superuser("boss", "boss@example.com", "pw12345!")
        p_admin, _ = Profile.objects.get_or_create(user=self.admin)
        p_admin.role = Profile.ROLE_ADMIN
        p_admin.save()

        self.staff = U.objects.create_user("cashier", "cashier@example.com", "pw12345!", is_staff=True)
        p_staff, _ = Profile.objects.get_or_create(user=self.staff)
        p_staff.role = Profile.ROLE_STAFF
        p_staff.save()

        self.guest = U.objects.create_user("shopper", "shopper@example.com", "pw12345!")

    def test_anonymous_redirected_to_login(self):
        r = self.client.get(reverse("dashboard"))
        self.assertEqual(r.status_code, 302)
        self.assertIn("/login/", r["Location"])

    def test_home_page_role_redirection(self):
        # Anonymous goes to login
        self.assertEqual(self.client.get(reverse("home"))["Location"], reverse("login"))

        # Admin goes to dashboard (full control)
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(reverse("home"))["Location"], reverse("dashboard"))
        self.client.logout()

        # Staff goes to POS catalog (POS control)
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(reverse("home"))["Location"], reverse("catalog"))

    def test_admin_has_full_control(self):
        """Admin has full control over all modules, reports, APIs, and POS."""
        self.client.force_login(self.admin)
        admin_urls = [
            "dashboard", "products", "sales", "upload_sales", "inventory",
            "forecast", "analytics", "accuracy", "reports", "customer_orders",
            "catalog", "cart", "order_history"
        ]
        for name in admin_urls:
            r = self.client.get(reverse(name))
            self.assertEqual(r.status_code, 200, f"Admin should access {name}")

        self.assertEqual(self.client.get(reverse("api_analytics")).status_code, 200)
        self.assertEqual(self.client.get(reverse("api_dashboard")).status_code, 200)

    def test_staff_controls_pos(self):
        """Staff has access to Point of Sale (POS) and order tickets."""
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(reverse("catalog")).status_code, 200)
        self.assertEqual(self.client.get(reverse("cart")).status_code, 200)
        self.assertEqual(self.client.get(reverse("order_history")).status_code, 200)

    def test_staff_forbidden_from_admin_modules(self):
        """Staff is denied (403) from accessing admin workspace and APIs."""
        self.client.force_login(self.staff)
        restricted_urls = [
            "dashboard", "products", "product_create", "sales", "upload_sales",
            "inventory", "forecast", "analytics", "accuracy", "reports", "customer_orders"
        ]
        for name in restricted_urls:
            r = self.client.get(reverse(name))
            self.assertEqual(r.status_code, 403, f"Staff must be forbidden (403) from {name}")

        self.assertEqual(self.client.get(reverse("api_analytics")).status_code, 403)
        self.assertEqual(self.client.get(reverse("api_dashboard")).status_code, 403)

    def test_login_landing_url_by_role(self):
        # Admin logs in -> lands on dashboard
        r_admin = self.client.post(reverse("login"), {"username": "boss", "password": "pw12345!"})
        self.assertRedirects(r_admin, reverse("dashboard"))
        self.client.logout()

        # Staff logs in -> lands on POS catalog
        r_staff = self.client.post(reverse("login"), {"username": "cashier", "password": "pw12345!"})
        self.assertRedirects(r_staff, reverse("catalog"))


class RegisterTests(TestCase):
    def test_register_as_admin_creates_superuser_and_redirects_dashboard(self):
        r = self.client.post(reverse("register"), {
            "username": "newboss",
            "email": "nb@example.com",
            "role": "admin",
            "password1": "Str0ngPass!9",
            "password2": "Str0ngPass!9"
        })
        self.assertRedirects(r, reverse("dashboard"))
        u = get_user_model().objects.get(username="newboss")
        self.assertTrue(u.is_superuser)
        self.assertTrue(u.is_staff)
        self.assertEqual(u.profile.role, "admin")

    def test_register_as_staff_creates_pos_user_and_redirects_pos(self):
        r = self.client.post(reverse("register"), {
            "username": "newcashier",
            "email": "nc@example.com",
            "role": "staff",
            "password1": "Str0ngPass!9",
            "password2": "Str0ngPass!9"
        })
        self.assertRedirects(r, reverse("catalog"))
        u = get_user_model().objects.get(username="newcashier")
        self.assertFalse(u.is_superuser)
        self.assertTrue(u.is_staff)
        self.assertEqual(u.profile.role, "staff")

    def test_register_rejects_mismatch(self):
        r = self.client.post(reverse("register"), {
            "username": "x",
            "email": "x@example.com",
            "role": "staff",
            "password1": "a1b2c3d4!",
            "password2": "zzz"
        })
        self.assertEqual(r.status_code, 200)
        self.assertFalse(get_user_model().objects.filter(username="x").exists())

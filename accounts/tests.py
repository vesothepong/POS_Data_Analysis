from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AccessTests(TestCase):
    def setUp(self):
        U = get_user_model()
        self.admin = U.objects.create_user("boss", password="pw12345!", is_staff=True)
        self.guest = U.objects.create_user("guest", password="pw12345!")

    def test_anonymous_redirected_to_login(self):
        r = self.client.get(reverse("dashboard"))
        self.assertEqual(r.status_code, 302)
        self.assertIn("/login/", r["Location"])

    def test_non_admin_forbidden_and_api_protected(self):
        self.client.force_login(self.guest)
        self.assertEqual(self.client.get(reverse("dashboard")).status_code, 403)
        self.assertEqual(self.client.get(reverse("api_analytics")).status_code, 403)
        self.assertEqual(self.client.get(reverse("api_dashboard")).status_code, 403)

    def test_login_page_and_logout_post(self):
        self.assertEqual(self.client.get(reverse("login")).status_code, 200)
        self.client.force_login(self.admin)
        self.assertEqual(self.client.post(reverse("logout")).status_code, 302)
        self.assertEqual(self.client.get(reverse("dashboard")).status_code, 302)


class RegisterTests(TestCase):
    def test_register_creates_user_and_logs_in(self):
        self.assertEqual(self.client.get(reverse("register")).status_code, 200)
        r = self.client.post(reverse("register"), {"username": "newcust", "email": "n@example.com", "password1": "Str0ngPass!9", "password2": "Str0ngPass!9"})
        self.assertEqual(r.status_code, 302)
        u = get_user_model().objects.get(username="newcust")
        self.assertTrue(u.is_staff)
        self.assertEqual(int(self.client.session["_auth_user_id"]), u.pk)

    def test_register_rejects_mismatch(self):
        r = self.client.post(reverse("register"), {"username": "x", "email": "x@example.com", "password1": "a1b2c3d4!", "password2": "zzz"})
        self.assertEqual(r.status_code, 200)
        self.assertFalse(get_user_model().objects.filter(username="x").exists())

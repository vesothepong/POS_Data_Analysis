from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import RegisterForm


def _landing_url(user):
    return reverse("dashboard") if (user.is_staff or user.is_superuser) else reverse("catalog")


class AppLoginView(LoginView):
    template_name = "accounts/login.html"

    def get_success_url(self):
        return _landing_url(self.request.user)


def register(request):
    """New accounts are customers (not staff) by default; only createsuperuser / seed_demo / the
    Django admin grant the admin (is_staff) role."""
    if request.user.is_authenticated:
        return redirect(_landing_url(request.user))
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        return redirect(_landing_url(user))
    return render(request, "accounts/register.html", {"form": form})


def home(request):
    """Root URL: route each visitor to their role's landing page.
    Unauthenticated visitors land directly on the Walk-in ordering kiosk."""
    if not request.user.is_authenticated:
        return redirect("catalog")
    return redirect(_landing_url(request.user))

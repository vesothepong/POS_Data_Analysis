from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import RegisterForm
from .permissions import is_admin, is_staff_member


def _landing_url(user):
    """Admin lands on Dashboard (full control); Staff lands on POS Catalog."""
    if is_admin(user):
        return reverse("dashboard")
    return reverse("catalog")


class AppLoginView(LoginView):
    template_name = "accounts/login.html"

    def get_success_url(self):
        return _landing_url(self.request.user)


def register(request):
    """Register either an Admin or Staff member with designated role & permissions."""
    if request.user.is_authenticated:
        return redirect(_landing_url(request.user))
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        return redirect(_landing_url(user))
    return render(request, "accounts/register.html", {"form": form})


def home(request):
    """Root URL:
    - If unauthenticated, redirect to login.
    - If Admin, redirect to dashboard (full control).
    - If Staff, redirect to POS catalog (POS control).
    """
    if not request.user.is_authenticated:
        return redirect("login")
    if is_admin(request.user):
        return redirect("dashboard")
    return redirect("catalog")

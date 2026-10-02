from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import RegisterForm


def _landing_url(user):
    return reverse("dashboard")


class AppLoginView(LoginView):
    template_name = "accounts/login.html"

    def get_success_url(self):
        return _landing_url(self.request.user)


def register(request):
    """Every registered user has the Admin role."""
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        user.is_staff = True
        user.save()
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        return redirect("dashboard")
    return render(request, "accounts/register.html", {"form": form})


def home(request):
    """Root URL: if authenticated, redirect to dashboard.
    If unauthenticated, redirect to login."""
    if not request.user.is_authenticated:
        return redirect("login")
    return redirect("dashboard")

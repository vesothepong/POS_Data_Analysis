from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied


def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def admin_required(view):
    """Login required AND the user must be an admin (is_staff / superuser)."""
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not is_admin(request.user):
            raise PermissionDenied("Admin role required.")
        return view(request, *args, **kwargs)
    return wrapper

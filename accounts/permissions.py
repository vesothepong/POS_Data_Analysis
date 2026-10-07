from functools import wraps
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission


def get_user_role(user):
    """Return the normalized role string: 'admin', 'staff', or 'guest'."""
    if not user or not user.is_authenticated:
        return "guest"
    profile = getattr(user, "profile", None)
    if profile and profile.role:
        return profile.role
    if user.is_superuser:
        return "admin"
    if user.is_staff:
        return "staff"
    return "guest"


def is_admin(user):
    """Admin role: Full control over dashboard, products, sales, inventory,
    forecasting, analytics, reports, and POS."""
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    profile = getattr(user, "profile", None)
    if profile and profile.role == "admin":
        return True
    return False


def is_staff_member(user):
    """Staff role: Controls the Point of Sale (POS) catalog, tickets, cart, and checkout.
    Admin also inherits full staff/POS privileges."""
    if not user or not user.is_authenticated:
        return False
    if is_admin(user):
        return True
    profile = getattr(user, "profile", None)
    if profile and profile.role == "staff":
        return True
    if user.is_staff and not is_admin(user):
        return True
    return False


def admin_required(view):
    """Requires authentication AND Admin role (full control).
    Redirects unauthenticated users to login.
    Raises PermissionDenied (HTTP 403) for Staff or other non-admin users."""
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not is_admin(request.user):
            raise PermissionDenied("Administrator privileges are required for this action.")
        return view(request, *args, **kwargs)
    return wrapper


def staff_required(view):
    """Requires authentication AND at least Staff (or Admin) role.
    Redirects unauthenticated users to login.
    Raises PermissionDenied (HTTP 403) for unauthorized users."""
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not is_staff_member(request.user):
            raise PermissionDenied("Staff or Administrator privileges are required.")
        return view(request, *args, **kwargs)
    return wrapper


class IsAdminRole(BasePermission):
    """REST framework permission check ensuring only Admin role can access admin APIs."""
    message = "Administrator privileges are required to access this API."

    def has_permission(self, request, view):
        return bool(request.user and is_admin(request.user))

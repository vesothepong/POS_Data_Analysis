from .permissions import is_admin, is_staff_member, get_user_role


def auth_roles(request):
    """Context processor providing authentication and role flags to all templates."""
    user = getattr(request, "user", None)
    admin_flag = is_admin(user)
    staff_flag = is_staff_member(user)
    role = get_user_role(user)
    return {
        "user_is_admin": admin_flag,
        "user_is_staff": staff_flag,
        "user_role": role,
    }

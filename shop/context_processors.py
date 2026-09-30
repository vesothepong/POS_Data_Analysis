from .services import cart_count as _cart_count


def cart_badge(request):
    if request.user.is_authenticated:
        return {"cart_count": _cart_count(request.session)}
    return {}

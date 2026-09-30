from django.shortcuts import render

from accounts.permissions import admin_required
from products.models import Product


@admin_required
def analytics(request):
    return render(request, "analytics/analytics.html", {"products": Product.objects.order_by("name")})

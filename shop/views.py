from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from products.models import Product

from .forms import AddToCartForm
from .models import Order
from .services import cart_contents, cart_count, checkout, remove_from_cart, set_quantity
from .services import add_to_cart as _add_to_cart


@login_required
def catalog(request):
    q = request.GET.get("q", "").strip()
    products = Product.objects.order_by("name")
    if q:
        products = products.filter(Q(name__icontains=q) | Q(category__icontains=q))
    return render(request, "shop/catalog.html", {"products": products, "q": q})


@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = AddToCartForm(request.POST)
        qty = form.cleaned_data["quantity"] if form.is_valid() else 1
        if product.stock_quantity <= 0:
            messages.error(request, f"{product.name} is out of stock.")
        else:
            _add_to_cart(request.session, product.id, qty)
            messages.success(request, f"Added {qty} x {product.name} to your cart.")
    nxt = request.POST.get("next")
    return redirect(nxt if nxt else "catalog")


@login_required
def cart_view(request):
    if request.method == "POST":
        action, pid = request.POST.get("action"), request.POST.get("product_id")
        if action == "remove":
            remove_from_cart(request.session, pid)
        elif action == "update":
            set_quantity(request.session, pid, request.POST.get("quantity", 0))
        return redirect("cart")
    items, total, warnings = cart_contents(request.session)
    for w in warnings:
        messages.warning(request, w)
    return render(request, "shop/cart.html", {"items": items, "total": total})


@login_required
def checkout_view(request):
    if request.method == "POST":
        try:
            order, warnings = checkout(request.user, request.session)
            for w in warnings:
                messages.warning(request, w)
            messages.success(request, f"Order #{order.id} placed successfully.")
            return redirect("order_history")
        except ValueError as e:
            messages.error(request, str(e))
            return redirect("cart")
    items, total, warnings = cart_contents(request.session)
    for w in warnings:
        messages.warning(request, w)
    return render(request, "shop/checkout.html", {"items": items, "total": total})


@login_required
def order_history(request):
    orders = Order.objects.filter(customer=request.user).prefetch_related("items__product")
    return render(request, "shop/orders.html", {"orders": orders})

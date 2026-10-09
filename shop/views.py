import json
from decimal import Decimal
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.permissions import is_staff_member
from products.models import Product, Topping

from .forms import AddToCartForm
from .models import Order
from .services import (
    cart_contents,
    cart_count,
    cart_summary,
    clear_cart,
    checkout,
    remove_from_cart,
    set_quantity,
)
from .services import add_to_cart as _add_to_cart


def _is_json_request(request):
    return (
        request.headers.get("x-requested-with") == "XMLHttpRequest"
        or request.content_type == "application/json"
        or request.POST.get("format") == "json"
        or request.GET.get("format") == "json"
    )


def catalog(request):
    """Walk-in POS / Kiosk catalog and ordering screen. Direct access for walk-in guests & users."""
    q = request.GET.get("q", "").strip()
    selected_cat = request.GET.get("category", "").strip()

    products = Product.objects.order_by("category", "name")
    if q:
        products = products.filter(Q(name__icontains=q) | Q(category__icontains=q))
    if selected_cat:
        products = products.filter(category__iexact=selected_cat)

    # Categories list and count
    raw_cats = Product.objects.exclude(category__isnull=True).exclude(category="").values_list("category", flat=True).distinct()
    categories = sorted(list(set(raw_cats)))
    category_data = [{"name": c, "count": Product.objects.filter(category=c).count()} for c in categories]
    total_products_count = Product.objects.count()

    # Active toppings for customization
    all_toppings = Topping.objects.filter(is_active=True).prefetch_related("products").order_by("name")
    toppings_json = json.dumps([
        {
            "id": t.id,
            "name": t.name,
            "price": float(t.price),
            "stock_quantity": t.stock_quantity,
            "applicable_category": t.applicable_category,
            "product_ids": list(t.products.values_list("id", flat=True)),
        }
        for t in all_toppings
    ])

    cart_items, cart_total, cart_warnings = cart_contents(request.session)
    for w in cart_warnings:
        messages.warning(request, w)

    # Check for receipt modal if an order was just completed
    receipt_order = None
    last_order_id = request.session.pop("last_walkin_order_id", None)
    if last_order_id:
        receipt_order = Order.objects.filter(id=last_order_id).prefetch_related("items__product", "items__toppings").first()

    context = {
        "products": products,
        "categories": categories,
        "category_data": category_data,
        "total_products_count": total_products_count,
        "selected_category": selected_cat,
        "q": q,
        "cart_items": cart_items,
        "cart_total": cart_total,
        "cart_count": sum(it["quantity"] for it in cart_items),
        "receipt_order": receipt_order,
        "toppings": all_toppings,
        "toppings_json": toppings_json,
    }
    return render(request, "shop/catalog.html", context)


def add_to_cart(request, pk):
    """Add item to walk-in cart. Supports both standard form POST and instantaneous AJAX."""
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        qty = 1
        if "quantity" in request.POST:
            try:
                qty = max(1, int(request.POST.get("quantity", 1)))
            except (ValueError, TypeError):
                qty = 1

        # Extract selected topping IDs
        raw_toppings = request.POST.getlist("toppings")
        topping_ids = []
        for item in raw_toppings:
            if isinstance(item, str) and "," in item:
                topping_ids.extend([t.strip() for t in item.split(",") if t.strip()])
            elif str(item).strip():
                topping_ids.append(str(item).strip())

        if product.stock_quantity <= 0:
            msg = f"{product.name} is currently out of stock."
            if _is_json_request(request):
                return JsonResponse({"success": False, "message": msg, "cart": cart_summary(request.session)}, status=400)
            messages.error(request, msg)
        else:
            _add_to_cart(request.session, product.id, qty, topping_ids=topping_ids)
            msg = f"Added {qty} × {product.name} to order."
            if _is_json_request(request):
                return JsonResponse({
                    "success": True,
                    "message": msg,
                    "cart": cart_summary(request.session),
                })
            messages.success(request, msg)

    nxt = request.POST.get("next")
    return redirect(nxt if nxt else "catalog")


def cart_view(request):
    """View and modify the walk-in cart. Supports AJAX update/remove/clear and standard POST."""
    if request.method == "POST":
        action = request.POST.get("action")
        item_key = request.POST.get("item_key") or request.POST.get("product_id")

        if action == "remove" and item_key:
            remove_from_cart(request.session, item_key)
        elif action == "update" and item_key:
            qty = request.POST.get("quantity", 0)
            set_quantity(request.session, item_key, qty)
        elif action == "clear":
            clear_cart(request.session)

        if _is_json_request(request):
            return JsonResponse({"success": True, "cart": cart_summary(request.session)})
        return redirect("cart")

    if _is_json_request(request):
        return JsonResponse({"success": True, "cart": cart_summary(request.session)})

    items, total, warnings = cart_contents(request.session)
    for w in warnings:
        messages.warning(request, w)
    return render(request, "shop/cart.html", {"items": items, "total": total})


def clear_cart_view(request):
    """Quick clear cart endpoint."""
    if request.method == "POST":
        clear_cart(request.session)
        if _is_json_request(request):
            return JsonResponse({"success": True, "cart": cart_summary(request.session)})
        messages.info(request, "Order ticket cleared.")
    return redirect("catalog")


def checkout_view(request):
    """Walk-in checkout: creates order ticket, deducts stock, mirrors to sales records."""
    if request.method == "POST":
        order_type = request.POST.get("order_type", "dine_in").strip()
        customer_name = request.POST.get("customer_name", "Walk-in Guest").strip()
        table_number = request.POST.get("table_number", "").strip()
        payment_method = request.POST.get("payment_method", "cash").strip()
        amount_tendered_raw = request.POST.get("amount_tendered", "").strip()
        change_due_raw = request.POST.get("change_due", "").strip()
        payment_reference = request.POST.get("payment_reference", "").strip()

        amount_tendered = None
        if amount_tendered_raw:
            try:
                amount_tendered = Decimal(amount_tendered_raw)
            except Exception:
                amount_tendered = None

        change_due = None
        if change_due_raw:
            try:
                change_due = Decimal(change_due_raw)
            except Exception:
                change_due = None

        try:
            order, warnings = checkout(
                user=request.user,
                session=request.session,
                order_type=order_type,
                customer_name=customer_name,
                table_number=table_number,
                payment_method=payment_method,
                amount_tendered=amount_tendered,
                change_due=change_due,
                payment_reference=payment_reference,
            )

            # Keep track of recent walk-in orders in session for guest history
            placed = request.session.get("placed_order_ids", [])
            placed.append(order.id)
            request.session["placed_order_ids"] = placed[-20:]  # keep recent 20

            for w in warnings:
                messages.warning(request, w)

            ticket_label = order.ticket_number or f"#{order.id}"
            messages.success(request, f"Walk-in Order {ticket_label} placed successfully!")

            if _is_json_request(request):
                # Clear any lingering receipt order in session so returning to POS doesn't re-trigger popup
                request.session.pop("last_walkin_order_id", None)
                items_data = [
                    {
                        "name": it.product.name,
                        "quantity": it.quantity,
                        "price": float(it.price),
                        "subtotal": float(it.subtotal),
                        "toppings": [t.topping_name for t in it.toppings.all()],
                        "toppings_text": it.toppings_summary,
                    }
                    for it in order.items.all().prefetch_related("toppings")
                ]
                return JsonResponse({
                    "success": True,
                    "order_id": order.id,
                    "ticket_number": ticket_label,
                    "customer_name": order.customer_name,
                    "order_type": order.order_type,
                    "order_type_display": order.get_order_type_display(),
                    "table_number": order.table_number,
                    "payment_method": order.payment_method,
                    "payment_method_display": order.get_payment_method_display(),
                    "amount_tendered": float(order.amount_tendered),
                    "change_due": float(order.change_due),
                    "payment_reference": order.payment_reference,
                    "total": float(order.total_amount),
                    "created_at": order.created_at.strftime("%b %d, %Y • %H:%M"),
                    "items": items_data,
                    "warnings": warnings,
                })

            # Non-AJAX fallback (e.g. traditional form POST): store in session so redirect shows receipt
            request.session["last_walkin_order_id"] = order.id
            return redirect("catalog")
        except ValueError as e:
            if _is_json_request(request):
                return JsonResponse({"success": False, "message": str(e)}, status=400)
            messages.error(request, str(e))
            return redirect("cart")

    items, total, warnings = cart_contents(request.session)
    for w in warnings:
        messages.warning(request, w)
    return render(request, "shop/checkout.html", {"items": items, "total": total})


def order_history(request):
    """Walk-in order history: displays customer orders or session's recent walk-in tickets.
    Staff and Admin can review all recent POS orders so they can manage order tickets."""
    recent_ids = request.session.get("placed_order_ids", [])
    if is_staff_member(request.user):
        orders = Order.objects.prefetch_related("items__product").distinct().order_by("-created_at")[:100]
    elif request.user.is_authenticated:
        orders = Order.objects.filter(
            Q(customer=request.user) | Q(id__in=recent_ids)
        ).prefetch_related("items__product").distinct().order_by("-created_at")
    else:
        orders = Order.objects.filter(id__in=recent_ids).prefetch_related("items__product").order_by("-created_at")

    return render(request, "shop/orders.html", {"orders": orders})

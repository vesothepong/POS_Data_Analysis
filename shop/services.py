"""Session-based cart + checkout. Checkout is the bridge between the storefront and the
admin side: every purchased line also creates a SalesRecord, so it appears immediately in
Sales Data, Data Analytics and Demand Forecast without any manual upload."""
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from products.models import Product
from sales.models import SalesRecord

from . import calc
from .models import Order, OrderItem

CART_SESSION_KEY = "cart"


def get_cart(session):
    return session.get(CART_SESSION_KEY, {})


def add_to_cart(session, product_id, quantity=1):
    cart = get_cart(session)
    key = str(product_id)
    cart[key] = cart.get(key, 0) + max(1, int(quantity))
    session[CART_SESSION_KEY] = cart
    session.modified = True


def set_quantity(session, product_id, quantity):
    cart = get_cart(session)
    key, quantity = str(product_id), int(quantity)
    if quantity <= 0:
        cart.pop(key, None)
    else:
        cart[key] = quantity
    session[CART_SESSION_KEY] = cart
    session.modified = True


def remove_from_cart(session, product_id):
    cart = get_cart(session)
    cart.pop(str(product_id), None)
    session[CART_SESSION_KEY] = cart
    session.modified = True


def clear_cart(session):
    session[CART_SESSION_KEY] = {}
    session.modified = True


def cart_count(session):
    return sum(get_cart(session).values())


def cart_contents(session):
    """Resolve the session cart into product rows + totals; caps quantities to current stock."""
    cart = get_cart(session)
    if not cart:
        return [], 0, []
    products = {p.id: p for p in Product.objects.filter(id__in=[int(k) for k in cart])}
    raw, warnings = [], []
    for pid_str, qty in cart.items():
        p = products.get(int(pid_str))
        if not p:
            warnings.append("A product in your cart is no longer available and was removed.")
            continue
        capped = min(qty, p.stock_quantity)
        if capped != qty:
            warnings.append(f"Only {p.stock_quantity} of {p.name} available; quantity adjusted.")
        if capped > 0:
            raw.append({"product": p, "quantity": capped, "price": float(p.price)})
    enriched, total = calc.cart_totals(raw)
    return enriched, total, warnings


def checkout(user, session):
    """Validate stock, create the Order/OrderItems, decrement stock, and mirror each line
    into SalesRecord. Raises ValueError (with a user-facing message) if the cart is empty
    or stock changed since the cart was built."""
    enriched, total, warnings = cart_contents(session)
    if not enriched:
        raise ValueError("Your cart is empty.")
    today = timezone.localdate()
    with transaction.atomic():
        order = Order.objects.create(customer=user, total_amount=Decimal(str(round(total, 2))))
        for row in enriched:
            product = Product.objects.get(pk=row["product"].pk)  # re-fetch: stock may have changed
            qty, price = row["quantity"], Decimal(str(row["price"]))
            if product.stock_quantity < qty:
                raise ValueError(f"Not enough stock for {product.name} (only {product.stock_quantity} left). Please update your cart.")
            product.stock_quantity -= qty
            product.save(update_fields=["stock_quantity", "updated_at"])
            record = SalesRecord.objects.create(product=product, sale_date=today, quantity_sold=qty, price=price,
                                                total_amount=Decimal(str(round(qty * float(price), 2))), source_file="Storefront order")
            OrderItem.objects.create(order=order, product=product, quantity=qty, price=price, sales_record=record)
    clear_cart(session)
    return order, warnings

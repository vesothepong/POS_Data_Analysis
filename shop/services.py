"""Session-based cart + checkout. Checkout is the bridge between the storefront and the
admin side: every purchased line also creates a SalesRecord, so it appears immediately in
Sales Data, Data Analytics and Demand Forecast without any manual upload."""
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from products.models import Product, Topping
from sales.models import SalesRecord

from . import calc
from .models import Order, OrderItem, OrderItemTopping

CART_SESSION_KEY = "cart"


def get_cart(session):
    return session.get(CART_SESSION_KEY, {})


def _normalize_cart(raw_cart):
    """Normalize raw session cart entries into a dict of:
    item_key -> {
        'product_id': int,
        'quantity': int,
        'topping_ids': [int, ...],
    }
    """
    normalized = {}
    if not isinstance(raw_cart, dict):
        return normalized
    for key, val in raw_cart.items():
        k = str(key)
        if isinstance(val, int):
            try:
                pid = int(k.split(":")[0])
                normalized[k] = {
                    "product_id": pid,
                    "quantity": max(0, val),
                    "topping_ids": [],
                }
            except (ValueError, TypeError):
                continue
        elif isinstance(val, dict):
            try:
                pid = int(val.get("product_id") or k.split(":")[0])
                qty = max(0, int(val.get("quantity", 0)))
                t_ids = sorted([int(t) for t in val.get("topping_ids", []) if str(t).isdigit()])
                normalized[k] = {
                    "product_id": pid,
                    "quantity": qty,
                    "topping_ids": t_ids,
                }
            except (ValueError, TypeError):
                continue
    return normalized


def _clean_topping_ids(topping_ids):
    cleaned = []
    if isinstance(topping_ids, str):
        items = topping_ids.split(",")
    elif isinstance(topping_ids, (list, tuple, set)):
        items = topping_ids
    else:
        items = [topping_ids] if topping_ids else []

    for item in items:
        if isinstance(item, str) and "," in item:
            for sub in item.split(","):
                if sub.strip().isdigit():
                    cleaned.append(int(sub.strip()))
        elif str(item).strip().isdigit():
            cleaned.append(int(str(item).strip()))
    return sorted(list(set(cleaned)))


def _make_item_key(product_id, topping_ids):
    t_ids = _clean_topping_ids(topping_ids)
    if not t_ids:
        return str(product_id)
    return f"{product_id}:{'-'.join(map(str, t_ids))}"


def add_to_cart(session, product_id, quantity=1, topping_ids=None):
    cart = _normalize_cart(get_cart(session))
    t_ids = _clean_topping_ids(topping_ids)
    key = _make_item_key(product_id, t_ids)
    qty = max(1, int(quantity))
    if key in cart:
        cart[key]["quantity"] += qty
    else:
        cart[key] = {
            "product_id": int(product_id),
            "quantity": qty,
            "topping_ids": t_ids,
        }
    session[CART_SESSION_KEY] = cart
    session.modified = True


def set_quantity(session, item_key, quantity):
    cart = _normalize_cart(get_cart(session))
    key = str(item_key)
    quantity = int(quantity)

    # Fallback match if key was provided as just product_id string
    if key not in cart:
        matching = [k for k, v in cart.items() if str(v["product_id"]) == key and not v["topping_ids"]]
        if matching:
            key = matching[0]

    if quantity <= 0:
        cart.pop(key, None)
    else:
        if key in cart:
            cart[key]["quantity"] = quantity
        else:
            try:
                pid = int(key.split(":")[0])
                cart[key] = {"product_id": pid, "quantity": quantity, "topping_ids": []}
            except ValueError:
                pass
    session[CART_SESSION_KEY] = cart
    session.modified = True


def remove_from_cart(session, item_key):
    cart = _normalize_cart(get_cart(session))
    key = str(item_key)
    if key in cart:
        cart.pop(key, None)
    else:
        matching = [k for k, v in cart.items() if str(v["product_id"]) == key and not v["topping_ids"]]
        if matching:
            cart.pop(matching[0], None)
        else:
            cart.pop(key, None)
    session[CART_SESSION_KEY] = cart
    session.modified = True


def clear_cart(session):
    session[CART_SESSION_KEY] = {}
    session.modified = True


def cart_count(session):
    cart = _normalize_cart(get_cart(session))
    return sum(it["quantity"] for it in cart.values())


def cart_contents(session):
    """Resolve the session cart into product rows + totals; caps quantities to current stock."""
    cart = _normalize_cart(get_cart(session))
    if not cart:
        return [], 0, []

    p_ids = list({it["product_id"] for it in cart.values()})
    products = {p.id: p for p in Product.objects.filter(id__in=p_ids)}

    all_t_ids = set()
    for it in cart.values():
        all_t_ids.update(it["topping_ids"])
    toppings_map = {t.id: t for t in Topping.objects.filter(id__in=all_t_ids)}

    raw, warnings = [], []
    for item_key, item_data in cart.items():
        pid = item_data["product_id"]
        qty = item_data["quantity"]
        t_ids = item_data["topping_ids"]

        p = products.get(pid)
        if not p:
            warnings.append("A product in your cart is no longer available and was removed.")
            continue

        capped = min(qty, p.stock_quantity)
        if capped != qty:
            warnings.append(f"Only {p.stock_quantity} of {p.name} available; quantity adjusted.")

        # Resolve selected toppings
        selected_toppings = [toppings_map[tid] for tid in t_ids if tid in toppings_map]
        toppings_price_sum = sum(Decimal(str(t.price)) for t in selected_toppings)
        unit_price = Decimal(str(p.price)) + toppings_price_sum

        toppings_data = [
            {"id": t.id, "name": t.name, "price": float(t.price)}
            for t in selected_toppings
        ]
        toppings_text = ", ".join(t.name for t in selected_toppings)

        if capped > 0:
            raw.append({
                "item_key": item_key,
                "product": p,
                "quantity": capped,
                "base_price": float(p.price),
                "price": float(unit_price),
                "toppings": toppings_data,
                "toppings_text": toppings_text,
                "selected_toppings_objs": selected_toppings,
            })
    enriched, total = calc.cart_totals(raw)
    return enriched, total, warnings


def cart_summary(session):
    """Return a serializable dictionary of the cart contents for API/AJAX responses."""
    items, total, warnings = cart_contents(session)
    formatted_items = []
    for it in items:
        p = it["product"]
        formatted_items.append({
            "item_key": it["item_key"],
            "product_id": p.id,
            "name": p.name,
            "category": p.category or "Uncategorized",
            "base_price": float(it["base_price"]),
            "price": float(it["price"]),
            "quantity": it["quantity"],
            "subtotal": float(it["subtotal"]),
            "stock_quantity": p.stock_quantity,
            "image_url": p.image.url if getattr(p, "image", None) else None,
            "toppings": it["toppings"],
            "toppings_text": it["toppings_text"],
        })
    return {
        "items": formatted_items,
        "count": sum(it["quantity"] for it in items),
        "total": float(total),
        "warnings": warnings,
    }


def checkout(user, session, order_type="dine_in", customer_name="Walk-in Guest", table_number="", payment_method="cash"):
    """Validate stock, create Order and OrderItems (with OrderItemTopping records), decrement stock,
    and mirror each line into SalesRecord."""
    enriched, total, warnings = cart_contents(session)
    if not enriched:
        raise ValueError("Your cart is empty.")
    today = timezone.localdate()
    customer_user = user if (user and getattr(user, "is_authenticated", False)) else None
    display_name = customer_name.strip() if customer_name and customer_name.strip() else "Walk-in Guest"

    with transaction.atomic():
        order = Order.objects.create(
            customer=customer_user,
            customer_name=display_name,
            order_type=order_type or "dine_in",
            table_number=(table_number or "").strip(),
            payment_method=payment_method or "cash",
            total_amount=Decimal(str(round(total, 2))),
        )
        for row in enriched:
            product = Product.objects.get(pk=row["product"].pk)  # re-fetch: stock may have changed
            qty, price = row["quantity"], Decimal(str(row["price"]))
            if product.stock_quantity < qty:
                raise ValueError(f"Not enough stock for {product.name} (only {product.stock_quantity} left). Please update your cart.")
            product.stock_quantity -= qty
            product.save(update_fields=["stock_quantity", "updated_at"])

            # Decrement topping inventory if tracked
            for t_obj_info in row.get("selected_toppings_objs", []):
                top_obj = Topping.objects.get(pk=t_obj_info.pk)
                if top_obj.stock_quantity > 0:
                    top_obj.stock_quantity = max(0, top_obj.stock_quantity - qty)
                    top_obj.save(update_fields=["stock_quantity", "updated_at"])

            record = SalesRecord.objects.create(
                product=product,
                sale_date=today,
                quantity_sold=qty,
                price=price,
                total_amount=Decimal(str(round(qty * float(price), 2))),
                source_file="Walk-in order",
            )
            order_item = OrderItem.objects.create(order=order, product=product, quantity=qty, price=price, sales_record=record)

            for t_obj_info in row.get("selected_toppings_objs", []):
                OrderItemTopping.objects.create(
                    order_item=order_item,
                    topping=t_obj_info,
                    topping_name=t_obj_info.name,
                    price=t_obj_info.price,
                )

    clear_cart(session)
    return order, warnings

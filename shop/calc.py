"""Pure cart maths (no Django imports): line subtotals and the cart total."""


def cart_totals(items):
    """items: iterable of {'quantity': int, 'price': number, ...}. Returns (items with 'subtotal' added, grand_total)."""
    enriched, total = [], 0
    for it in items:
        sub = it["quantity"] * it["price"]
        enriched.append({**it, "subtotal": sub})
        total += sub
    return enriched, total

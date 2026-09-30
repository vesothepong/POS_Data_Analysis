from django.db.models import Q

from forecasting.services import latest_forecasts

from . import calc
from .models import Product


def inventory_rows(status=None, query=None):
    """One row per product: stock, latest forecast, reorder quantity and inventory status."""
    products = Product.objects.all().order_by("name")
    if query:
        products = products.filter(Q(name__icontains=query) | Q(category__icontains=query))
    forecasts = latest_forecasts()
    rows = []
    for p in products:
        f = forecasts.get(p.id)
        predicted = f.predicted_quantity if f else None
        st = calc.inventory_status(p.stock_quantity, p.reorder_level, predicted)
        rows.append({"product": p, "stock": p.stock_quantity, "reorder_level": p.reorder_level, "predicted": predicted,
                     "forecast_month": f.forecast_month if f else None, "reorder_qty": calc.reorder_quantity(p.stock_quantity, predicted),
                     "status": st, "badge": calc.STATUS_BADGES[st]})
    if status:
        rows = [r for r in rows if r["status"] == status]
    return rows

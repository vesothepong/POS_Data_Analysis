from django.db import transaction

from analytics import calc as agg
from products.models import Product
from sales.models import SalesRecord
from sales.services import sales_dataframe

from . import calc
from .models import Forecast


def product_series(product_id):
    """Monthly units series for one product."""
    return agg.monthly_series(sales_dataframe(SalesRecord.objects.filter(product_id=product_id)))


def forecast_product(product):
    """Train Linear Regression on the product's monthly sales and save next month's forecast."""
    s = product_series(product.id)
    result = calc.forecast_series(s)
    ev = calc.evaluate_series(s)
    next_month = result["next_month"].date()
    with transaction.atomic():
        Forecast.objects.filter(product=product, forecast_month=next_month).delete()
        forecast = Forecast.objects.create(product=product, forecast_month=next_month, predicted_quantity=result["predicted"],
                                           mae=ev["mae"] if ev else None)
    return forecast, s, result


def forecast_all():
    """Forecast every product that has enough history. Returns (done, skipped_names)."""
    done, skipped = [], []
    for p in Product.objects.order_by("name"):
        try:
            done.append(forecast_product(p)[0])
        except ValueError:
            skipped.append(p.name)
    return done, skipped


def latest_forecasts():
    """{product_id: most recent Forecast}."""
    latest = {}
    for f in Forecast.objects.select_related("product").order_by("product_id", "-forecast_month", "-created_at"):
        latest.setdefault(f.product_id, f)
    return latest


def accuracy_summary():
    """Hold-out evaluation for every product with at least 4 months of history."""
    df = sales_dataframe()
    out, skipped = [], []
    for p in Product.objects.order_by("name"):
        ev = calc.evaluate_series(agg.monthly_series(df[df["product_id"] == p.id]))
        if ev:
            out.append({"product_id": p.id, "product": p.name, **ev})
        else:
            skipped.append(p.name)
    return out, skipped

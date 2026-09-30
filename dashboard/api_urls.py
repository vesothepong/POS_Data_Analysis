from django.db.models import Sum
from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response

from products import calc as inv
from products.models import Product
from products.services import inventory_rows
from sales.models import SalesRecord


@api_view(["GET"])
def dashboard_api(request):
    agg = SalesRecord.objects.aggregate(units=Sum("quantity_sold"), revenue=Sum("total_amount"))
    rows = inventory_rows()
    return Response({
        "total_products": Product.objects.count(),
        "total_sales": agg["units"] or 0,
        "revenue": float(agg["revenue"] or 0),
        "current_inventory": sum(r["stock"] for r in rows),
        "predicted_demand": sum(r["predicted"] for r in rows if r["predicted"] is not None),
        "low_stock": sum(r["status"] in (inv.STATUS_LOW, inv.STATUS_OUT) for r in rows),
        "need_reorder": sum(r["reorder_qty"] > 0 for r in rows),
        "forecasts": [{"product": r["product"].name, "month": r["forecast_month"], "predicted_quantity": r["predicted"], "stock": r["stock"],
                       "reorder_quantity": r["reorder_qty"], "status": r["status"]} for r in rows if r["predicted"] is not None],
    })


urlpatterns = [path("dashboard/", dashboard_api, name="api_dashboard")]

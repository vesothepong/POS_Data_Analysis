from django.http import Http404
from django.shortcuts import render

from accounts.permissions import admin_required
from analytics import calc as agg
from products import calc as inv
from products.services import inventory_rows
from sales.models import UploadRecord
from sales.services import sales_dataframe
from shop.models import Order

from . import reports as report_lib


@admin_required
def dashboard(request):
    df = sales_dataframe()
    rows = inventory_rows()
    ctx = {
        "total_products": len(rows),
        "total_sales": int(df["units"].sum()) if len(df) else 0,
        "revenue": float(df["revenue"].sum()) if len(df) else 0,
        "current_inventory": sum(r["stock"] for r in rows),
        "predicted_demand": sum(r["predicted"] for r in rows if r["predicted"] is not None),
        "low_stock": sum(r["status"] in (inv.STATUS_LOW, inv.STATUS_OUT) for r in rows),
        "need_reorder": sum(r["reorder_qty"] > 0 for r in rows),
        "attention": [r for r in rows if r["status"] != inv.STATUS_OK][:8],
        "chart": {
            "monthly": agg.monthly_totals(df),
            "forecast": [{"product": r["product"].name, "stock": r["stock"], "predicted": r["predicted"]} for r in rows if r["predicted"] is not None],
        },
    }
    return render(request, "dashboard/dashboard.html", ctx)


@admin_required
def reports(request):
    kind = request.GET.get("type", "sales")
    if kind not in report_lib.REPORT_TITLES:
        raise Http404("Unknown report")
    cols, rows = report_lib.build(kind)
    return render(request, "dashboard/reports.html", {"kind": kind, "titles": report_lib.REPORT_TITLES, "title": report_lib.REPORT_TITLES[kind],
                                                       "columns": cols, "rows": rows[:300], "total_rows": len(rows),
                                                       "uploads": UploadRecord.objects.order_by("-uploaded_at")[:10]})


@admin_required
def report_export(request, kind, fmt):
    if kind not in report_lib.REPORT_TITLES or fmt not in ("csv", "xlsx"):
        raise Http404("Unknown report or format")
    return report_lib.export(kind, fmt)


@admin_required
def customer_orders(request):
    """All storefront orders, newest first: shows the admin exactly what customers bought."""
    orders = Order.objects.select_related("customer").prefetch_related("items__product")
    return render(request, "dashboard/orders.html", {"orders": orders, "count": orders.count()})

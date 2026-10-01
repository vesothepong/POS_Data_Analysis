from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.dateparse import parse_date

from accounts.permissions import admin_required
from analytics import calc as agg
from products.models import Product

from .forms import SalesUploadForm
from .models import SalesRecord, UploadRecord
from .services import import_xlsx, sales_dataframe


def _parse_day(value):
    try:
        return parse_date(value) if value else None
    except ValueError:
        return None


@admin_required
def sales(request):
    g = request.GET
    f = {k: g.get(k, "").strip() for k in ("product", "category", "date_from", "date_to", "month", "year")}
    qs = SalesRecord.objects.select_related("product").order_by("-sale_date", "-id")
    if f["product"].isdigit():
        qs = qs.filter(product_id=int(f["product"]))
    if f["category"]:
        qs = qs.filter(product__category=f["category"]) if f["category"] != "Uncategorized" else qs.filter(product__category="")
    if _parse_day(f["date_from"]):
        qs = qs.filter(sale_date__gte=_parse_day(f["date_from"]))
    if _parse_day(f["date_to"]):
        qs = qs.filter(sale_date__lte=_parse_day(f["date_to"]))
    if f["month"]:  # <input type="month"> sends YYYY-MM
        try:
            y, m = f["month"].split("-")
            qs = qs.filter(sale_date__year=int(y), sale_date__month=int(m))
        except ValueError:
            messages.warning(request, "Month filter ignored: use YYYY-MM.")
    if f["year"].isdigit():
        qs = qs.filter(sale_date__year=int(f["year"]))

    df = sales_dataframe(qs)  # sales analysis on exactly the filtered records
    ctx = {
        "sales": qs[:500], "count": qs.count(), "filters": f,
        "products": Product.objects.order_by("name"),
        "categories": sorted({c or "Uncategorized" for c in Product.objects.values_list("category", flat=True)}),
        "total_units": int(df["units"].sum()) if len(df) else 0,
        "total_revenue": float(df["revenue"].sum()) if len(df) else 0,
        "by_month": agg.monthly_totals(df, ascending=False), "by_product": agg.group_totals(df, "product"),
        "by_category": agg.group_totals(df, "category"),
    }
    ctx["best_sellers"] = ctx["by_product"][:5]
    return render(request, "sales/list.html", ctx)


@admin_required
def upload_sales(request):
    form = SalesUploadForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        try:
            upload = import_xlsx(form.cleaned_data["file"])
            messages.success(request, upload.message)
            return redirect("sales")
        except ValueError as e:
            messages.error(request, str(e))
    return render(request, "sales/upload.html", {"form": form, "uploads": UploadRecord.objects.order_by("-uploaded_at")[:5]})

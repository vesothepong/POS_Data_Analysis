from django.contrib import messages
from django.shortcuts import get_object_or_404, render

from accounts.permissions import admin_required
from products import calc as inv
from products.models import Product

from .services import accuracy_summary, forecast_all, forecast_product


@admin_required
def forecast_page(request):
    ctx = {"products": Product.objects.order_by("name"), "selected": None, "forecast": None, "results": None}
    if request.method == "POST":
        if request.POST.get("product") == "all":
            done, skipped = forecast_all()
            done_results = []
            for f in done:
                st = inv.inventory_status(f.product.stock_quantity, f.product.reorder_level, f.predicted_quantity)
                done_results.append({
                    "forecast": f,
                    "reorder": inv.reorder_quantity(f.product.stock_quantity, f.predicted_quantity),
                    "status": st,
                    "badge": inv.STATUS_BADGES.get(st, "text-bg-secondary"),
                })
            ctx["results"] = done_results
            messages.success(request, f"Forecasts generated for {len(done)} products.")
            if skipped:
                messages.warning(request, "Skipped (need at least 2 months of sales): " + ", ".join(skipped))
        else:
            selected = get_object_or_404(Product, pk=request.POST.get("product"))
            ctx["selected"] = selected
            try:
                forecast, s, result = forecast_product(selected)
                ctx.update(
                    forecast=forecast,
                    reorder=inv.reorder_quantity(selected.stock_quantity, forecast.predicted_quantity),
                    status=inv.inventory_status(selected.stock_quantity, selected.reorder_level, forecast.predicted_quantity),
                    chart={"history": [{"month": i.strftime("%Y-%m"), "actual": int(v)} for i, v in s.items()],
                           "fitted": result["fitted"], "next_month": forecast.forecast_month.strftime("%Y-%m"), "predicted": forecast.predicted_quantity},
                )
                messages.success(request, f"Forecast generated: {forecast.predicted_quantity} units for {forecast.forecast_month:%B %Y}.")
            except ValueError as e:
                messages.error(request, str(e))
    return render(request, "forecasting/forecast.html", ctx)


@admin_required
def accuracy(request):
    results, skipped = accuracy_summary()
    selected = request.GET.get("product", "")
    detail = next((r for r in results if str(r["product_id"]) == selected), results[0] if results else None)

    def avg(key):
        return round(sum(r[key] for r in results) / len(results), 2) if results else None

    scored = [r["accuracy"] for r in results if r["accuracy"] is not None]
    overall = {"mae": avg("mae"), "baseline": avg("baseline_mae"), "accuracy": round(sum(scored) / len(scored), 1) if scored else None}
    return render(request, "forecasting/accuracy.html", {"results": results, "skipped": skipped, "detail": detail, "overall": overall})

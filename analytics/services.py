from forecasting import calc as fc
from products.models import Product
from sales.services import sales_dataframe

from . import calc


def analytics_payload(product_id=None):
    """Everything the Data Analytics charts & statistical tables need, as plain JSON-able data."""
    df = sales_dataframe()
    all_products = list(Product.objects.order_by("name"))

    abc = calc.abc_analysis(df)
    stats_list = calc.statistical_profiling(df, all_products)
    corr = calc.correlation_analysis(df)

    total_units = int(df["units"].sum()) if len(df) else 0
    total_rev = round(float(df["revenue"].sum()), 2) if len(df) else 0.0

    monthly_data = calc.monthly_totals(df)
    growth = calc.sales_growth_analysis(monthly_data)

    payload = {
        "monthly": monthly_data,
        "products": calc.group_totals(df, "product"),
        "categories": calc.group_totals(df, "category"),
        "abc": abc,
        "statistical_profiles": stats_list,
        "correlation": corr,
        "sales_growth": growth,
        "kpis": {
            "total_units": total_units,
            "total_revenue": total_rev,
            "product_count": len(all_products),
            "class_a_count": abc["summary"].get("count_a", 0),
        },
    }
    payload["top_products"] = payload["products"][:5]
    payload["selected"] = None

    if product_id:
        product = Product.objects.filter(pk=product_id).first()
        if product:
            s = calc.monthly_series(df[df["product_id"] == product.id])
            profile = next((st for st in stats_list if st["product_id"] == product.id), None)
            sel = {
                "id": product.id,
                "product": product.name,
                "category": product.category or "Uncategorized",
                "price": float(product.price),
                "stock_quantity": product.stock_quantity,
                "reorder_level": product.reorder_level,
                "image_url": product.image_url,
                "profile": profile,
                "history": [{"month": i.strftime("%Y-%m"), "actual": int(v)} for i, v in s.items()],
                "forecast": None,
            }
            if len(s) >= 2:
                r = fc.forecast_series(s)
                sel["forecast"] = {
                    "month": r["next_month"].strftime("%Y-%m"),
                    "predicted": r["predicted"],
                    "fitted": r["fitted"],
                    "slope": r.get("slope"),
                    "intercept": r.get("intercept"),
                    "formula": r.get("formula"),
                    "r2": r.get("r2"),
                    "std_err": r.get("std_err"),
                    "ci_lower": r.get("ci_lower"),
                    "ci_upper": r.get("ci_upper"),
                }
            payload["selected"] = sel
    return payload


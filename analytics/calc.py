"""Pure aggregation helpers (pandas only, no Django): sales DataFrame -> monthly / product / category totals."""
import pandas as pd


def monthly_series(df):
    """Units per calendar month (month-start index). Months with no sales become 0."""
    if df is None or len(df) == 0:
        return pd.Series(dtype=float)
    return df.set_index("sale_date")["units"].resample("MS").sum().astype(float)


def monthly_totals(df):
    if df is None or len(df) == 0:
        return []
    g = df.groupby("month").agg(units=("units", "sum"), revenue=("revenue", "sum")).reset_index().sort_values("month")
    return [{"month": r.month.strftime("%Y-%m"), "units": int(r.units), "revenue": round(float(r.revenue), 2)} for r in g.itertuples()]


def group_totals(df, column):
    """Units and revenue grouped by 'product' or 'category', best seller first."""
    if df is None or len(df) == 0:
        return []
    g = df.groupby(column).agg(units=("units", "sum"), revenue=("revenue", "sum")).reset_index().sort_values(["units", column], ascending=[False, True])
    return [{"name": str(getattr(r, column)), "units": int(r.units), "revenue": round(float(r.revenue), 2)} for r in g.itertuples()]


def abc_analysis(df):
    """ABC Inventory Analysis based on the Pareto Principle (80/20 rule).
    Class A: Top ~70% cumulative revenue (High business impact).
    Class B: Next ~20% cumulative revenue (Moderate impact).
    Class C: Bottom ~10% cumulative revenue (Low impact / long tail).
    """
    if df is None or len(df) == 0:
        return {"items": [], "chart": {"labels": [], "revenue": [], "cum_pct": []}, "summary": {"a": 0, "b": 0, "c": 0}}

    g = df.groupby("product").agg(units=("units", "sum"), revenue=("revenue", "sum")).reset_index()
    g = g.sort_values("revenue", ascending=False).reset_index(drop=True)
    total_rev = float(g["revenue"].sum())
    if total_rev <= 0:
        return {"items": [], "chart": {"labels": [], "revenue": [], "cum_pct": []}, "summary": {"a": 0, "b": 0, "c": 0}}

    running_rev = 0.0
    items = []
    labels, revenues, cum_pcts = [], [], []
    count_a, count_b, count_c = 0, 0, 0

    for r in g.itertuples():
        rev = float(r.revenue)
        running_rev += rev
        cum_pct = round((running_rev / total_rev) * 100, 1)
        pct_rev = round((rev / total_rev) * 100, 1)

        # ABC threshold assignment
        if cum_pct <= 70.0 or (len(items) == 0 and cum_pct > 70.0):
            abc_class = "A"
            badge = "badge-danger"
            count_a += 1
        elif cum_pct <= 90.0 or count_a == len(items):
            abc_class = "B"
            badge = "badge-warning"
            count_b += 1
        else:
            abc_class = "C"
            badge = "badge-secondary"
            count_c += 1

        items.append({
            "product": r.product,
            "revenue": round(rev, 2),
            "units": int(r.units),
            "pct_revenue": pct_rev,
            "cumulative_pct": cum_pct,
            "abc_class": abc_class,
            "badge": badge,
        })
        labels.append(r.product)
        revenues.append(round(rev, 2))
        cum_pcts.append(cum_pct)

    return {
        "items": items,
        "chart": {"labels": labels, "revenue": revenues, "cum_pct": cum_pcts},
        "summary": {
            "total_revenue": round(total_rev, 2),
            "count_a": count_a,
            "count_b": count_b,
            "count_c": count_c,
        },
    }


def statistical_profiling(df, products):
    """Computes descriptive statistics (Mean, Std Dev, Variance, Skewness, CV)
    and prescriptive supply chain metrics (EOQ, Safety Stock, ROP, Turnover)
    for each product.
    """
    if df is None or len(df) == 0:
        return []

    # Map ABC class
    abc = {it["product"]: it for it in abc_analysis(df).get("items", [])}
    results = []

    for p in products:
        pdf = df[df["product_id"] == p.id]
        if pdf.empty:
            continue

        s = monthly_series(pdf)
        vals = s.values
        n = len(vals)
        if n == 0:
            continue

        mean = float(vals.mean())
        median = float(pd.Series(vals).median())
        std_dev = float(vals.std(ddof=1)) if n > 1 else 0.0
        variance = float(vals.var(ddof=1)) if n > 1 else 0.0
        skewness = float(pd.Series(vals).skew()) if n > 2 else 0.0
        cv = round(std_dev / mean, 2) if mean > 0 else 0.0

        # Demand pattern classification
        if cv < 0.25:
            volatility = "Stable"
            volatility_badge = "bg-success"
        elif cv <= 0.50:
            volatility = "Moderate"
            volatility_badge = "bg-info text-dark"
        else:
            volatility = "Erratic"
            volatility_badge = "bg-warning text-dark"

        # Prescriptive supply-chain formulas
        price = float(p.price)
        annual_demand = mean * 12
        holding_cost = max(1.0, price * 0.20)  # 20% annual holding cost benchmark
        order_setup_cost = 25.0                 # Standard order transaction cost
        
        # Economic Order Quantity: sqrt(2 * D * S / H)
        eoq = int(round(((2 * annual_demand * order_setup_cost) / holding_cost) ** 0.5)) if holding_cost > 0 else 0
        
        # Safety Stock for 95% service level (Z = 1.65) assuming 1 month supplier lead time
        safety_stock = int(round(1.65 * std_dev))
        recommended_rop = int(round(mean + safety_stock))
        
        # Stock Turnover = Annual Demand / max(Current Stock, 1)
        stock_qty = p.stock_quantity
        turnover = round(annual_demand / max(stock_qty, 1), 2)
        dsi = round(365 / max(turnover, 0.1), 1)

        abc_info = abc.get(p.name, {})

        results.append({
            "product_id": p.id,
            "product_name": p.name,
            "category": p.category or "Uncategorized",
            "price": price,
            "stock_quantity": stock_qty,
            "reorder_level": p.reorder_level,
            "image_url": p.image_url,
            "active_months": n,
            "total_units": int(vals.sum()),
            "total_revenue": round(float(pdf["revenue"].sum()), 2),
            "mean": round(mean, 1),
            "median": round(median, 1),
            "std_dev": round(std_dev, 2),
            "variance": round(variance, 2),
            "skewness": round(skewness, 2) if not pd.isna(skewness) else 0.0,
            "min": int(vals.min()),
            "max": int(vals.max()),
            "cv": cv,
            "volatility": volatility,
            "volatility_badge": volatility_badge,
            "abc_class": abc_info.get("abc_class", "C"),
            "pct_revenue": abc_info.get("pct_revenue", 0.0),
            "eoq": eoq,
            "safety_stock": safety_stock,
            "recommended_rop": recommended_rop,
            "turnover": turnover,
            "dsi": dsi,
        })

    return sorted(results, key=lambda x: x["total_revenue"], reverse=True)


def correlation_analysis(df):
    """Calculates Pearson correlation between Unit Price and Monthly Quantity Sold."""
    if df is None or len(df) < 3:
        return {"correlation": 0.0, "elasticity": "Insufficient data"}
    try:
        r = float(df["price"].corr(df["units"]))
        r = round(r, 3)
        if pd.isna(r):
            return {"correlation": 0.0, "elasticity": "Neutral"}
        if r < -0.3:
            elasticity = "Price Sensitive (Elastic: Higher price reduces volume)"
        elif r > 0.3:
            elasticity = "Inelastic / Premium demand pattern"
        else:
            elasticity = "Relatively Inelastic / Stable across prices"
        return {"correlation": r, "elasticity": elasticity}
    except Exception:
        return {"correlation": 0.0, "elasticity": "Neutral"}

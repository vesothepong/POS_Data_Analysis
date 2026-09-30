import io
from decimal import Decimal

import pandas as pd
from django.db import transaction

from products.models import Product

from .cleaning import clean_sales_frame
from .models import SalesRecord, UploadRecord

BATCH = 1000


def _text(v):
    return "" if pd.isna(v) else str(v)


def _key(name, day, qty, price):
    return (name, day, int(qty), round(float(price), 2))


def import_xlsx(uploaded_file):
    """Upload flow: read -> validate columns -> clean -> drop duplicates -> store -> log."""
    try:
        raw = pd.read_excel(io.BytesIO(uploaded_file.read()), engine="openpyxl")
    except Exception:
        raise ValueError("The file could not be read. Please upload a valid .xlsx workbook.")
    good, rejected, dup_in_file = clean_sales_frame(raw)  # raises ValueError for missing columns

    sample = "; ".join(f"row {r}: {why}" for r, why in rejected[:5])
    if rejected and len(rejected) > 5:
        sample += f"; ... and {len(rejected) - 5} more"

    dup_in_db = 0
    if len(good):
        names = list(good["Product"].unique())
        existing = set(
            (n, d, q, round(float(p), 2))
            for n, d, q, p in SalesRecord.objects.filter(product__name__in=names)
            .values_list("product__name", "sale_date", "quantity_sold", "price")
        )
        keep = [_key(r.Product, r.Date.date(), r.Qty, r.Price) not in existing
                for r in good.rename(columns={"Quantity Sold": "Qty"}).itertuples()]
        dup_in_db = len(good) - sum(keep)
        good = good[keep]

    if not len(good):
        msg = "No new valid rows to import."
        if rejected:
            msg += f" {len(rejected)} invalid ({sample})."
        if dup_in_file or dup_in_db:
            msg += f" {dup_in_file + dup_in_db} duplicate rows skipped."
        UploadRecord.objects.create(file_name=uploaded_file.name, rows_processed=0, rows_rejected=len(rejected), status="Rejected", message=msg)
        raise ValueError(msg)

    with transaction.atomic():
        names = list(good["Product"].unique())
        products = {p.name: p for p in Product.objects.filter(name__in=names)}
        latest = good.sort_values("Date").groupby("Product").last()  # newest row per product
        new = [Product(name=n, category=_text(latest.loc[n, "Category"]), price=Decimal(str(latest.loc[n, "Price"])),
                       stock_quantity=int(latest.loc[n, "Stock Quantity"]) if pd.notna(latest.loc[n, "Stock Quantity"]) else 0)
               for n in names if n not in products]
        Product.objects.bulk_create(new)
        products = {p.name: p for p in Product.objects.filter(name__in=names)}  # re-query: bulk_create may not return pks (MySQL)

        for n in names:  # fill blank category / apply stock from the file if provided
            p, row, changed = products[n], latest.loc[n], False
            if not p.category and _text(row["Category"]):
                p.category, changed = _text(row["Category"]), True
            if pd.notna(row["Stock Quantity"]) and p.stock_quantity != int(row["Stock Quantity"]):
                p.stock_quantity, changed = max(0, int(row["Stock Quantity"])), True
            if changed:
                p.save()

        records = [
            SalesRecord(product=products[r.Product], sale_date=r.Date.date(), quantity_sold=int(r.Qty), price=Decimal(str(r.Price)),
                        total_amount=Decimal(str(round(int(r.Qty) * float(r.Price), 2))), source_file=uploaded_file.name)
            for r in good.rename(columns={"Quantity Sold": "Qty"}).itertuples()
        ]
        SalesRecord.objects.bulk_create(records, batch_size=BATCH)

        msg = f"Imported {len(records)} clean rows."
        if rejected:
            msg += f" Rejected {len(rejected)} invalid rows ({sample})."
        if dup_in_file or dup_in_db:
            msg += f" Skipped {dup_in_file} duplicate rows in the file and {dup_in_db} already in the database."
        upload = UploadRecord.objects.create(file_name=uploaded_file.name, rows_processed=len(records),
                                             rows_rejected=len(rejected), status="Completed", message=msg)
    return upload


SALES_COLUMNS = ["sale_date", "units", "revenue", "product_id", "product", "category", "month"]


def sales_dataframe(qs=None):
    """Load sales records (optionally a filtered queryset) into a DataFrame for analysis."""
    qs = SalesRecord.objects.all() if qs is None else qs
    rows = list(qs.values("sale_date", "quantity_sold", "total_amount", "product_id", "product__name", "product__category"))
    if not rows:
        return pd.DataFrame(columns=SALES_COLUMNS)
    df = pd.DataFrame(rows).rename(columns={"quantity_sold": "units", "total_amount": "revenue",
                                             "product__name": "product", "product__category": "category"})
    df["sale_date"] = pd.to_datetime(df["sale_date"])
    df["revenue"] = df["revenue"].astype(float)
    df["category"] = df["category"].replace("", "Uncategorized").fillna("Uncategorized")
    df["month"] = df["sale_date"].dt.to_period("M").dt.to_timestamp()
    return df

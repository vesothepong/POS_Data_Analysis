"""Pure cleaning / validation of an uploaded sales sheet (pandas only)."""
import pandas as pd

REQUIRED = ["Date", "Product", "Quantity Sold", "Price"]
ALIASES = {
    "date": "Date", "product": "Product", "quantity sold": "Quantity Sold", "quantity_sold": "Quantity Sold",
    "price": "Price", "category": "Category", "stock quantity": "Stock Quantity", "stock_quantity": "Stock Quantity",
}


def normalize_columns(df):
    rename = {}
    for col in df.columns:
        key = str(col).strip().lower()
        if key in ALIASES:
            rename[col] = ALIASES[key]
    return df.rename(columns=rename)


def clean_sales_frame(raw):
    """Validate and clean a raw sheet.

    Returns (clean_df, rejected, dup_in_file):
      clean_df    - valid, de-duplicated rows with normalised types
      rejected    - list of (excelrow_no_number, reason) for invalid rows
      dup_in_file - number of exact duplicate rows removed
    Raises ValueError when required columns are missing.
    """
    df = normalize_columns(raw).dropna(how="all").copy()
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing) + ". Required: " + ", ".join(REQUIRED) + ".")
    df["row_no"] = df.index + 2  # row number as seen in Excel (row 1 is the header)
    product_missing = df["Product"].isna() | df["Product"].astype(str).str.strip().eq("")
    df["Product"] = df["Product"].astype(str).str.strip()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.normalize()
    df["Quantity Sold"] = pd.to_numeric(df["Quantity Sold"], errors="coerce")
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
    if "Category" not in df:
        df["Category"] = ""
    df["Category"] = df["Category"].astype("string").str.strip().replace("", pd.NA).astype(object).where(lambda c: c.notna(), float("nan"))
    if "Stock Quantity" not in df:
        df["Stock Quantity"] = float("nan")
    else:
        df["Stock Quantity"] = pd.to_numeric(df["Stock Quantity"], errors="coerce")

    df["reason"] = ""

    def mark(mask, msg):
        df.loc[mask & (df["reason"] == ""), "reason"] = msg

    mark(df["Date"].isna(), "invalid or missing date")
    mark(product_missing, "missing product name")
    mark(df["Quantity Sold"].isna(), "invalid or missing quantity")
    mark(df["Quantity Sold"] < 0, "negative quantity")
    mark(df["Price"].isna(), "invalid or missing price")
    mark(df["Price"] < 0, "negative price")

    bad = df[df["reason"] != ""]
    rejected = [(int(r.row_no), r.reason) for r in bad.itertuples()]
    good = df[df["reason"] == ""].copy()
    before = len(good)
    good = good.drop_duplicates(subset=["Date", "Product", "Quantity Sold", "Price"])
    dup_in_file = before - len(good)
    good["Quantity Sold"] = good["Quantity Sold"].round().astype(int)
    good["Price"] = good["Price"].round(2)
    return good.reset_index(drop=True), rejected, dup_in_file

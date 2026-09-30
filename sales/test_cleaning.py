import io
import unittest
import pandas as pd
from .cleaning import clean_sales_frame


def sheet(rows, cols=("Date", "Product", "Quantity Sold", "Price")):
    buf = io.BytesIO()
    pd.DataFrame(rows, columns=list(cols)).to_excel(buf, index=False)
    buf.seek(0)
    return pd.read_excel(buf, engine="openpyxl")


class CleaningTests(unittest.TestCase):
    def test_clean_reject_and_dedupe(self):
        raw = sheet([
            ["2025-01-05", "T-Shirt", 10, 9.5],
            ["2025-01-05", "T-Shirt", 10, 9.5],      # exact duplicate
            ["not a date", "Jeans", 3, 20],           # bad date
            ["2025-01-06", "", 3, 20],                # missing product
            ["2025-01-07", "Shoes", -4, 40],          # negative quantity
            ["2025-01-08", "Shoes", 4, None],         # missing price
            ["2025-02-01", " Jacket ", 2, 55],        # whitespace trimmed
        ])
        good, rejected, dups = clean_sales_frame(raw)
        self.assertEqual(len(good), 2)
        self.assertEqual(dups, 1)
        self.assertEqual(len(rejected), 4)
        self.assertEqual(rejected[0], (4, "invalid or missing date"))  # excel row 4
        self.assertIn("Jacket", set(good["Product"]))

    def test_missing_columns(self):
        with self.assertRaisesRegex(ValueError, "Missing required columns: Price"):
            clean_sales_frame(sheet([["2025-01-01", "A", 1]], cols=("Date", "Product", "Quantity Sold")))

    def test_column_aliases_and_optional_columns(self):
        raw = sheet([["2025-01-01", "A", 1, 2.0, "Cat", 30]],
                    cols=("date", "PRODUCT", "quantity_sold", "price", "category", "stock_quantity"))
        good, rejected, _ = clean_sales_frame(raw)
        self.assertEqual(rejected, [])
        self.assertEqual(good.loc[0, "Category"], "Cat")
        self.assertEqual(good.loc[0, "Stock Quantity"], 30)


if __name__ == "__main__":
    unittest.main()

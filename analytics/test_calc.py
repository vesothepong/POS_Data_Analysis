import unittest

import pandas as pd

from . import calc


class AggregationTests(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            "sale_date": pd.to_datetime(["2025-01-05", "2025-01-20", "2025-02-03"]),
            "units": [10, 5, 7], "revenue": [100.0, 50.0, 70.0],
            "product": ["A", "B", "A"], "category": ["X", "X", "Y"],
        })
        self.df["month"] = self.df["sale_date"].dt.to_period("M").dt.to_timestamp()

    def test_monthly_totals(self):
        self.assertEqual(calc.monthly_totals(self.df)[0], {"month": "2025-01", "units": 15, "revenue": 150.0})

    def test_group_totals_best_first(self):
        self.assertEqual(calc.group_totals(self.df, "product")[0]["name"], "A")

    def test_monthly_series_and_empty(self):
        self.assertEqual(calc.monthly_series(self.df).tolist(), [15.0, 7.0])
        self.assertEqual(calc.group_totals(None, "product"), [])
        self.assertEqual(calc.monthly_totals(None), [])

    def test_gap_months_become_zero(self):
        df = pd.DataFrame({"sale_date": pd.to_datetime(["2025-01-05", "2025-04-05"]), "units": [1, 2]})
        self.assertEqual(calc.monthly_series(df).tolist(), [1.0, 0.0, 0.0, 2.0])

    def test_abc_analysis(self):
        res = calc.abc_analysis(self.df)
        self.assertEqual(len(res["items"]), 2)
        self.assertEqual(res["items"][0]["product"], "A")
        self.assertEqual(res["items"][0]["abc_class"], "A")
        self.assertIn("chart", res)
        self.assertEqual(res["summary"]["count_a"] + res["summary"]["count_b"] + res["summary"]["count_c"], 2)

    def test_correlation_analysis(self):
        df = pd.DataFrame({"price": [10.0, 20.0, 30.0], "units": [100, 50, 20]})
        c = calc.correlation_analysis(df)
        self.assertLess(c["correlation"], 0)
        self.assertIn("Elastic", c["elasticity"])
        self.assertEqual(c["simple_status"], "Price Sensitive")

    def test_sales_growth_analysis(self):
        # Growing (> +5%)
        m_grow = [{"month": "2025-01", "revenue": 100.0}, {"month": "2025-02", "revenue": 120.0}]
        res = calc.sales_growth_analysis(m_grow)
        self.assertEqual(res["status"], "Growing")
        self.assertEqual(res["trend"], "up")
        self.assertEqual(res["pct_change"], 20.0)

        # Declining (< -5%)
        m_dec = [{"month": "2025-01", "revenue": 100.0}, {"month": "2025-02", "revenue": 80.0}]
        res_dec = calc.sales_growth_analysis(m_dec)
        self.assertEqual(res_dec["status"], "Declining")
        self.assertEqual(res_dec["trend"], "down")
        self.assertEqual(res_dec["pct_change"], -20.0)

        # Steady (-5% to +5%)
        m_steady = [{"month": "2025-01", "revenue": 100.0}, {"month": "2025-02", "revenue": 102.0}]
        res_steady = calc.sales_growth_analysis(m_steady)
        self.assertEqual(res_steady["status"], "Steady")
        self.assertEqual(res_steady["trend"], "stable")
        self.assertEqual(res_steady["pct_change"], 2.0)

        # Edge cases: 0 or 1 month
        self.assertEqual(calc.sales_growth_analysis([])["status"], "Steady")
        self.assertEqual(calc.sales_growth_analysis([{"month": "2025-01", "revenue": 100.0}])["status"], "Steady")


if __name__ == "__main__":
    unittest.main()

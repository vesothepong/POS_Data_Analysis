import unittest

import pandas as pd

from . import calc


def series(values, start="2025-01-01"):
    return pd.Series(values, index=pd.date_range(start, periods=len(values), freq="MS"), dtype=float)


class ForecastMathTests(unittest.TestCase):
    def test_forecast_follows_trend(self):
        r = calc.forecast_series(series([100, 120, 130, 150, 160]))
        self.assertEqual(r["predicted"], 177)  # least-squares line; the 170 in the brief is a rounded illustration
        self.assertEqual(r["next_month"], pd.Timestamp("2025-06-01"))
        self.assertGreater(r["slope"], 0)
        self.assertIn("r2", r)
        self.assertGreater(r["r2"], 0.9)
        self.assertIn("formula", r)
        self.assertIn("ci_lower", r)
        self.assertIn("ci_upper", r)

    def test_forecast_needs_two_months(self):
        with self.assertRaises(ValueError):
            calc.forecast_series(series([10]))

    def test_forecast_never_negative(self):
        self.assertEqual(calc.forecast_series(series([50, 30, 10, 2]))["predicted"], 0)

    def test_evaluate_needs_four_months(self):
        self.assertIsNone(calc.evaluate_series(series([1, 2, 3])))

    def test_evaluate_linear_data_is_near_perfect(self):
        ev = calc.evaluate_series(series([10 * i for i in range(1, 11)]))
        self.assertAlmostEqual(ev["mae"], 0, places=6)
        self.assertGreater(ev["baseline_mae"], ev["mae"])  # regression beats the plain average
        self.assertEqual(ev["train_months"] + ev["test_months"], 10)

    def test_evaluate_rows(self):
        ev = calc.evaluate_series(series([100, 120, 130, 150, 160]))
        self.assertEqual(ev["test_months"], 1)
        self.assertEqual(ev["rows"][0]["actual"], 160)


if __name__ == "__main__":
    unittest.main()

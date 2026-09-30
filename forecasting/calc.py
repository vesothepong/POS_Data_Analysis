"""Pure forecasting maths: Linear Regression forecast + hold-out accuracy (no Django imports)."""
import numpy as np
import pandas as pd

try:
    from sklearn.linear_model import LinearRegression
    ENGINE = "scikit-learn"
except ImportError:  # e.g. Windows Application Control blocks scikit-learn's compiled DLLs
    ENGINE = "NumPy least squares"

    class LinearRegression:
        """Minimal drop-in for sklearn's LinearRegression (ordinary least squares, one feature)."""

        def fit(self, x, y):
            slope, intercept = np.polyfit(np.asarray(x, dtype=float).ravel(), np.asarray(y, dtype=float), 1)
            self.coef_ = np.array([slope])
            self.intercept_ = float(intercept)
            return self

        def predict(self, x):
            return np.asarray(x, dtype=float).ravel() * self.coef_[0] + self.intercept_


def forecast_series(s):
    """Fit Linear Regression (month index -> units) and predict the next month."""
    n = len(s)
    if n < 2:
        raise ValueError("At least 2 months of sales history are required for forecasting.")
    x = np.arange(1, n + 1).reshape(-1, 1)
    y = s.values.astype(float)
    model = LinearRegression().fit(x, y)
    raw_pred = float(model.predict(np.array([[n + 1]]))[0])
    predicted = max(0, int(round(raw_pred)))
    fitted_vals = np.asarray(model.predict(x), dtype=float).ravel()
    residuals = y - fitted_vals
    ss_res = float(np.sum(residuals ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = max(0.0, min(1.0, float(1.0 - (ss_res / ss_tot)))) if ss_tot > 0 else 1.0
    se = float(np.sqrt(ss_res / max(1, n - 2))) if n > 2 else float(np.std(residuals))
    ci_margin = float(1.96 * se)
    ci_lower = max(0, int(round(raw_pred - ci_margin)))
    ci_upper = max(0, int(round(raw_pred + ci_margin)))
    slope = float(model.coef_[0])
    intercept = float(model.intercept_)
    sign = "+" if intercept >= 0 else "-"
    formula = f"y = {slope:.2f}x {sign} {abs(intercept):.2f}"
    return {
        "predicted": predicted,
        "next_month": s.index[-1] + pd.offsets.MonthBegin(1),
        "fitted": [round(float(v), 1) for v in fitted_vals],
        "slope": slope,
        "intercept": round(intercept, 2),
        "formula": formula,
        "r2": round(r2, 3),
        "std_err": round(se, 2),
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
    }


def evaluate_series(s, test_ratio=0.2):
    """Hold-out evaluation: train on the early months, predict the last ones.

    Returns None if there is not enough history (needs >= 4 months: 3 to train, 1 to test).
    Also reports a naive baseline (predict the training average) so it is clear
    that the regression is doing more than calculating an average.
    """
    n = len(s)
    if n < 4:
        return None
    test_size = min(max(1, int(round(n * test_ratio))), n - 3)
    train_n = n - test_size
    x = np.arange(1, n + 1).reshape(-1, 1)
    y = s.values.astype(float)
    model = LinearRegression().fit(x[:train_n], y[:train_n])
    pred = np.clip(model.predict(x[train_n:]), 0, None)
    actual = y[train_n:]
    err = actual - pred
    baseline = np.full(len(actual), y[:train_n].mean())
    nonzero = actual != 0
    mape = float(np.mean(np.abs(err[nonzero] / actual[nonzero])) * 100) if nonzero.any() else None
    rows = [
        {"month": s.index[train_n + i].strftime("%Y-%m"), "actual": int(actual[i]),
         "predicted": int(round(pred[i])), "difference": int(round(actual[i] - pred[i]))}
        for i in range(len(actual))
    ]
    return {
        "train_months": train_n,
        "test_months": test_size,
        "mae": float(np.mean(np.abs(err))),
        "rmse": float(np.sqrt(np.mean(err ** 2))),
        "mape": mape,
        "accuracy": None if mape is None else max(0.0, 100.0 - mape),
        "baseline_mae": float(np.mean(np.abs(actual - baseline))),
        "rows": rows,
    }



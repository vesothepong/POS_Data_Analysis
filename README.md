# Food & Drink Inventory Demand Forecasting & Data Analytics Dashboard

Django data-analytics project designed for inventory demand forecasting: upload historical sales (XLSX) or capture storefront orders, analyse demand distributions, forecast demand with **Ordinary Least Squares (OLS) Linear Regression**, conduct **ABC Pareto Inventory Analysis**, optimize stock with **Economic Order Quantity (EOQ)** and **Safety Stock**, and generate academic statistical reports and Excel/CSV exports.

## Domain & Demo Catalog
The system is tailored for a **Food & Beverage (Café & Fresh Food)** business model (Artisan Coffee, Match Latte, Croissants, Burgers, Fresh Juice, Pastries), where demand forecasting, shelf-life freshness, and safety stock buffers are critical.

## Stack
Django 5 + Django REST Framework, Bootstrap 5 + Chart.js, Pandas / NumPy / scikit-learn, OpenPyXL,
SQLite for development (MySQL via `.env`).

## Quick start (Windows PowerShell)
```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py seed_demo          # demo data + demo admin (admin / admin12345) if no user exists
python manage.py runserver
```
Open http://127.0.0.1:8000/ . To use your own admin instead: `python manage.py createsuperuser`
(any user with `is_staff` is an admin). **Change the demo password.**

MySQL: install the server and the `mysqlclient` prerequisites, set `DB_ENGINE=mysql` and the DB values in `.env`,
create the database, then run `python manage.py migrate`.

## Run the tests
```powershell
python manage.py test            # Django tests + pure pandas/scikit-learn tests
python -m unittest forecasting.test_calc products.test_calc analytics.test_calc sales.test_cleaning   # maths only, no database
```

## Roles
- **Admin** (`is_staff`): dashboard, products, sales, inventory, forecasting, analytics, reports, and Walk-in Customer Orders. Created with `createsuperuser` or `seed_demo`.
- **Walk-in Customer / Guest**: streamlined walk-in ordering kiosk — direct access without login, Dine In / Takeaway options, payment method selection (Cash, Card, QR), live POS order ticket, digital thermal receipt generation, and recent ticket history.

Unauthenticated visitors land directly on the Walk-in Kiosk (`/shop/`), while logged-in admins go straight to their Dashboard. Placing a walk-in order immediately creates a `SalesRecord` for each line, so **Sales Data, Data Analytics, and Demand Forecast update live in real-time from walk-in purchases**, with no manual upload required. The XLSX upload remains available for bulk/historical data.

`python manage.py seed_demo` creates both a demo admin and a demo customer:
| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin12345` |
| Customer | `customer` | `customer12345` |

## Pages
| Page | What it does |
|---|---|
| Dashboard | 7 KPIs (products, units sold, revenue, inventory, predicted demand, low stock, need reorder), sales trend, stock vs forecast, products needing attention |
| Products | Search, add, edit, delete with **product image upload & live preview** |
| Sales Data | Filter by product, category, date range, month, year; totals, best sellers, category and monthly sales |
| Upload XLSX | Validate columns, clean, reject invalid rows (with row numbers), skip duplicates (also on re-upload), upload log |
| Inventory | Stock list with thumbnails, inline stock update, status filter, per-product detail with sales history |
| Demand Forecast | Forecast one product or all products; chart with actual, trend line and forecast |
| Data Analytics | **Comprehensive Statistical Suite**: Monthly trends, ABC Pareto analysis (80/20 rule), descriptive stats (Mean, Std Dev, Variance, Skewness, CV), prescriptive optimization (EOQ, Safety Stock, ROP), and product OLS regression ($y = mx + b$, $R^2$, 95% CI) |
| Forecast Accuracy | Train/test split, MAE / RMSE / MAPE, comparison with a plain-average baseline |
| Walk-in POS Kiosk (`/shop/`) | Modern split-screen POS for walk-in counter ordering with category pills, live sticky order ticket, Dine-In/Takeaway, payment selector, and digital thermal receipt |
| Reports | Sales, Inventory, ABC & Statistical Inventory, Product Performance, Demand Forecast, Reorder, Revenue; export to Excel (.xlsx) or CSV |
| Walk-in Customer Orders (admin) | Every walk-in order, newest first, displaying ticket number, dining option, table #, guest name, payment method, and line breakdown |

## Business rules
- Forecast: monthly units per product, x = month number, y = units; predicts the next month (needs >= 2 months).
- Reorder quantity = predicted demand - current stock (never below 0).
- Status priority: **Out of Stock** (stock 0) > **Low Stock** (below reorder level) > **Need Reorder** (below forecast) > **Sufficient Stock**.
- Accuracy needs >= 4 months (3 to train, at least 1 to test; test set is about the last 20%).
- Access: every page and the API require an admin (`is_staff`); other logged-in users get a 403 page.

## XLSX format
Required: `Date`, `Product`, `Quantity Sold`, `Price`. Optional: `Category`, `Stock Quantity`
(if given, it overwrites the product's current stock with the newest value in the file).

## Project structure (one Django app per feature)
```
inventory_forecasting/
  manage.py  requirements.txt  .env.example  sample_data/ (two test XLSX files)
  config/        settings, root urls
  accounts/      login/logout, admin_required permission, (403 page in templates/)
  products/      Product model, CRUD, inventory pages, stock-status rules (calc.py, services.py)
  sales/         SalesRecord + UploadRecord, XLSX upload, cleaning.py, sales filters/analysis
  forecasting/   Forecast model, Linear Regression + accuracy (calc.py), forecast/accuracy pages
  analytics/     aggregation maths (calc.py), chart data service, /api/analytics/
  dashboard/     dashboard, six reports + Excel/CSV export, /api/dashboard/, seed_demo command
  templates/     base.html + one folder per app      static/   css, js
```
Each app follows the same pattern: `models.py`, `views.py`, `urls.py`, `services.py` (database + pandas), `calc.py`
(pure maths, unit-testable without Django), `tests.py`.
Flow: view -> service -> pandas -> Linear Regression -> database.

## Known limitations
- Months with no sales are treated as 0 units, and the current, partly finished month counts as a full month.
- Linear Regression captures a straight-line trend only; it does not model seasonality.
- `products.services` imports `forecasting.services` (stock status needs the latest forecast); nothing imports the other way round.

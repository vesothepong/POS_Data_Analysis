from django.urls import path

from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("orders/", views.customer_orders, name="customer_orders"),
    path("reports/", views.reports, name="reports"),
    path("reports/export/<slug:kind>/<slug:fmt>/", views.report_export, name="report_export"),
]

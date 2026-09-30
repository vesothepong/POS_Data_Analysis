from django.urls import path

from . import views

urlpatterns = [
    path("sales/", views.sales, name="sales"),
    path("sales/upload/", views.upload_sales, name="upload_sales"),
]

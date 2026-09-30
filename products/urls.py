from django.urls import path

from . import views

urlpatterns = [
    path("products/", views.products, name="products"),
    path("products/add/", views.product_create, name="product_create"),
    path("products/<int:pk>/edit/", views.product_edit, name="product_edit"),
    path("products/<int:pk>/delete/", views.product_delete, name="product_delete"),
    path("inventory/", views.inventory, name="inventory"),
    path("inventory/<int:pk>/", views.inventory_detail, name="inventory_detail"),
    path("inventory/<int:pk>/update/", views.inventory_update, name="inventory_update"),
]

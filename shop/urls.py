from django.urls import path

from . import views

urlpatterns = [
    path("shop/", views.catalog, name="catalog"),
    path("shop/add/<int:pk>/", views.add_to_cart, name="add_to_cart"),
    path("shop/cart/", views.cart_view, name="cart"),
    path("shop/cart/clear/", views.clear_cart_view, name="cart_clear"),
    path("shop/checkout/", views.checkout_view, name="checkout"),
    path("shop/orders/", views.order_history, name="order_history"),
]

from django.urls import path

from . import views

urlpatterns = [
    path("forecast/", views.forecast_page, name="forecast"),
    path("accuracy/", views.accuracy, name="accuracy"),
]

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("accounts.urls")),
    path("", include("dashboard.urls")),
    path("", include("products.urls")),
    path("", include("sales.urls")),
    path("", include("forecasting.urls")),
    path("", include("analytics.urls")),
    path("", include("shop.urls")),
    path("api/", include("dashboard.api_urls")),
    path("api/", include("analytics.api_urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

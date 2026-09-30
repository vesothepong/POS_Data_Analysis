from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .services import analytics_payload


@api_view(["GET"])
def analytics_api(request):
    pid = request.query_params.get("product")
    return Response(analytics_payload(int(pid) if pid and pid.isdigit() else None))


urlpatterns = [path("analytics/", analytics_api, name="api_analytics")]

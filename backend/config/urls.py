"""
URL configuration for text-to-sql-platform project.
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    return Response({
        "status": "healthy",
        "service": "Text-to-SQL Platform Backend",
        "version": "1.0.0"
    })

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check, name="health-check"),
    path("api/auth/", include("accounts.urls")),
    path("api/organizations/", include("organizations.urls")),
    path("api/connections/", include("connections.urls")),
    path("api/schema/", include("schema_engine.urls")),
    path("api/query/", include("query_engine.urls")),
    path("api/history/", include("history.urls")),
]

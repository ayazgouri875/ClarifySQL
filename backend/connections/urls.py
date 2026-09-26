from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DatabaseConnectionViewSet

router = DefaultRouter()
router.register(r"", DatabaseConnectionViewSet, basename="connections")

urlpatterns = [
    path("", include(router.urls)),
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QueryHistoryViewSet

router = DefaultRouter()
router.register(r"", QueryHistoryViewSet, basename="history")

urlpatterns = [
    path("", include(router.urls)),
]

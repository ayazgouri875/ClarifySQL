from django.urls import path
from .views import ProcessQueryView, ExecuteQueryView, ExplainQueryView

urlpatterns = [
    path("process/", ProcessQueryView.as_view(), name="query-process"),
    path("execute/", ExecuteQueryView.as_view(), name="query-execute"),
    path("explain/", ExplainQueryView.as_view(), name="query-explain"),
]

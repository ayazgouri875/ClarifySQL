from django.urls import path
from .views import ConnectionSchemaView, TablePreviewView

urlpatterns = [
    path("<uuid:connection_id>/", ConnectionSchemaView.as_view(), name="schema-detail"),
    path("<uuid:connection_id>/tables/<str:table_name>/preview/", TablePreviewView.as_view(), name="schema-table-preview"),
]

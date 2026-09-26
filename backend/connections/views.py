from django.utils import timezone
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import DatabaseConnection
from .serializers import DatabaseConnectionSerializer
from .services import test_connection_params, decrypt_credential
from schema_engine.services import introspect_connection_schema

class DatabaseConnectionViewSet(viewsets.ModelViewSet):
    serializer_class = DatabaseConnectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.organization:
            return DatabaseConnection.objects.none()
        return DatabaseConnection.objects.filter(organization=user.organization)

    def perform_create(self, serializer):
        conn = serializer.save(organization=self.request.user.organization)
        # Attempt immediate background schema sync on creation
        try:
            schema_data = introspect_connection_schema(conn)
            conn.schema_cache = schema_data
            conn.last_synced_at = timezone.now()
            conn.save(update_fields=["schema_cache", "last_synced_at"])
        except Exception:
            pass

    @action(detail=False, methods=["post"], url_path="test")
    def test_raw_connection(self, request):
        db_type = request.data.get("db_type", "sqlite")
        database_name = request.data.get("database_name", "")
        host = request.data.get("host", "localhost")
        port = int(request.data.get("port", 5432) or 5432)
        username = request.data.get("username", "")
        password = request.data.get("password", "")
        ssl_enabled = bool(request.data.get("ssl_enabled", False))

        if not database_name:
            return Response({"success": False, "error": "database_name is required"}, status=status.HTTP_400_BAD_REQUEST)

        ok, msg = test_connection_params(
            db_type=db_type,
            database_name=database_name,
            host=host,
            port=port,
            username=username,
            password=password,
            ssl_enabled=ssl_enabled
        )
        return Response({"success": ok, "message": msg})

    @action(detail=True, methods=["post"], url_path="test-existing")
    def test_existing_connection(self, request, pk=None):
        conn = self.get_object()
        password = decrypt_credential(conn.encrypted_password)
        ok, msg = test_connection_params(
            db_type=conn.db_type,
            database_name=conn.database_name,
            host=conn.host,
            port=conn.port,
            username=conn.username,
            password=password,
            ssl_enabled=conn.ssl_enabled
        )
        return Response({"success": ok, "message": msg})

    @action(detail=True, methods=["post"], url_path="sync-schema")
    def sync_schema(self, request, pk=None):
        conn = self.get_object()
        try:
            schema_data = introspect_connection_schema(conn)
            conn.schema_cache = schema_data
            conn.last_synced_at = timezone.now()
            conn.save(update_fields=["schema_cache", "last_synced_at"])
            return Response({
                "success": True,
                "message": f"Successfully synced {len(schema_data.get('tables', {}))} tables",
                "tables_count": len(schema_data.get("tables", {})),
                "last_synced_at": conn.last_synced_at
            })
        except Exception as exc:
            return Response({"success": False, "error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

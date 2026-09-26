from rest_framework import status, views, permissions
from rest_framework.response import Response
from connections.models import DatabaseConnection
from .services import introspect_connection_schema, get_table_preview

class ConnectionSchemaView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, connection_id):
        try:
            conn = DatabaseConnection.objects.get(
                id=connection_id,
                organization=request.user.organization
            )
        except DatabaseConnection.DoesNotExist:
            return Response({"error": "Connection not found"}, status=status.HTTP_404_NOT_FOUND)

        if not conn.schema_cache:
            try:
                schema_data = introspect_connection_schema(conn)
                conn.schema_cache = schema_data
                conn.save(update_fields=["schema_cache"])
            except Exception as exc:
                return Response({"error": f"Failed to introspect schema: {exc}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "connection_id": str(conn.id),
            "connection_name": conn.name,
            "db_type": conn.db_type,
            "last_synced_at": conn.last_synced_at,
            "schema": conn.schema_cache
        })

class TablePreviewView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, connection_id, table_name):
        try:
            conn = DatabaseConnection.objects.get(
                id=connection_id,
                organization=request.user.organization
            )
        except DatabaseConnection.DoesNotExist:
            return Response({"error": "Connection not found"}, status=status.HTTP_404_NOT_FOUND)

        limit = int(request.query_params.get("limit", 10))
        try:
            data = get_table_preview(conn, table_name, limit=limit)
            return Response({
                "table_name": table_name,
                "columns": data.get("columns", []),
                "rows": data.get("rows", []),
                "row_count": len(data.get("rows", []))
            })
        except Exception as exc:
            return Response({"error": f"Failed to fetch preview: {exc}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

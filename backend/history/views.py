from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Count
from .models import QueryHistoryItem
from .serializers import QueryHistorySerializer
from connections.models import DatabaseConnection

class QueryHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = QueryHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.organization:
            return QueryHistoryItem.objects.none()

        qs = QueryHistoryItem.objects.filter(organization=user.organization)

        # Filters
        conn_id = self.request.query_params.get("connection_id")
        if conn_id:
            qs = qs.filter(connection_id=conn_id)

        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)

        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(natural_query__icontains=search)

        return qs

    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        user = request.user
        if not user.organization:
            return Response({
                "total_queries": 0,
                "successful_queries": 0,
                "failed_queries": 0,
                "clarified_queries": 0,
                "avg_execution_time_ms": 0.0,
                "connections_count": 0
            })

        qs = QueryHistoryItem.objects.filter(organization=user.organization)
        total = qs.count()
        success = qs.filter(status="success").count()
        failed = qs.filter(status="error").count()
        clarified = qs.filter(clarification_log__isnull=False).count()
        avg_time = qs.filter(status="success").aggregate(Avg("execution_time_ms"))["execution_time_ms__avg"] or 0.0
        connections_count = DatabaseConnection.objects.filter(organization=user.organization).count()

        return Response({
            "total_queries": total,
            "successful_queries": success,
            "failed_queries": failed,
            "clarified_queries": clarified,
            "avg_execution_time_ms": round(avg_time, 2),
            "connections_count": connections_count
        })

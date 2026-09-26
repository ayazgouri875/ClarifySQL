from rest_framework import serializers
from .models import QueryHistoryItem

class QueryHistorySerializer(serializers.ModelSerializer):
    connection_name = serializers.CharField(source="connection.name", read_only=True, default="Unknown Connection")
    user_name = serializers.CharField(source="user.name", read_only=True, default="Anonymous")

    class Meta:
        model = QueryHistoryItem
        fields = [
            "id",
            "connection",
            "connection_name",
            "user",
            "user_name",
            "natural_query",
            "generated_sql",
            "status",
            "execution_time_ms",
            "row_count",
            "error_message",
            "clarification_log",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

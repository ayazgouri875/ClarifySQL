from rest_framework import serializers
from .models import DatabaseConnection
from .services import encrypt_credential

class DatabaseConnectionSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    table_count = serializers.SerializerMethodField()

    class Meta:
        model = DatabaseConnection
        fields = [
            "id",
            "name",
            "db_type",
            "host",
            "port",
            "database_name",
            "username",
            "password",
            "ssl_enabled",
            "schema_cache",
            "last_synced_at",
            "is_active",
            "table_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "schema_cache", "last_synced_at", "created_at", "updated_at"]

    def get_table_count(self, obj):
        if obj.schema_cache and isinstance(obj.schema_cache, dict):
            return len(obj.schema_cache.get("tables", {}))
        return 0

    def create(self, validated_data):
        password = validated_data.pop("password", "")
        if password:
            validated_data["encrypted_password"] = encrypt_credential(password)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        if password is not None and password != "":
            instance.encrypted_password = encrypt_credential(password)
        return super().update(instance, validated_data)

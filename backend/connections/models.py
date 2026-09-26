import uuid
from django.db import models

class DatabaseConnection(models.Model):
    DB_TYPE_CHOICES = (
        ("sqlite", "SQLite"),
        ("postgresql", "PostgreSQL"),
        ("mysql", "MySQL"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "organizations.Organization",
        related_name="connections",
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    db_type = models.CharField(max_length=20, choices=DB_TYPE_CHOICES)
    host = models.CharField(max_length=255, blank=True, default="localhost")
    port = models.IntegerField(default=5432)
    database_name = models.CharField(max_length=255)
    username = models.CharField(max_length=100, blank=True, default="")
    encrypted_password = models.TextField(blank=True, default="")
    ssl_enabled = models.BooleanField(default=False)
    schema_cache = models.JSONField(null=True, blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "database_connections"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.db_type}) - Org: {self.organization.name}"

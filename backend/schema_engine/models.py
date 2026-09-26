import uuid
from django.db import models

class SchemaMetadata(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    connection = models.OneToOneField(
        "connections.DatabaseConnection",
        related_name="schema_metadata",
        on_delete=models.CASCADE
    )
    raw_schema = models.JSONField(default=dict)
    table_count = models.IntegerField(default=0)
    synced_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "schema_metadata"

    def __str__(self):
        return f"Schema for {self.connection.name} ({self.table_count} tables)"

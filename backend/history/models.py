import uuid
from django.db import models

class QueryHistoryItem(models.Model):
    STATUS_CHOICES = (
        ("success", "Success"),
        ("error", "Error"),
        ("clarified", "Clarified"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "organizations.Organization",
        related_name="query_history",
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        "accounts.User",
        related_name="queries",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    connection = models.ForeignKey(
        "connections.DatabaseConnection",
        related_name="queries",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    natural_query = models.TextField()
    generated_sql = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="success")
    execution_time_ms = models.FloatField(default=0.0)
    row_count = models.IntegerField(default=0)
    error_message = models.TextField(null=True, blank=True)
    clarification_log = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "query_history"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.status.upper()}] {self.natural_query[:50]} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

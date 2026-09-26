from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from organizations.models import Organization
from connections.models import DatabaseConnection
from connections.services import encrypt_credential
from schema_engine.services import introspect_connection_schema
from history.models import QueryHistoryItem

User = get_user_model()

class Command(BaseCommand):
    help = "Seeds demo organization, user, sample database connection, and query history."

    def handle(self, *args, **options):
        # 1. Create or get Demo Organization
        org, _ = Organization.objects.get_or_create(
            name="Acme Global Analytics",
            defaults={"slug": "acme-global"}
        )

        # 2. Create or get Demo User
        user, created = User.objects.get_or_create(
            email="demo@example.com",
            defaults={
                "name": "Ayaz Gouri",
                "organization": org,
                "role": "owner"
            }
        )
        if created:
            user.set_password("Password123!")
            user.save()
            self.stdout.write(self.style.SUCCESS("Created demo user: demo@example.com / Password123!"))
        else:
            self.stdout.write(self.style.NOTICE("Demo user demo@example.com already exists."))

        # 3. Create or get Retail & Analytics SQLite Connection
        conn, conn_created = DatabaseConnection.objects.get_or_create(
            organization=org,
            name="Enterprise Retail DB (SQLite)",
            defaults={
                "db_type": "sqlite",
                "database_name": "company.db",
                "host": "localhost",
                "port": 0,
                "username": "",
                "encrypted_password": "",
                "ssl_enabled": False,
                "is_active": True
            }
        )

        # Introspect schema
        try:
            schema_data = introspect_connection_schema(conn)
            conn.schema_cache = schema_data
            conn.last_synced_at = timezone.now()
            conn.save(update_fields=["schema_cache", "last_synced_at"])
            self.stdout.write(self.style.SUCCESS(f"Introspected {len(schema_data.get('tables', {}))} tables for {conn.name}"))
        except Exception as exc:
            self.stdout.write(self.style.WARNING(f"Schema introspection warning: {exc}"))

        # 4. Seed sample query history if empty
        if QueryHistoryItem.objects.filter(organization=org).count() == 0:
            QueryHistoryItem.objects.create(
                organization=org,
                user=user,
                connection=conn,
                natural_query="Who are our best customers recently?",
                generated_sql="SELECT c.id, c.name, SUM(o.total_amount) AS total_spent, COUNT(o.id) AS order_count FROM customers c JOIN orders o ON c.id = o.customer_id GROUP BY c.id, c.name ORDER BY total_spent DESC LIMIT 10;",
                status="success",
                execution_time_ms=12.4,
                row_count=10,
                clarification_log={
                    "term": "best customers",
                    "selected": "Highest total spending (SUM of orders)",
                    "category": "metric"
                }
            )
            QueryHistoryItem.objects.create(
                organization=org,
                user=user,
                connection=conn,
                natural_query="Show sales breakdown by category",
                generated_sql="SELECT p.category, SUM(oi.quantity * oi.unit_price) AS category_revenue FROM products p JOIN order_items oi ON p.id = oi.product_id GROUP BY p.category ORDER BY category_revenue DESC LIMIT 20;",
                status="success",
                execution_time_ms=9.8,
                row_count=4,
                clarification_log=None
            )
            self.stdout.write(self.style.SUCCESS("Created sample query history entries."))

        self.stdout.write(self.style.SUCCESS("Demo seeding completed successfully!"))

from typing import Dict, Any
from connections.services import get_engine_for_connection
from ai.parser import format_schema_for_llm
from .introspector import DatabaseIntrospector
from .models import SchemaMetadata

def introspect_connection_schema(connection) -> Dict[str, Any]:
    """Introspects and caches schema for a given DatabaseConnection model instance."""
    engine = get_engine_for_connection(connection)
    try:
        schema_dict = DatabaseIntrospector.introspect(engine)
        
        # Save or update SchemaMetadata record
        SchemaMetadata.objects.update_or_create(
            connection=connection,
            defaults={
                "raw_schema": schema_dict,
                "table_count": len(schema_dict.get("tables", {}))
            }
        )
        return schema_dict
    finally:
        engine.dispose()

def get_table_preview(connection, table_name: str, limit: int = 5) -> Dict[str, Any]:
    """Fetches sample preview rows from the connection's database."""
    engine = get_engine_for_connection(connection)
    try:
        return DatabaseIntrospector.get_sample_rows(engine, table_name, limit=limit)
    finally:
        engine.dispose()

def get_schema_for_llm(connection) -> str:
    """Returns formatted schema text ready for prompt injection."""
    if connection.schema_cache:
        return format_schema_for_llm(connection.schema_cache)
        
    try:
        schema_data = introspect_connection_schema(connection)
        connection.schema_cache = schema_data
        connection.save(update_fields=["schema_cache"])
        return format_schema_for_llm(schema_data)
    except Exception:
        return "No schema available."

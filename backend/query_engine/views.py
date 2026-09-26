from rest_framework import status, views, permissions
from rest_framework.response import Response
from django.conf import settings
from connections.models import DatabaseConnection
from schema_engine.services import get_schema_for_llm
from history.models import QueryHistoryItem
from ai.gemini_client import gemini_client
from ai.prompts import SQL_EXPLANATION_PROMPT
from .ambiguity import ambiguity_detector
from .clarification import clarification_resolver
from .sql_generator import sql_generator
from .sql_validator import sql_validator
from .executor import sql_executor

class ProcessQueryView(views.APIView):
    """
    Main Text-to-SQL Pipeline:
    1. Checks for business & semantic ambiguity
    2. If ambiguous and not yet clarified, returns clarification questions
    3. If clarified or unambiguous, generates verified SQL
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        connection_id = request.data.get("connection_id")
        question = request.data.get("question", "").strip()
        selected_option = request.data.get("selected_option")
        category = request.data.get("category")

        if not question:
            return Response({"error": "Question is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not connection_id:
            # Fallback to first active connection in organization
            conn = DatabaseConnection.objects.filter(
                organization=request.user.organization,
                is_active=True
            ).first()
            if not conn:
                return Response({"error": "No database connection available. Please create a connection first."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                conn = DatabaseConnection.objects.get(
                    id=connection_id,
                    organization=request.user.organization
                )
            except DatabaseConnection.DoesNotExist:
                return Response({"error": "Database connection not found."}, status=status.HTTP_404_NOT_FOUND)

        # 1. If user already supplied a clarified option, resolve it directly into SQL
        if selected_option:
            resolution = clarification_resolver.resolve(question, selected_option, category)
            sql = sql_generator.generate(
                question=question,
                dialect=conn.db_type,
                schema_dict=conn.schema_cache,
                resolved_specification=resolution.get("resolved_specification"),
                resolved_context=resolution.get("context")
            )
            is_valid, val_err = sql_validator.validate(sql)
            return Response({
                "status": "sql_generated",
                "is_ambiguous": False,
                "sql": sql,
                "is_valid": is_valid,
                "validation_error": val_err,
                "resolved_specification": resolution.get("resolved_specification"),
                "selected_option": selected_option,
                "connection_id": str(conn.id)
            })

        # 2. Check for Ambiguity
        schema_text = get_schema_for_llm(conn)
        ambiguity_result = ambiguity_detector.analyze(question, schema_text)

        if ambiguity_result.get("is_ambiguous"):
            return Response({
                "status": "clarification_needed",
                "is_ambiguous": True,
                "ambiguity": ambiguity_result,
                "connection_id": str(conn.id)
            })

        # 3. Completely Unambiguous: Generate direct SQL
        sql = sql_generator.generate(
            question=question,
            dialect=conn.db_type,
            schema_dict=conn.schema_cache
        )
        is_valid, val_err = sql_validator.validate(sql)

        return Response({
            "status": "sql_generated",
            "is_ambiguous": False,
            "sql": sql,
            "is_valid": is_valid,
            "validation_error": val_err,
            "connection_id": str(conn.id)
        })

class ExecuteQueryView(views.APIView):
    """Executes validated SQL against the target database and records query history."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        connection_id = request.data.get("connection_id")
        sql = request.data.get("sql", "").strip()
        question = request.data.get("question", "")
        clarification_log = request.data.get("clarification_log")

        if not sql:
            return Response({"error": "SQL query is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            conn = DatabaseConnection.objects.get(
                id=connection_id,
                organization=request.user.organization
            )
        except DatabaseConnection.DoesNotExist:
            return Response({"error": "Database connection not found."}, status=status.HTTP_404_NOT_FOUND)

        # Execute safe query
        exec_result = sql_executor.execute(conn, sql)

        # Log to query history
        history_item = QueryHistoryItem.objects.create(
            organization=request.user.organization,
            user=request.user,
            connection=conn,
            natural_query=question or "Direct SQL execution",
            generated_sql=exec_result.get("executed_sql", sql),
            status="success" if exec_result["success"] else "error",
            execution_time_ms=exec_result.get("execution_time_ms", 0.0),
            row_count=exec_result.get("row_count", 0),
            error_message=exec_result.get("error", None),
            clarification_log=clarification_log
        )

        return Response({
            **exec_result,
            "history_id": str(history_item.id)
        })

class ExplainQueryView(views.APIView):
    """Generates plain English explanation of generated SQL logic."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        question = request.data.get("question", "")
        sql = request.data.get("sql", "").strip()

        if not sql:
            return Response({"error": "SQL is required"}, status=status.HTTP_400_BAD_REQUEST)

        if gemini_client.is_available:
            prompt = SQL_EXPLANATION_PROMPT.format(question=question or "Custom SQL", sql=sql)
            explanation = gemini_client.generate_text(prompt, temperature=0.2)
            if explanation:
                return Response({"explanation": explanation})

        # Fallback heuristic explanation
        explanation = (
            f"• Reads records using read-only execution.\n"
            f"• Returns up to {getattr(settings, 'DEFAULT_QUERY_LIMIT', 50)} rows.\n"
            f"• Computes requested projections and aggregations directly."
        )
        return Response({"explanation": explanation})

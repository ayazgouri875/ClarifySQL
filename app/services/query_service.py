"""
Master Query Service Orchestrator with Multi-Tenant Support.
Coordinates Intent Extraction, Ambiguity Detection, Clarification Resolution,
Dynamic Schema SQL Generation, AST Security Validation, Isolated DB Execution,
and Tenant Query History Logging.
"""

import uuid
import json
from typing import Dict, Optional, Any
from sqlalchemy.orm import Session

from app.intent.models import (
    QueryRequest,
    QueryResponse,
    AmbiguityItem,
    SessionMemory,
    QueryResultData
)
from app.clarification.detector import ambiguity_detector
from app.clarification.resolver import clarification_resolver
from app.sql.generator import sql_generator
from app.sql.validator import sql_validator
from app.sql.executor import sql_executor
from app.services.explainer import result_explainer
from app.services.connection_service import connection_service
from app.database.models import DatabaseConnection, QueryHistoryItem

class QueryService:
    def __init__(self):
        self.sessions: Dict[str, SessionMemory] = {}

    def get_or_create_session(self, session_id: str = None, connection_id: str = None) -> SessionMemory:
        if not session_id or session_id not in self.sessions:
            new_id = session_id or str(uuid.uuid4())
            self.sessions[new_id] = SessionMemory(session_id=new_id, connection_id=connection_id)
            return self.sessions[new_id]
        if connection_id and not self.sessions[session_id].connection_id:
            self.sessions[session_id].connection_id = connection_id
        return self.sessions[session_id]

    def process_query(
        self,
        request: QueryRequest,
        organization_id: Optional[str] = None,
        user_id: Optional[str] = None,
        connection: Optional[DatabaseConnection] = None,
        db: Optional[Session] = None
    ) -> QueryResponse:
        session = self.get_or_create_session(request.session_id, request.connection_id)
        session_id = session.session_id

        # Determine active dynamic schema if tenant connection is provided
        dynamic_schema = None
        allowed_tables = None
        if connection:
            if connection.schema_cache:
                try:
                    dynamic_schema = json.loads(connection.schema_cache)
                except Exception:
                    dynamic_schema = connection_service.introspect_schema(connection)
            else:
                dynamic_schema = connection_service.introspect_schema(connection)
                if db:
                    connection.schema_cache = json.dumps(dynamic_schema)
                    db.commit()

            if dynamic_schema and "tables" in dynamic_schema:
                allowed_tables = set(dynamic_schema["tables"].keys())

        # Case 1: User replying to a clarification question
        if request.selected_clarification and session.pending_clarification:
            clarification = session.pending_clarification
            original_q = session.history[-1]["question"] if session.history else request.question
            
            # Step A: Resolve intent
            resolved_ctx = clarification_resolver.resolve(
                original_question=original_q,
                clarification=clarification,
                user_choice=request.selected_clarification
            )

            # Step B: Generate SQL (grounded in dynamic schema if provided)
            sql = sql_generator.generate(
                question=original_q,
                resolved_specification=resolved_ctx.get("resolved_instruction"),
                resolved_context=resolved_ctx,
                dynamic_schema=dynamic_schema
            )

            # Step C: Validate SQL
            is_valid, sanitized_sql, error_msg = sql_validator.validate_and_sanitize(sql, allowed_tables=allowed_tables)
            if not is_valid:
                self._record_history(
                    db=db,
                    org_id=organization_id,
                    u_id=user_id,
                    conn_id=connection.id if connection else None,
                    q=original_q,
                    clar_q=clarification.question,
                    clar_a=request.selected_clarification,
                    intent=resolved_ctx.get("resolved_instruction"),
                    sql=sql,
                    status="error",
                    error=error_msg
                )
                return QueryResponse(
                    status="error",
                    session_id=session_id,
                    question=original_q,
                    connection_id=connection.id if connection else None,
                    generated_sql=sql,
                    error_message=error_msg
                )

            # Step D: Execute SQL (tenant connection vs default demo)
            try:
                if connection:
                    cols, rows, exec_ms = connection_service.execute_query(connection, sanitized_sql)
                    result_data = QueryResultData(
                        columns=cols,
                        rows=rows,
                        row_count=len(rows),
                        execution_time_ms=exec_ms
                    )
                else:
                    success, result_data, sanitized_sql, error_msg = sql_executor.execute_safe_sql(sanitized_sql)
                    if not success:
                        raise RuntimeError(error_msg)
            except Exception as e:
                clean_err = f"Execution failed: {str(e)}"
                self._record_history(
                    db=db,
                    org_id=organization_id,
                    u_id=user_id,
                    conn_id=connection.id if connection else None,
                    q=original_q,
                    clar_q=clarification.question,
                    clar_a=request.selected_clarification,
                    intent=resolved_ctx.get("resolved_instruction"),
                    sql=sanitized_sql,
                    status="error",
                    error=clean_err
                )
                return QueryResponse(
                    status="error",
                    session_id=session_id,
                    question=original_q,
                    connection_id=connection.id if connection else None,
                    generated_sql=sanitized_sql,
                    error_message=clean_err
                )

            # Step E: Natural Language Explanation
            explanation = result_explainer.explain(
                question=original_q,
                sql=sanitized_sql,
                columns=result_data.columns,
                rows=result_data.rows
            )

            # Clear pending clarification and update session
            session.pending_clarification = None
            session.history.append({
                "question": original_q,
                "clarification_answered": request.selected_clarification,
                "sql": sanitized_sql,
                "row_count": result_data.row_count
            })

            # Record in Tenant Query History
            self._record_history(
                db=db,
                org_id=organization_id,
                u_id=user_id,
                conn_id=connection.id if connection else None,
                q=original_q,
                clar_q=clarification.question,
                clar_a=request.selected_clarification,
                intent=resolved_ctx.get("resolved_instruction"),
                sql=sanitized_sql,
                status="success",
                rows=result_data.row_count,
                ms=result_data.execution_time_ms
            )

            return QueryResponse(
                status="success",
                session_id=session_id,
                question=original_q,
                connection_id=connection.id if connection else None,
                generated_sql=sanitized_sql,
                validated=True,
                data=result_data,
                explanation=explanation
            )

        # Case 2: New incoming question
        question = request.question.strip()
        
        # Step 1: Ambiguity Detection
        ambiguity = ambiguity_detector.analyze(question)
        if ambiguity:
            session.pending_clarification = ambiguity
            session.history.append({
                "question": question,
                "ambiguity_detected": ambiguity.model_dump()
            })
            self._record_history(
                db=db,
                org_id=organization_id,
                u_id=user_id,
                conn_id=connection.id if connection else None,
                q=question,
                clar_q=ambiguity.question,
                status="clarification_required"
            )
            return QueryResponse(
                status="clarification_required",
                session_id=session_id,
                question=question,
                connection_id=connection.id if connection else None,
                clarification=ambiguity
            )

        # Step 2: Clear Query -> Direct SQL Generation
        sql = sql_generator.generate(question=question, dynamic_schema=dynamic_schema)

        # Step 3: Validate SQL
        is_valid, sanitized_sql, error_msg = sql_validator.validate_and_sanitize(sql, allowed_tables=allowed_tables)
        if not is_valid:
            self._record_history(
                db=db,
                org_id=organization_id,
                u_id=user_id,
                conn_id=connection.id if connection else None,
                q=question,
                sql=sql,
                status="error",
                error=error_msg
            )
            return QueryResponse(
                status="error",
                session_id=session_id,
                question=question,
                connection_id=connection.id if connection else None,
                generated_sql=sql,
                error_message=error_msg
            )

        # Step 4: Execute SQL
        try:
            if connection:
                cols, rows, exec_ms = connection_service.execute_query(connection, sanitized_sql)
                result_data = QueryResultData(
                    columns=cols,
                    rows=rows,
                    row_count=len(rows),
                    execution_time_ms=exec_ms
                )
            else:
                success, result_data, sanitized_sql, error_msg = sql_executor.execute_safe_sql(sanitized_sql)
                if not success:
                    raise RuntimeError(error_msg)
        except Exception as e:
            clean_err = f"Execution failed: {str(e)}"
            self._record_history(
                db=db,
                org_id=organization_id,
                u_id=user_id,
                conn_id=connection.id if connection else None,
                q=question,
                sql=sanitized_sql,
                status="error",
                error=clean_err
            )
            return QueryResponse(
                status="error",
                session_id=session_id,
                question=question,
                connection_id=connection.id if connection else None,
                generated_sql=sanitized_sql,
                error_message=clean_err
            )

        # Step 5: Natural Language Explanation
        explanation = result_explainer.explain(
            question=question,
            sql=sanitized_sql,
            columns=result_data.columns,
            rows=result_data.rows
        )

        session.history.append({
            "question": question,
            "sql": sanitized_sql,
            "row_count": result_data.row_count
        })

        self._record_history(
            db=db,
            org_id=organization_id,
            u_id=user_id,
            conn_id=connection.id if connection else None,
            q=question,
            sql=sanitized_sql,
            status="success",
            rows=result_data.row_count,
            ms=result_data.execution_time_ms
        )

        return QueryResponse(
            status="success",
            session_id=session_id,
            question=question,
            connection_id=connection.id if connection else None,
            generated_sql=sanitized_sql,
            validated=True,
            data=result_data,
            explanation=explanation
        )

    def _record_history(
        self,
        db: Optional[Session],
        org_id: Optional[str],
        u_id: Optional[str],
        conn_id: Optional[str],
        q: str,
        clar_q: Optional[str] = None,
        clar_a: Optional[str] = None,
        intent: Optional[str] = None,
        sql: Optional[str] = None,
        status: str = "success",
        rows: int = 0,
        ms: float = 0.0,
        error: Optional[str] = None
    ):
        """Helper to securely save an isolated tenant query audit record."""
        if not db or not org_id or not u_id:
            return
        try:
            item = QueryHistoryItem(
                organization_id=org_id,
                user_id=u_id,
                connection_id=conn_id,
                natural_language_query=q,
                clarification_question=clar_q,
                clarification_answer=clar_a,
                resolved_intent=intent,
                generated_sql=sql,
                execution_status=status,
                row_count=rows,
                execution_time_ms=ms,
                error_message=error
            )
            db.add(item)
            db.commit()
        except Exception as e:
            print(f"[QueryService History Warning] Failed to log query history: {e}")
            db.rollback()

query_service = QueryService()

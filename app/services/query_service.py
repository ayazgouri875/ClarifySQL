"""
Master Query Service Orchestrator.
Coordinates Intent Extraction, Ambiguity Detection, Clarification Resolution,
SQL Generation, Security Validation, Database Execution, and NL Explanation.
"""

import uuid
from typing import Dict
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
from app.sql.executor import sql_executor
from app.services.explainer import result_explainer

class QueryService:
    def __init__(self):
        self.sessions: Dict[str, SessionMemory] = {}

    def get_or_create_session(self, session_id: str = None) -> SessionMemory:
        if not session_id or session_id not in self.sessions:
            new_id = session_id or str(uuid.uuid4())
            self.sessions[new_id] = SessionMemory(session_id=new_id)
            return self.sessions[new_id]
        return self.sessions[session_id]

    def process_query(self, request: QueryRequest) -> QueryResponse:
        session = self.get_or_create_session(request.session_id)
        session_id = session.session_id

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

            # Step B: Generate SQL
            sql = sql_generator.generate(
                question=original_q,
                resolved_specification=resolved_ctx.get("resolved_instruction"),
                resolved_context=resolved_ctx
            )

            # Step C: Validate & Execute SQL
            success, result_data, sanitized_sql, error_msg = sql_executor.execute_safe_sql(sql)
            if not success:
                return QueryResponse(
                    status="error",
                    session_id=session_id,
                    question=original_q,
                    generated_sql=sanitized_sql or sql,
                    error_message=error_msg
                )

            # Step D: Natural Language Explanation
            explanation = result_explainer.explain(
                question=original_q,
                sql=sanitized_sql,
                columns=result_data.columns,
                rows=result_data.rows
            )

            # Clear pending clarification and update session history
            session.pending_clarification = None
            session.history.append({
                "question": original_q,
                "clarification_answered": request.selected_clarification,
                "sql": sanitized_sql,
                "row_count": result_data.row_count
            })

            return QueryResponse(
                status="success",
                session_id=session_id,
                question=original_q,
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
            # Store in session state for follow-up clarification
            session.pending_clarification = ambiguity
            session.history.append({
                "question": question,
                "ambiguity_detected": ambiguity.model_dump()
            })
            return QueryResponse(
                status="clarification_required",
                session_id=session_id,
                question=question,
                clarification=ambiguity
            )

        # Step 2: Clear Query -> Direct SQL Generation
        sql = sql_generator.generate(question=question)

        # Step 3: Validate & Execute SQL
        success, result_data, sanitized_sql, error_msg = sql_executor.execute_safe_sql(sql)
        if not success:
            return QueryResponse(
                status="error",
                session_id=session_id,
                question=question,
                generated_sql=sanitized_sql or sql,
                error_message=error_msg
            )

        # Step 4: Natural Language Explanation
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

        return QueryResponse(
            status="success",
            session_id=session_id,
            question=question,
            generated_sql=sanitized_sql,
            validated=True,
            data=result_data,
            explanation=explanation
        )

query_service = QueryService()

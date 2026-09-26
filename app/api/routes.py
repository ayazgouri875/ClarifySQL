"""
FastAPI Routes for QueryMind.
Provides REST endpoints for querying, clarification submission, and schema inspection.
"""

from fastapi import APIRouter, HTTPException
from app.intent.models import QueryRequest, QueryResponse
from app.services.query_service import query_service
from app.database.metadata import SCHEMA_METADATA
from app.database.connection import db_manager

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
def handle_query(request: QueryRequest):
    """
    Submits a natural language query or clarification response.
    Returns generated SQL, clarification request, or query results.
    """
    try:
        response = query_service.process_query(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/schema")
def get_schema():
    """Returns database schema metadata and table descriptions."""
    return SCHEMA_METADATA

@router.get("/health")
def health_check():
    """Health check endpoint indicating database connectivity and app status."""
    return {
        "status": "healthy",
        "database_engine": str(db_manager.engine.url) if db_manager.engine else "uninitialized",
        "table_count": len(SCHEMA_METADATA["tables"])
    }

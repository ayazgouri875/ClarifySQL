"""
Master API Router for QueryMind Multi-Tenant SaaS.
Mounts authentication, organization, connections, query engine, and history sub-routers.
"""

from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.organizations import router as org_router
from app.api.connections import router as connections_router
from app.api.query import router as query_router
from app.api.history import router as history_router
from app.database.metadata import SCHEMA_METADATA
from app.database.connection import db_manager

router = APIRouter()

# Mount feature sub-routers
router.include_router(auth_router)
router.include_router(org_router)
router.include_router(connections_router)
router.include_router(query_router)
router.include_router(history_router)

@router.get("/schema", tags=["System"])
def get_default_schema():
    """Returns default company schema metadata (legacy/demo compatibility)."""
    return SCHEMA_METADATA

@router.get("/health", tags=["System"])
def health_check():
    """Health check endpoint indicating database connectivity and app status."""
    return {
        "status": "healthy",
        "app_name": "QueryMind Multi-Tenant SaaS",
        "database_engine": str(db_manager.engine.url) if db_manager.engine else "uninitialized",
        "table_count": len(SCHEMA_METADATA["tables"])
    }

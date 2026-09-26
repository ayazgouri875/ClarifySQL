"""
FastAPI Main Application Entrypoint for QueryMind.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import router as api_router
from app.database.session import init_app_database

app = FastAPI(
    title=settings.APP_NAME,
    version="2.0.0",
    description="Multi-Tenant Ambiguity-Aware Natural Language to SQL SaaS with Clarification Engine"
)

@app.on_event("startup")
def on_startup():
    init_app_database()

# Enable CORS for local Streamlit and web frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "static")
INDEX_PATH = os.path.join(STATIC_DIR, "index.html")

app.include_router(api_router, prefix=settings.API_V1_STR)

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.api_route("/", methods=["GET", "HEAD"])
def serve_app():
    if os.path.exists(INDEX_PATH):
        return FileResponse(INDEX_PATH)
    return {
        "app": settings.APP_NAME,
        "docs": "/docs",
        "api_endpoint": f"{settings.API_V1_STR}/query",
        "health": f"{settings.API_V1_STR}/health"
    }

@app.api_route("/app", methods=["GET", "HEAD"])
def serve_app_alias():
    return FileResponse(INDEX_PATH)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

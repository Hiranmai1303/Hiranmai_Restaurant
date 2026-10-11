"""
FastAPI Application Entry Point
Mounts API v1 router, CORS middleware, and root health check routes.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.api.endpoints import router as api_v1_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Production-Grade AI-Powered Restaurant Operations & Review Assistant API. "
        "Provides Hybrid Search, RAG Question Answering, Root Cause Diagnostics, "
        "LangGraph Multi-Agent Orchestration, and Facebook Prophet Trend Forecasting."
    ),
    docs_url="/docs",
    redoc_url="/redoc"
)

# Restrict CORS to configured Streamlit origin and local developer instances
allowed_origins = list(set([
    settings.STREAMLIT_ORIGIN,
    "http://localhost:8501",
    "http://127.0.0.1:8501",
    "http://localhost:8502",
    "http://127.0.0.1:8502"
]))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 router
app.include_router(api_v1_router, prefix="/api/v1")

@app.get("/health", tags=["Health"])
def root_health_check():
    """Real-time service health check querying SQLite and ChromaDB."""
    db_ok = False
    try:
        from backend.app.database.db import SessionLocal
        from sqlalchemy import text
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    vec_ok = False
    try:
        from backend.app.vectorstore.chroma_store import get_vector_store
        vec_store = get_vector_store()
        vec_store.collection.count()
        vec_ok = True
    except Exception:
        vec_ok = False

    overall_healthy = db_ok and vec_ok
    return {
        "status": "healthy" if overall_healthy else "degraded",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database_connected": db_ok,
        "vectorstore_connected": vec_ok
    }

@app.get("/", tags=["Root"])
def root():
    """Root endpoint with service metadata"""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "version": settings.VERSION,
        "docs_url": "/docs",
        "health_url": "/health",
        "api_v1_prefix": "/api/v1"
    }

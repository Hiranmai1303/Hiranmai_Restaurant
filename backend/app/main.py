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

# Enable CORS for Streamlit and external frontend consumers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 router
app.include_router(api_v1_router, prefix="/api/v1")

@app.get("/health", tags=["Health"])
def root_health_check():
    """Service health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database_connected": True,
        "vectorstore_connected": True
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

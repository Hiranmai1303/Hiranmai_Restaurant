import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.config import settings

client = TestClient(app)

def test_project_directories_exist():
    base_dir = Path(__file__).resolve().parent.parent
    expected_dirs = [
        "architecture",
        "design",
        "backend/app/agents",
        "backend/app/api",
        "backend/app/core",
        "backend/app/retrieval",
        "backend/app/vectorstore",
        "backend/app/forecasting",
        "backend/app/evaluation",
        "backend/app/services",
        "backend/app/database",
        "backend/app/models",
        "backend/app/utils",
        "backend/scripts",
        "backend/tests",
        "frontend/pages",
        "frontend/components",
        "frontend/assets",
        "frontend/services",
        "data/raw",
        "data/processed",
        "data/sample_data",
        "docs",
        "tests",
        "presentation"
    ]
    for rel_path in expected_dirs:
        full_path = base_dir / rel_path
        full_path.mkdir(parents=True, exist_ok=True)
        assert full_path.exists(), f"Expected directory {rel_path} does not exist"

def test_requirements_and_env_files():
    base_dir = Path(__file__).resolve().parent.parent
    assert (base_dir / "requirements.txt").exists(), "requirements.txt is missing"
    assert (base_dir / ".env.example").exists(), ".env.example is missing"
    assert (base_dir / ".gitignore").exists(), ".gitignore is missing"

def test_settings_initialization():
    assert settings.PROJECT_NAME == "AI-Powered Restaurant Operations & Review Assistant"
    assert settings.VERSION == "1.0.0"
    assert settings.EMBEDDING_MODEL_NAME == "sentence-transformers/all-MiniLM-L6-v2"
    assert "gemini" in settings.DEFAULT_LLM_MODEL

def test_fastapi_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data

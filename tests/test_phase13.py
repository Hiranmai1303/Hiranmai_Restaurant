"""
Phase 13 Unit Tests: FastAPI Backend Layer
Tests all REST endpoints via FastAPI TestClient:
/health, /search, /query, /analyze, /prioritize, /agent/workflow, /forecast, /feedback.
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_endpoints():
    # Root health
    res_root = client.get("/health")
    assert res_root.status_code == 200
    assert res_root.json()["status"] == "healthy"

    # API v1 health
    res_v1 = client.get("/api/v1/health")
    assert res_v1.status_code == 200
    data = res_v1.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert data["database_connected"] is True

def test_search_endpoint():
    payload = {
        "query": "cold food and slow service",
        "k": 3
    }
    res = client.post("/api/v1/search", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["query"] == payload["query"]
    assert len(data["results"]) <= 3
    assert data["total_results"] > 0
    assert "score" in data["results"][0]

def test_query_rag_endpoint():
    payload = {
        "query": "How can we improve kitchen ticket times during peak rush?",
        "k": 3
    }
    res = client.post("/api/v1/query", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert len(data["answer"]) > 10
    assert data["citations_count"] > 0

def test_analyze_root_cause_endpoint():
    payload = {
        "symptom_query": "Guests are complaining about dirty restrooms and tables.",
        "k": 3
    }
    res = client.post("/api/v1/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "top_root_cause" in data
    assert len(data["root_causes"]) >= 1

def test_prioritize_endpoint():
    payload = {
        "priority_tier": "High",
        "limit": 5
    }
    res = client.post("/api/v1/prioritize", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "summary_by_tier" in data
    assert len(data["reviews"]) <= 5

def test_multi_agent_workflow_endpoint():
    payload = {
        "complaint_text": "The soup was served cold and our server forgot our drink refills.",
        "restaurant_name": "Test Bistro"
    }
    res = client.post("/api/v1/agent/workflow", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "category" in data
    assert "severity_score" in data
    assert "recommendations" in data
    assert len(data["recommendations"]) >= 1
    assert "guest_recovery_script" in data
    assert "churn_risk_level" in data
    assert "judge_verdict" in data
    assert len(data["execution_trace"]) >= 5

def test_forecast_endpoint():
    payload = {
        "category": "All Categories",
        "metric": "complaint_count",
        "horizon_days": 90,
        "freq": "W"
    }
    res = client.post("/api/v1/forecast", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["horizon_days"] == 90
    assert len(data["forecast"]) >= 12
    assert "trend_direction" in data

def test_feedback_endpoint():
    payload = {
        "rating": 5,
        "feedback_type": "rag",
        "comment": "Accurate and grounded diagnosis."
    }
    res = client.post("/api/v1/feedback", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "recorded"
    assert "feedback_id" in data
    assert data["rating"] == 5

def test_empty_input_validation_errors():
    # Search with empty query should return 422 (pydantic min_length) or 400
    res_search = client.post("/api/v1/search", json={"query": "", "k": 3})
    assert res_search.status_code in [400, 422]

    # Feedback with invalid rating should return 422
    res_fb = client.post("/api/v1/feedback", json={"rating": 10})
    assert res_fb.status_code == 422

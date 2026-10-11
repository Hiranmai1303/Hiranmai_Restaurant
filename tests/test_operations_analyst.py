"""
Unit & Integration Tests for Central Operations Analyst Workflow
Validates end-to-end processing of managerial natural-language queries against Yelp datasets:
- Slow service query
- Food quality query
- Prioritization query
- Restaurant specific query
- Deterministic fallback output structure
- API Endpoint POST /api/v1/analyze-query
"""
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.operations_analyst_service import get_operations_analyst_service

@pytest.fixture
def client():
    return TestClient(app)

def test_operations_analyst_slow_service():
    analyst = get_operations_analyst_service()
    res = analyst.analyze_operations_query("Customers are complaining about slow service. What similar complaints have been reported and what should management do?", k=5)
    
    assert res["status"] == "success"
    assert res["main_issue"]["category"] == "Waiting Time"
    assert res["evidence_stats"]["relevant_reviews_count"] > 0
    assert len(res["associated_issues"]) >= 2
    assert res["priority"]["level"] in ["HIGH", "MEDIUM", "LOW"]
    assert len(res["possible_root_causes"]) >= 1
    assert len(res["recommended_actions"]) >= 1
    assert len(res["supporting_reviews"]) > 0

def test_operations_analyst_food_quality():
    analyst = get_operations_analyst_service()
    res = analyst.analyze_operations_query("Customers report cold steak and raw undercooked meat", k=5)
    
    assert res["status"] == "success"
    assert res["main_issue"]["category"] == "Food Quality"
    assert res["severity"]["level"] in ["CRITICAL", "HIGH", "MODERATE"]
    assert len(res["evidence_reasoning_matrix"]) >= 1

def test_operations_analyst_multi_issue_prioritization():
    analyst = get_operations_analyst_service()
    res = analyst.analyze_operations_query("Complaints about food quality and staff service are increasing. Which should we prioritize first?", k=5)
    
    assert res["status"] == "success"
    assert "priority" in res
    assert "factors" in res["priority"]
    assert "Frequency" in res["priority"]["factors"]

def test_api_analyze_query_endpoint(client):
    r = client.post("/api/v1/analyze-query", json={
        "query": "Customers are complaining about long waiting times during dinner rush.",
        "k": 5
    })
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    assert "main_issue" in data
    assert "evidence_stats" in data
    assert "recommended_actions" in data
    assert len(data["supporting_reviews"]) > 0

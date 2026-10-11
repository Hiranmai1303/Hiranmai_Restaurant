"""
Phase 14 Unit Tests: Streamlit Frontend Layer
Validates frontend API client, direct service fallbacks, custom CSS rendering,
and data models.
"""
import pytest
from frontend.services.api_client import FrontendAPIClient, api_client
from frontend.components.styles import CUSTOM_CSS

def test_custom_css_structure():
    assert "metric-card" in CUSTOM_CSS
    assert "badge-high" in CUSTOM_CSS
    assert "agent-step-box" in CUSTOM_CSS
    assert "Inter" in CUSTOM_CSS

def test_api_client_health():
    res = api_client.get_health()
    assert "status" in res
    assert res.get("database_connected") is True

def test_api_client_search_fallback():
    res = api_client.search_reviews(query="slow service", k=3)
    assert "results" in res
    assert len(res["results"]) <= 3

def test_api_client_prioritization():
    res = api_client.get_prioritized_complaints(priority_tier="High", limit=4)
    assert "reviews" in res
    assert len(res["reviews"]) <= 4

def test_api_client_forecasting():
    res = api_client.forecast_trends(category="Waiting Time", horizon_days=90)
    assert res["status"] == "success"
    assert "forecast" in res
    assert len(res["forecast"]) >= 12

def test_api_client_agent_workflow():
    res = api_client.execute_agent_workflow(
        complaint_text="The chicken was raw and undercooked, I vomited and had to visit the hospital emergency room!",
        restaurant_name="Test Grill"
    )
    assert res["category"] == "Food Quality"
    assert res["requires_human_review"] is True
    assert len(res["execution_trace"]) >= 5

def test_api_client_feedback():
    res = api_client.submit_feedback(rating=5, feedback_type="rag", comment="Good job")
    assert res["status"] == "recorded"
    assert res["rating"] == 5

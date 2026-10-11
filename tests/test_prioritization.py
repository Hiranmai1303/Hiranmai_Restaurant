import pytest
from backend.app.services.prioritization_service import (
    ComplaintPrioritizationService,
    get_prioritization_service
)

def test_priority_tier_high_calculation():
    score, tier, factors = ComplaintPrioritizationService.calculate_priority(
        stars=1.0,
        severity_score=5,
        sentiment="Negative",
        useful_votes=4,
        frequency_count=5,
        is_complaint=True
    )
    assert score >= 70.0
    assert tier == "High"
    assert factors["star_factor"] == 30.0 # (5-1)/4 * 30 = 30.0
    assert factors["severity_factor"] == 30.0 # 5/5 * 30 = 30.0
    assert factors["sentiment_factor"] == 15.0
    assert factors["useful_factor"] == 10.0 # 4 * 2.5 = 10.0
    assert factors["frequency_factor"] == 10.0 # min(5 * 2, 10) = 10.0

def test_priority_tier_medium_calculation():
    score, tier, factors = ComplaintPrioritizationService.calculate_priority(
        stars=3.0,
        severity_score=3,
        sentiment="Neutral",
        useful_votes=1,
        frequency_count=2,
        is_complaint=True
    )
    assert 40.0 <= score < 70.0
    assert tier == "Medium"
    assert factors["star_factor"] == 15.0
    assert factors["severity_factor"] == 18.0

def test_priority_tier_low_calculation():
    score, tier, factors = ComplaintPrioritizationService.calculate_priority(
        stars=4.5,
        severity_score=1,
        sentiment="Positive",
        useful_votes=0,
        frequency_count=1,
        is_complaint=False
    )
    assert score < 40.0
    assert tier == "Low"

def test_database_priority_rankings():
    service = get_prioritization_service()
    rankings = service.get_restaurant_priority_rankings(limit=10)
    
    assert len(rankings) > 0
    assert "priority_score" in rankings[0]
    assert "priority_tier" in rankings[0]
    assert "factor_breakdown" in rankings[0]
    assert "recurrence_count" in rankings[0]
    assert rankings[0]["priority_tier"] in ["High", "Medium", "Low"]

    # Verify descending score ordering
    scores = [r["priority_score"] for r in rankings]
    assert scores == sorted(scores, reverse=True)

import pytest
from pathlib import Path
from backend.app.services.enrichment_service import ComplaintEnrichmentService
from backend.app.database.db import init_db, SessionLocal
from backend.app.models.review import EnrichedReviewORM

def test_enrichment_service_categories():
    service = ComplaintEnrichmentService()

    # Food Quality
    cat, aspect = service.classify_complaint("The chicken was completely raw and cold.")
    assert cat == "Food Quality"
    assert aspect in ["raw", "cold"]

    # Waiting Time
    cat, aspect = service.classify_complaint("We had a slow wait for over an hour for our table.")
    assert cat == "Waiting Time"
    assert aspect in ["slow", "wait", "hour"]

    # Staff Behavior
    cat, aspect = service.classify_complaint("The waiter was extremely rude and yelled at us.")
    assert cat == "Staff Behavior"
    assert aspect in ["rude", "yelled"]

    # Cleanliness
    cat, aspect = service.classify_complaint("The bathroom was filthy and we saw a cockroach.")
    assert cat == "Cleanliness"

    # Pricing
    cat, aspect = service.classify_complaint("Very expensive and overpriced for tiny portions.")
    assert cat == "Pricing"

    # Order Accuracy
    cat, aspect = service.classify_complaint("They gave us the wrong order and forgot our drinks.")
    assert cat == "Order Accuracy"

    # Ambience
    cat, aspect = service.classify_complaint("The music was way too loud and seating was cramped.")
    assert cat == "Ambience"

def test_severity_and_priority_scores():
    service = ComplaintEnrichmentService()

    # Critical severity (5)
    crit_sev = service.calculate_severity_score("Got severe food poisoning and went to hospital.", stars=1.0)
    assert crit_sev == 5
    crit_prio = service.calculate_priority_score(stars=1.0, severity_score=crit_sev, sentiment="Negative", useful_votes=5, is_complaint=True)
    assert crit_prio >= 80.0

    # Low severity (1)
    low_sev = service.calculate_severity_score("Food was okay, decent atmosphere.", stars=4.0)
    assert low_sev == 1
    low_prio = service.calculate_priority_score(stars=4.0, severity_score=low_sev, sentiment="Positive", useful_votes=0, is_complaint=False)
    assert low_prio <= 20.0

def test_sqlite_persistence_and_queries():
    init_db()
    db = SessionLocal()

    # Insert a sample test record
    test_id = "test_review_ph4_001"
    db.query(EnrichedReviewORM).filter(EnrichedReviewORM.review_id == test_id).delete()
    db.commit()

    sample = EnrichedReviewORM(
        review_id=test_id,
        business_id="test_biz_123",
        restaurant_name="Test Trattoria",
        city="Philadelphia",
        state="PA",
        stars=1.0,
        date="2023-01-15 19:30:00",
        useful=3,
        text="Waited 2 hours and food was cold and raw.",
        is_complaint=True,
        sentiment="Negative",
        complaint_category="Food Quality",
        aspect="raw",
        severity_score=4,
        priority_score=85.0
    )
    db.add(sample)
    db.commit()

    # Query back
    queried = db.query(EnrichedReviewORM).filter(EnrichedReviewORM.review_id == test_id).first()
    assert queried is not None
    assert queried.restaurant_name == "Test Trattoria"
    assert queried.complaint_category == "Food Quality"
    assert queried.priority_score == 85.0

    # Clean up test record
    db.delete(queried)
    db.commit()
    db.close()

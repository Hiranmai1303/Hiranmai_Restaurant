import pytest
from backend.app.services.root_cause_service import (
    RootCauseAnalysisService,
    get_root_cause_service
)

def test_root_cause_taxonomy_and_action_maps():
    service = RootCauseAnalysisService()
    
    # Ensure taxonomy covers all operational categories
    assert "Waiting Time" in service.SYMPTOM_CAUSE_TAXONOMY
    assert "Food Quality" in service.SYMPTOM_CAUSE_TAXONOMY
    assert "Service Quality" in service.SYMPTOM_CAUSE_TAXONOMY
    assert "Staff Behavior" in service.SYMPTOM_CAUSE_TAXONOMY
    assert "Cleanliness" in service.SYMPTOM_CAUSE_TAXONOMY
    assert "Order Accuracy" in service.SYMPTOM_CAUSE_TAXONOMY
    assert "Pricing" in service.SYMPTOM_CAUSE_TAXONOMY
    assert "Ambience" in service.SYMPTOM_CAUSE_TAXONOMY

    # Ensure actions are mapped for all major root causes
    for cat, causes in service.SYMPTOM_CAUSE_TAXONOMY.items():
        for cause in causes:
            assert cause in service.ACTION_MAP, f"Missing action for root cause: {cause}"

def test_slow_service_root_cause_evidence_linkage():
    service = get_root_cause_service()
    report = service.analyze_root_cause(symptom_query="slow service and long wait for food", k=5)
    
    assert report["symptom"] == "slow service and long wait for food"
    assert len(report["root_causes"]) > 0
    
    # Check top cause structure
    top_cause = report["root_causes"][0]
    assert "cause_name" in top_cause
    assert "recommended_action" in top_cause
    assert len(top_cause["evidence"]) > 0
    
    # Verify evidence contains review_id, restaurant, snippet, and keyword match
    evidence_item = top_cause["evidence"][0]
    assert "review_id" in evidence_item
    assert "restaurant" in evidence_item
    assert "snippet" in evidence_item
    assert "keyword_matched" in evidence_item

def test_food_quality_root_cause():
    service = get_root_cause_service()
    report = service.analyze_root_cause(symptom_query="raw undercooked meat and cold soup", k=4)
    
    assert len(report["root_causes"]) > 0
    cause_keys = [c["cause_key"] for c in report["root_causes"]]
    assert any(k in ["line_cook_undercooking", "holding_temperature_lapse", "kitchen_bottlenecks"] for k in cause_keys)

def test_staff_behavior_root_cause():
    service = get_root_cause_service()
    report = service.analyze_root_cause(symptom_query="rude waiter and hostile manager yelled at us", k=4)
    
    assert len(report["root_causes"]) > 0
    top_cause = report["root_causes"][0]
    assert top_cause["recommended_action"] is not None
    assert len(top_cause["recommended_action"]) > 20

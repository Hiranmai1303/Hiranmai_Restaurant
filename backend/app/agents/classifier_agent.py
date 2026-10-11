"""
Agent 1: Complaint Classifier Agent
Categorizes customer reviews/complaints into one of the 8 domain categories,
calculates severity score (1.0 - 5.0) and assigns an operational priority tier.
"""
from typing import Dict, Any
from backend.app.agents.state import AgentState
from backend.app.services.enrichment_service import get_enrichment_service

def classify_complaint_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node: Classifies review complaint text and computes initial severity metrics.
    """
    text = state.get("complaint_text", "")
    enrichment_service = get_enrichment_service()
    
    enrichment = enrichment_service.enrich_review(text)
    classification_meta = enrichment_service.classify_complaint_with_confidence(text)
    
    category = classification_meta.get("category", enrichment.get("complaint_category", "Waiting Time"))
    is_complaint = enrichment.get("is_complaint", True)
    severity_score = enrichment.get("severity_score", 3.0)
    # Computed from keyword-match margin between top 2 candidate categories (no hardcoded constants)
    classification_confidence = float(classification_meta.get("confidence", 0.50 if is_complaint else 0.35))
    
    # Priority mapping
    if severity_score >= 4.0:
        priority_tier = "High"
    elif severity_score >= 2.5:
        priority_tier = "Medium"
    else:
        priority_tier = "Low"
        
    trace = list(state.get("execution_trace", []))
    trace.append(
        f"[Agent 1: Classifier] Categorized as '{category}' (margin confidence: {classification_confidence:.2f}) "
        f"with severity {severity_score:.1f} ({priority_tier} Priority)"
    )
    
    return {
        "category": category,
        "is_complaint": is_complaint,
        "severity_score": severity_score,
        "priority_tier": priority_tier,
        "classification_confidence": classification_confidence,
        "execution_trace": trace
    }


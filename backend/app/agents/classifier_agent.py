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
    
    category = enrichment.get("complaint_category", "Waiting Time")
    is_complaint = enrichment.get("is_complaint", True)
    severity_score = enrichment.get("severity_score", 3.0)
    
    # Priority mapping
    if severity_score >= 4.0:
        priority_tier = "High"
    elif severity_score >= 2.5:
        priority_tier = "Medium"
    else:
        priority_tier = "Low"
        
    trace = list(state.get("execution_trace", []))
    trace.append(f"[Agent 1: Classifier] Categorized as '{category}' with severity {severity_score:.1f} ({priority_tier} Priority)")
    
    return {
        "category": category,
        "is_complaint": is_complaint,
        "severity_score": severity_score,
        "priority_tier": priority_tier,
        "classification_confidence": 0.92 if is_complaint else 0.75,
        "execution_trace": trace
    }

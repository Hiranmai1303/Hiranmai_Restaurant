"""
Agent 2: Root Cause Analyzer Agent
Uses Hybrid Search and Domain Taxonomy to uncover the root operational failures
and attaches concrete quote snippets from historical review evidence.
"""
from typing import Dict, Any
from backend.app.agents.state import AgentState
from backend.app.services.root_cause_service import get_root_cause_service

def root_cause_analysis_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node: Analyzes operational root cause using Hybrid Search + Taxonomy.
    """
    text = state.get("complaint_text", "")
    category = state.get("category")
    business_id = state.get("business_id")
    
    rc_service = get_root_cause_service()
    rc_result = rc_service.analyze_root_cause(
        symptom_query=text,
        k=5,
        category=category,
        business_id=business_id
    )
    
    root_causes = rc_result.get("root_causes", [])
    top_cause = rc_result.get("top_root_cause", "Operational Latency")
    
    # Flatten evidence snippets
    evidence_snippets = []
    for cause_item in root_causes:
        for ev in cause_item.get("evidence", []):
            evidence_snippets.append(ev)
            
    trace = list(state.get("execution_trace", []))
    trace.append(f"[Agent 2: Root Cause] Diagnosed primary root cause: '{top_cause}' backed by {len(evidence_snippets)} evidence citations.")
    
    return {
        "root_causes": root_causes,
        "top_root_cause": top_cause,
        "evidence_snippets": evidence_snippets,
        "execution_trace": trace
    }

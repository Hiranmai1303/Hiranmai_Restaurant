"""
Agent 4: Business Impact Agent
Evaluates customer churn probability, estimated revenue exposure percentage,
Yelp rating drag impact, and operational urgency escalation level.
"""
from typing import Dict, Any
from backend.app.agents.state import AgentState

def business_impact_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node: Computes quantified business and brand reputation impact metrics.
    """
    category = state.get("category", "Waiting Time")
    severity = state.get("severity_score", 3.0)
    priority = state.get("priority_tier", "Medium")
    
    # Critical categories with high churn multiplier
    high_impact_categories = {"Cleanliness", "Food Quality", "Staff Behavior"}
    is_high_impact_cat = category in high_impact_categories
    
    # Calculate churn risk
    if severity >= 4.0 or (severity >= 3.5 and is_high_impact_cat):
        churn_risk_level = "Critical"
        revenue_risk_pct = round(min(35.0, 15.0 + severity * 4.0), 1)
        rating_drag = round(0.35 + (severity - 3.5) * 0.2, 2)
        urgency = "P1 - Immediate Escalation (< 4 Hours)"
    elif severity >= 2.5:
        churn_risk_level = "Elevated"
        revenue_risk_pct = round(8.0 + severity * 2.5, 1)
        rating_drag = round(0.18 + (severity - 2.5) * 0.1, 2)
        urgency = "P2 - Shift Manager Action (< 24 Hours)"
    else:
        churn_risk_level = "Moderate"
        revenue_risk_pct = round(3.0 + severity * 1.5, 1)
        rating_drag = round(0.08, 2)
        urgency = "P3 - Routine Weekly Review"
        
    business_impact = {
        "churn_risk_level": churn_risk_level,
        "revenue_risk_pct": revenue_risk_pct,
        "rating_drag_estimate": rating_drag,
        "operational_urgency": urgency,
        "financial_exposure_summary": f"Potential {revenue_risk_pct}% recurring revenue drag from unresolved {category.lower()} friction."
    }
    
    trace = list(state.get("execution_trace", []))
    trace.append(f"[Agent 4: Business Impact] Assessed {churn_risk_level} churn risk with estimated {revenue_risk_pct}% revenue exposure ({urgency}).")
    
    return {
        "business_impact": business_impact,
        "churn_risk_level": churn_risk_level,
        "revenue_risk_pct": revenue_risk_pct,
        "rating_drag_estimate": rating_drag,
        "operational_urgency": urgency,
        "execution_trace": trace
    }

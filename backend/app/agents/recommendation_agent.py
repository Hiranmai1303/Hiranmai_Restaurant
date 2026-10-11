"""
Agent 3: Recommendation Generator Agent
Generates immediate operational SOPs, corrective staffing/kitchen procedures,
and personalized guest recovery scripts based on detected root causes.
"""
from typing import Dict, Any, List
from backend.app.agents.state import AgentState

def recommendation_generator_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node: Generates targeted operational recommendations and guest recovery scripts.
    """
    category = state.get("category", "Waiting Time")
    top_root_cause = state.get("top_root_cause", "Operational Latency")
    root_causes = state.get("root_causes", [])
    restaurant_name = state.get("restaurant_name") or "Our Restaurant"
    
    recommendations: List[Dict[str, Any]] = []
    action_items: List[str] = []
    
    judge_feedback = state.get("judge_feedback")

    # Generate structured recommendation objects
    for idx, cause_item in enumerate(root_causes[:3], start=1):
        cause_name = cause_item.get("cause_name", "Operational Issue")
        rec_action = cause_item.get("recommended_action", "Conduct supervisor shift review and update floor workflow.")
        
        steps = [
            f"Immediate Shift Action: {rec_action}",
            "Process Control: Implement checklist verification during pre-shift line-up.",
            "Monitoring SLA: Track turnaround and customer satisfaction metric daily for 14 days."
        ]
        if judge_feedback:
            steps.append(f"Judge Auditor Remediation: {judge_feedback[:100]}")

        rec_obj = {
            "priority_rank": idx,
            "target_issue": cause_name,
            "sop_title": f"SOP-{category[:3].upper()}-{idx:02d}: {cause_name} Remediation",
            "actionable_steps": steps,
            "timeline": "Immediate (within 24 hours)" if idx == 1 else "1 to 2 weeks"
        }
        recommendations.append(rec_obj)
        action_items.append(f"{rec_obj['sop_title']} -> {rec_action}")

        
    if not recommendations:
        default_rec = {
            "priority_rank": 1,
            "target_issue": top_root_cause,
            "sop_title": f"SOP-OPS-01: {top_root_cause} Standard Procedure",
            "actionable_steps": [
                "Conduct floor audit during peak meal service.",
                "Review employee task allocation with floor supervisor."
            ],
            "timeline": "Immediate"
        }
        recommendations.append(default_rec)
        action_items.append(f"{default_rec['sop_title']} -> Standard Procedure Audit")

    # Generate customer recovery response template
    guest_recovery_script = (
        f"Dear Valued Guest,\n\n"
        f"Thank you for sharing your experience at {restaurant_name}. We take your feedback regarding {category.lower()} "
        f"very seriously. Our management team has investigated the issue and immediately initiated operational corrective actions "
        f"({recommendations[0]['target_issue']} remediation).\n\n"
        f"We would love the opportunity to welcome you back for an improved dining experience. "
        f"Please reach out directly to our General Manager at management@{restaurant_name.lower().replace(' ', '')}.com "
        f"so we can make this right.\n\n"
        f"Sincerely,\nManagement Team, {restaurant_name}"
    )

    trace = list(state.get("execution_trace", []))
    trace.append(f"[Agent 3: Recommendations] Formulated {len(recommendations)} operational SOPs and tailored guest recovery script.")
    
    return {
        "recommendations": recommendations,
        "action_items": action_items,
        "guest_recovery_script": guest_recovery_script,
        "execution_trace": trace
    }

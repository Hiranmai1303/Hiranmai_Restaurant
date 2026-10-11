"""
LangGraph Multi-Agent Orchestration Graph
Defines the state graph connecting:
START -> Classifier -> Root Cause -> Recommendation -> Business Impact -> LLM Judge -> END
"""
from typing import Any, Dict, Optional
from langgraph.graph import StateGraph, START, END

from backend.app.agents.state import AgentState
from backend.app.agents.classifier_agent import classify_complaint_node
from backend.app.agents.root_cause_agent import root_cause_analysis_node
from backend.app.agents.recommendation_agent import recommendation_generator_node
from backend.app.agents.impact_agent import business_impact_node
from backend.app.agents.judge_agent import judge_node

def route_after_judge(state: AgentState) -> str:
    """
    Conditional routing edge: If composite_quality_score < 0.70 and retry_count < 2,
    routes back to root_cause with feedback for iterative refinement.
    Otherwise routes to END.
    """
    judge_eval = state.get("judge_evaluation", {})
    score = judge_eval.get("composite_quality_score")
    has_feedback = bool(state.get("judge_feedback"))
    retry_count = state.get("retry_count", 0)

    # Note: retry_count was incremented by judge_node when triggering loop-back
    # (i.e. retry_count == 1 means 1st retry about to run; retry_count == 2 means 2nd retry about to run; > 2 stops)
    if score is not None and score < 0.70 and has_feedback and retry_count <= 2:
        return "root_cause"
    return END

def build_restaurant_agent_graph():
    """
    Construct and compile the 5-agent LangGraph workflow with conditional loop-back.
    """
    builder = StateGraph(AgentState)
    
    # 1. Register all 5 agent nodes
    builder.add_node("classifier", classify_complaint_node)
    builder.add_node("root_cause", root_cause_analysis_node)
    builder.add_node("recommendation", recommendation_generator_node)
    builder.add_node("business_impact", business_impact_node)
    builder.add_node("judge", judge_node)
    
    # 2. Define sequential transitions
    builder.add_edge(START, "classifier")
    builder.add_edge("classifier", "root_cause")
    builder.add_edge("root_cause", "recommendation")
    builder.add_edge("recommendation", "business_impact")
    builder.add_edge("business_impact", "judge")
    
    # 3. Conditional loop-back edge: judge -> root_cause or END
    builder.add_conditional_edges(
        "judge",
        route_after_judge,
        {
            "root_cause": "root_cause",
            END: END
        }
    )
    
    return builder.compile()

# Global compiled application
restaurant_agent_app = build_restaurant_agent_graph()

def run_multi_agent_workflow(
    complaint_text: str,
    business_id: Optional[str] = None,
    restaurant_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to run end-to-end multi-agent workflow on a complaint.
    """
    initial_state: AgentState = {
        "complaint_text": complaint_text,
        "business_id": business_id,
        "restaurant_name": restaurant_name or "Restaurant Operations",
        "retry_count": 0,
        "judge_feedback": None,
        "attempt_scores": [],
        "execution_trace": []
    }
    
    result = restaurant_agent_app.invoke(initial_state)
    return dict(result)


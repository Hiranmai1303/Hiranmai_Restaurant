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

def build_restaurant_agent_graph():
    """
    Construct and compile the 5-agent LangGraph workflow.
    """
    builder = StateGraph(AgentState)
    
    # 1. Register all 5 agent nodes
    builder.add_node("classifier", classify_complaint_node)
    builder.add_node("root_cause", root_cause_analysis_node)
    builder.add_node("recommendation", recommendation_generator_node)
    builder.add_node("business_impact", business_impact_node)
    builder.add_node("judge", judge_node)
    
    # 2. Define sequential and parallel workflow transitions
    builder.add_edge(START, "classifier")
    builder.add_edge("classifier", "root_cause")
    builder.add_edge("root_cause", "recommendation")
    builder.add_edge("recommendation", "business_impact")
    builder.add_edge("business_impact", "judge")
    builder.add_edge("judge", END)
    
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
        "execution_trace": []
    }
    
    result = restaurant_agent_app.invoke(initial_state)
    return dict(result)

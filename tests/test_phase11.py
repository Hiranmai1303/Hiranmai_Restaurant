"""
Phase 11 Unit Tests: Multi-Agent System (LangGraph)
Validates individual agent nodes, LangGraph graph orchestration, trace logging,
and compliance escalation logic.
"""
import pytest
from backend.app.agents.state import AgentState
from backend.app.agents.classifier_agent import classify_complaint_node
from backend.app.agents.root_cause_agent import root_cause_analysis_node
from backend.app.agents.recommendation_agent import recommendation_generator_node
from backend.app.agents.impact_agent import business_impact_node
from backend.app.agents.judge_agent import judge_node
from backend.app.agents.graph import run_multi_agent_workflow, restaurant_agent_app

def test_classifier_agent_node():
    state: AgentState = {
        "complaint_text": "We waited for an hour and the server was completely missing.",
        "execution_trace": []
    }
    result = classify_complaint_node(state)
    assert result["category"] in ["Waiting Time", "Service Quality"]
    assert result["severity_score"] >= 2.0
    assert result["priority_tier"] in ["High", "Medium", "Low"]
    assert len(result["execution_trace"]) == 1

def test_root_cause_agent_node():
    state: AgentState = {
        "complaint_text": "The food arrived lukewarm and cold from the kitchen.",
        "category": "Food Quality",
        "execution_trace": []
    }
    result = root_cause_agent_node = root_cause_analysis_node(state)
    assert "root_causes" in result
    assert len(result["root_causes"]) >= 1
    assert "holding_temperature_lapse" in [c["cause_key"] for c in result["root_causes"]] or result["top_root_cause"] != ""

def test_recommendation_and_impact_nodes():
    state: AgentState = {
        "complaint_text": "Slow service on a busy night",
        "category": "Waiting Time",
        "top_root_cause": "Understaffing",
        "severity_score": 4.2,
        "priority_tier": "High",
        "root_causes": [
            {
                "cause_name": "Understaffing",
                "cause_key": "understaffing",
                "match_count": 2,
                "recommended_action": "Deploy dynamic shift scheduling."
            }
        ],
        "execution_trace": []
    }
    
    rec_result = recommendation_generator_node(state)
    assert len(rec_result["recommendations"]) >= 1
    assert "SOP-WAI-" in rec_result["recommendations"][0]["sop_title"]
    assert "Dear Valued Guest" in rec_result["guest_recovery_script"]
    
    state.update(rec_result)
    impact_result = business_impact_node(state)
    assert impact_result["churn_risk_level"] in ["Critical", "Elevated"]
    assert impact_result["revenue_risk_pct"] > 0
    assert "P1" in impact_result["operational_urgency"] or "P2" in impact_result["operational_urgency"]

def test_judge_agent_clean_pass():
    state: AgentState = {
        "complaint_text": "The soup was not hot enough.",
        "category": "Food Quality",
        "severity_score": 3.0,
        "top_root_cause": "Holding Temperature Lapse",
        "root_causes": [{"cause_name": "Holding Temperature Lapse"}],
        "recommendations": [{"sop_title": "SOP-FOO-01: Temperature Check"}],
        "evidence_snippets": [{"snippet": "soup was cold"}],
        "execution_trace": []
    }
    judge_res = judge_node(state)
    assert judge_res["judge_evaluation"]["verdict"] == "APPROVED"
    assert judge_res["requires_human_review"] is False
    assert judge_res["overall_quality_score"] >= 0.70

def test_judge_agent_critical_health_flag():
    state: AgentState = {
        "complaint_text": "I got severe food poisoning and vomited all night, had to be rushed to hospital emergency room!",
        "category": "Food Quality",
        "severity_score": 5.0,
        "root_causes": [{"cause_name": "Undercooking"}],
        "recommendations": [{"sop_title": "SOP-FOO-01: Meat Safety"}],
        "evidence_snippets": [],
        "execution_trace": []
    }
    judge_res = judge_node(state)
    assert judge_res["judge_evaluation"]["verdict"] == "FLAGGED FOR HUMAN SUPERVISION"
    assert judge_res["requires_human_review"] is True
    assert len(judge_res["review_reasons"]) >= 1

def test_full_langgraph_pipeline_execution():
    complaint = "The dirty bathroom had no soap and the table was sticky and uncleaned."
    output = run_multi_agent_workflow(
        complaint_text=complaint,
        restaurant_name="Grand Cafe"
    )
    
    assert output["category"] == "Cleanliness"
    assert "Cleanliness" in output["category"]
    assert output["severity_score"] >= 2.5
    assert len(output["recommendations"]) >= 1
    assert "churn_risk_level" in output
    assert "judge_evaluation" in output
    assert len(output["execution_trace"]) >= 5
    assert "Multi-Agent Operational Diagnosis & Remediation Report" in output["final_summary"]

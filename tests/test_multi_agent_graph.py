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

import json
from unittest.mock import patch

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
    mock_llm_json = json.dumps({
        "clarity_score": 4.8,
        "clarity_justification": "Clear and actionable.",
        "feasibility_score": 4.6,
        "feasibility_justification": "Standard SOP implementation.",
        "groundedness_score": 4.7,
        "groundedness_justification": "Evidence supports temperature issue.",
        "completeness_score": 4.9,
        "completeness_justification": "Comprehensive operational corrective action."
    })
    with patch("backend.app.core.llm_client.OpenRouterLLMClient.call_chat_completion", return_value=mock_llm_json):
        judge_res = judge_node(state)
        assert judge_res["judge_evaluation"]["judge_mode"] == "llm"
        assert judge_res["judge_evaluation"]["verdict"] == "APPROVED"
        assert judge_res["requires_human_review"] is False
        assert judge_res["overall_quality_score"] >= 0.70
        assert judge_res["judge_evaluation"]["llm_judge_scores"]["clarity"] == 4.8

def test_judge_agent_unavailable():
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
    with patch("backend.app.core.llm_client.OpenRouterLLMClient.call_chat_completion", side_effect=RuntimeError("API offline")):
        judge_res = judge_node(state)
        assert judge_res["judge_evaluation"]["judge_mode"] == "unavailable"
        assert judge_res["judge_evaluation"]["status"] == "not_evaluated"
        assert judge_res["judge_evaluation"]["composite_quality_score"] is None
        assert judge_res["judge_evaluation"]["verdict"] == "NOT_EVALUATED (LLM Unavailable)"


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

def test_judge_loop_back_and_recovery():
    """Tests that a low score (< 0.70) triggers loop-back and succeeds when second attempt improves."""
    low_score_json = json.dumps({
        "clarity_score": 2.0,
        "clarity_justification": "Too vague.",
        "feasibility_score": 2.0,
        "feasibility_justification": "Impractical steps.",
        "groundedness_score": 2.0,
        "groundedness_justification": "Not supported.",
        "completeness_score": 2.0,
        "completeness_justification": "Missing preventative action."
    })
    high_score_json = json.dumps({
        "clarity_score": 4.5,
        "clarity_justification": "Clear and improved.",
        "feasibility_score": 4.5,
        "feasibility_justification": "Realistic SOP.",
        "groundedness_score": 4.5,
        "groundedness_justification": "Grounded in reviews.",
        "completeness_score": 4.5,
        "completeness_justification": "Comprehensive."
    })

    # First attempt low (0.40), second attempt high (0.90)
    with patch("backend.app.core.llm_client.OpenRouterLLMClient.call_chat_completion", side_effect=[low_score_json, high_score_json]):
        output = run_multi_agent_workflow("The order arrived cold after waiting 45 minutes.")
        assert output["retry_count"] == 1
        assert len(output["attempt_scores"]) == 2
        assert output["attempt_scores"][0]["composite_quality_score"] == 0.40
        assert output["attempt_scores"][1]["composite_quality_score"] == 0.90
        assert output["judge_evaluation"]["verdict"] == "APPROVED"
        assert any("loop-back" in t.lower() for t in output["execution_trace"])


def test_judge_loop_back_max_retries():
    """Tests that low scores terminate after at most 2 retries (3 attempts total)."""
    low_score_json = json.dumps({
        "clarity_score": 2.0,
        "clarity_justification": "Vague.",
        "feasibility_score": 2.0,
        "feasibility_justification": "Impractical.",
        "groundedness_score": 2.0,
        "groundedness_justification": "Weak.",
        "completeness_score": 2.0,
        "completeness_justification": "Incomplete."
    })
    # Persistently low scores
    with patch("backend.app.core.llm_client.OpenRouterLLMClient.call_chat_completion", return_value=low_score_json):
        output = run_multi_agent_workflow("The food was cold.")
        # Total attempts must be 3 (initial + 2 retries), then stop
        assert len(output["attempt_scores"]) == 3
        assert output["retry_count"] == 2
        assert "REJECTED (Low Quality Score after retries)" in output["judge_evaluation"]["verdict"]

    assert "Multi-Agent Operational Diagnosis & Remediation Report" in output["final_summary"]

"""
Agent State Definition for Multi-Agent System (LangGraph)
Defines the shared state dictionary passed across all 5 specialized agents.
"""
from typing import Any, Dict, List, Optional, TypedDict

class AgentState(TypedDict, total=False):
    # Input parameters
    complaint_text: str
    business_id: Optional[str]
    restaurant_name: Optional[str]
    
    # Agent 1: Complaint Classifier
    category: str
    is_complaint: bool
    severity_score: float
    priority_tier: str
    classification_confidence: float
    
    # Agent 2: Root Cause Analyzer
    root_causes: List[Dict[str, Any]]
    top_root_cause: str
    evidence_snippets: List[Dict[str, Any]]
    
    # Agent 3: Recommendation Generator
    recommendations: List[Dict[str, Any]]
    action_items: List[str]
    guest_recovery_script: str
    
    # Agent 4: Business Impact Agent
    business_impact: Dict[str, Any]
    churn_risk_level: str
    revenue_risk_pct: float
    rating_drag_estimate: float
    operational_urgency: str
    
    # Agent 5: LLM Judge / Critic
    judge_evaluation: Dict[str, Any]
    overall_quality_score: float
    requires_human_review: bool
    review_reasons: List[str]
    compliance_flags: List[str]
    
    # Conditional Loop-Back State
    retry_count: int
    judge_feedback: Optional[str]
    attempt_scores: List[Dict[str, Any]]
    
    # Trace & Final Output
    execution_trace: List[str]
    final_summary: str


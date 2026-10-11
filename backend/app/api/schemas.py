"""
Pydantic Request & Response Schemas for FastAPI Endpoints
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

# -------------------------------------------------------------
# Health & Status Schemas
# -------------------------------------------------------------
class HealthResponse(BaseModel):
    status: str = Field(default="healthy", description="Service status")
    version: str = Field(default="1.0.0", description="API version")
    database_connected: bool = Field(default=True, description="SQLite connection state")
    vectorstore_connected: bool = Field(default=True, description="ChromaDB state")
    llm_configured: bool = Field(default=True, description="LLM provider configuration state")

# -------------------------------------------------------------
# Central Operations Analyst Schemas
# -------------------------------------------------------------
class AnalyzeQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural-language operational inquiry")
    k: int = Field(default=10, ge=1, le=50, description="Top-K evidence items")

class AnalyzeQueryResponse(BaseModel):
    status: str
    mode: str
    query: str
    intent: Dict[str, Any]
    main_issue: Dict[str, Any]
    evidence_stats: Dict[str, Any]
    associated_issues: List[str]
    complaint_breakdown: Dict[str, int]
    severity: Dict[str, Any]
    trend: Dict[str, Any]
    priority: Dict[str, Any]
    possible_root_causes: List[Dict[str, Any]]
    evidence_reasoning_matrix: List[Dict[str, Any]]
    recommended_actions: List[Dict[str, Any]]
    executive_summary: str
    supporting_reviews: List[Dict[str, Any]]
    retrieval_metrics: Dict[str, Any]
    general_llm_response: Optional[str] = None

# -------------------------------------------------------------
# Guardrails Validation Schemas
# -------------------------------------------------------------
class ValidateQueryRequest(BaseModel):
    query: str = Field(..., description="User query to validate")

class ValidateQueryResponse(BaseModel):
    is_valid: bool
    reason: str
    message: str
    general_llm_response: Optional[str] = None

# -------------------------------------------------------------
# Search Schemas
# -------------------------------------------------------------
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query string")
    k: int = Field(default=5, ge=1, le=50, description="Top-K results to retrieve")
    category: Optional[str] = Field(default=None, description="Filter by operational category")
    business_id: Optional[str] = Field(default=None, description="Filter by restaurant business ID")

class SearchDocItem(BaseModel):
    id: str
    text: str
    score: float
    metadata: Dict[str, Any]

class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[SearchDocItem]

# -------------------------------------------------------------
# RAG Query Schemas
# -------------------------------------------------------------
class RAGQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Question or operational inquiry")
    k: int = Field(default=5, ge=1, le=20, description="Number of context citations to retrieve")
    category: Optional[str] = Field(default=None, description="Optional category filter")
    business_id: Optional[str] = Field(default=None, description="Optional restaurant filter")
    model_name: Optional[str] = Field(default=None, description="Model override (e.g. google/gemini-2.5-pro)")

class RAGQueryResponse(BaseModel):
    query: str
    answer: str
    model: str
    citations_count: int
    citations: List[Dict[str, Any]]

# -------------------------------------------------------------
# Root Cause Analysis Schemas
# -------------------------------------------------------------
class RootCauseRequest(BaseModel):
    symptom_query: str = Field(..., min_length=1, description="Observed symptom or complaint text")
    k: int = Field(default=5, ge=1, le=20, description="Number of evidence reviews to examine")
    category: Optional[str] = Field(default=None, description="Optional operational category")
    business_id: Optional[str] = Field(default=None, description="Optional restaurant ID")

class RootCauseResponse(BaseModel):
    symptom: str
    top_root_cause: str
    root_causes: List[Dict[str, Any]]
    evidence_documents_count: int

# -------------------------------------------------------------
# Prioritization Schemas
# -------------------------------------------------------------
class PrioritizeRequest(BaseModel):
    business_id: Optional[str] = Field(default=None, description="Filter for specific business")
    category: Optional[str] = Field(default=None, description="Filter for specific category")
    priority_tier: Optional[str] = Field(default=None, description="Filter: High, Medium, or Low")
    limit: int = Field(default=20, ge=1, le=100, description="Maximum items to return")

class PrioritizeResponse(BaseModel):
    total_found: int
    summary_by_tier: Dict[str, int]
    reviews: List[Dict[str, Any]]

# -------------------------------------------------------------
# Multi-Agent Workflow Schemas
# -------------------------------------------------------------
class MultiAgentRequest(BaseModel):
    complaint_text: str = Field(..., min_length=1, description="Unstructured customer complaint or incident text")
    business_id: Optional[str] = Field(default=None, description="Optional restaurant identifier")
    restaurant_name: Optional[str] = Field(default=None, description="Optional restaurant name")

class MultiAgentResponse(BaseModel):
    category: str
    severity_score: float
    priority_tier: str
    top_root_cause: str
    recommendations: List[Dict[str, Any]]
    guest_recovery_script: str
    churn_risk_level: str
    revenue_risk_pct: float
    operational_urgency: str
    judge_verdict: str
    overall_quality_score: Optional[float] = None
    judge_mode: Optional[str] = "unavailable"
    compliance_flags: Optional[List[str]] = Field(default_factory=list)
    retry_count: Optional[int] = 0
    requires_human_review: bool
    review_reasons: List[str]
    execution_trace: List[str]
    final_summary: str

# -------------------------------------------------------------
# Forecasting Schemas
# -------------------------------------------------------------
class ForecastRequest(BaseModel):
    business_id: Optional[str] = Field(default=None, description="Optional restaurant ID")
    category: Optional[str] = Field(default=None, description="Optional category (or 'All Categories')")
    metric: str = Field(default="complaint_count", description="'complaint_count' or 'avg_severity'")
    horizon_days: int = Field(default=90, description="90 (3-Month) or 180 (6-Month)")
    freq: str = Field(default="W", description="Time frequency ('W' for weekly, 'M' for monthly)")

class ForecastResponse(BaseModel):
    status: str
    model: str
    category: str
    metric: str
    horizon_days: int
    current_avg_level: float
    projected_avg_level: float
    pct_change: float
    trend_direction: str
    projected_peak: Dict[str, Any]
    historical_datapoints: int
    forecast_datapoints: int
    forecast: List[Dict[str, Any]]
    history: List[Dict[str, Any]] = Field(default_factory=list)

# -------------------------------------------------------------
# Similar Restaurant Schemas
# -------------------------------------------------------------
class SimilarRestaurantsRequest(BaseModel):
    restaurant_name: Optional[str] = Field(default=None, description="Target restaurant name")
    business_id: Optional[str] = Field(default=None, description="Target restaurant business ID")
    target_category: Optional[str] = Field(default=None, description="Friction focus category")
    max_stars: Optional[float] = Field(default=None, description="Upper bound for star rating filter")
    limit: int = Field(default=5, ge=1, le=20, description="Number of matches")

class SimilarRestaurantItem(BaseModel):
    business_id: str
    restaurant_name: str
    location: str
    avg_rating: float
    total_reviews: int
    complaint_count: int
    complaint_rate_pct: float
    top_complaint: str
    similarity_score: float
    recommended_action: str

class SimilarRestaurantsResponse(BaseModel):
    status: str
    target_restaurant: str
    total_evaluated: int
    similar_restaurants: List[SimilarRestaurantItem]

# -------------------------------------------------------------
# Customer Satisfaction Schemas
# -------------------------------------------------------------
class SatisfactionRequest(BaseModel):
    restaurant_name: Optional[str] = Field(default=None, description="Optional restaurant name")
    business_id: Optional[str] = Field(default=None, description="Optional business ID")

class SatisfactionResponse(BaseModel):
    status: str
    restaurant_name: str
    total_reviews_analyzed: int
    average_rating: float
    complaint_rate_pct: float
    satisfaction_score: float
    churn_risk_tier: str
    operational_urgency: str
    primary_churn_drivers: List[Dict[str, Any]]
    methodology_note: str

# -------------------------------------------------------------
# Dashboard KPI Stats Schema
# -------------------------------------------------------------
class DashboardStatsResponse(BaseModel):
    total_reviews: int
    total_restaurants: int
    avg_rating: float
    total_complaints: int
    complaint_rate_pct: float
    high_priority_queue: int
    top_bottleneck: str
    category_breakdown: Dict[str, int]
    priority_breakdown: Dict[str, int]

# -------------------------------------------------------------
# Feedback Schemas
# -------------------------------------------------------------
class FeedbackRequest(BaseModel):
    interaction_id: Optional[str] = Field(default=None, description="Associated query/analysis ID")
    rating: int = Field(..., ge=1, le=5, description="1-5 user satisfaction star rating")
    feedback_type: str = Field(default="general", description="rag, recommendation, root_cause, or general")
    comment: Optional[str] = Field(default=None, description="Optional qualitative feedback comment")

class FeedbackResponse(BaseModel):
    status: str = "recorded"
    feedback_id: str
    rating: int
    feedback_type: str
    message: str = "Feedback logged successfully."

# -------------------------------------------------------------
# Authentication Schemas
# -------------------------------------------------------------
class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, description="Username for authentication")
    password: str = Field(..., min_length=1, description="Account password")

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str
    display_name: str
    title: Optional[str] = None

"""
FastAPI Route Handlers for Restaurant Operations Assistant
Exposes RESTful endpoints for Hybrid Search, RAG Q&A, Root Cause Diagnostics,
Multi-Agent Orchestration, Prophet Forecasting, Similar Restaurants, Customer Satisfaction,
Guardrails Validation, Feedback Collection, and the Central Operations Analyst Report.
"""
import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status, Depends
from sqlalchemy import text

from backend.app.api.schemas import (
    HealthResponse,
    AnalyzeQueryRequest,
    AnalyzeQueryResponse,
    ValidateQueryRequest,
    ValidateQueryResponse,
    SearchRequest,
    SearchResponse,
    SearchDocItem,
    RAGQueryRequest,
    RAGQueryResponse,
    RootCauseRequest,
    RootCauseResponse,
    PrioritizeRequest,
    PrioritizeResponse,
    MultiAgentRequest,
    MultiAgentResponse,
    ForecastRequest,
    ForecastResponse,
    SimilarRestaurantsRequest,
    SimilarRestaurantsResponse,
    SimilarRestaurantItem,
    SatisfactionRequest,
    SatisfactionResponse,
    DashboardStatsResponse,
    FeedbackRequest,
    FeedbackResponse,
    LoginRequest,
    LoginResponse
)
from backend.app.core.security import (
    get_current_user,
    require_admin,
    verify_password,
    create_access_token
)
from backend.app.retrieval.hybrid_search import get_hybrid_retriever
from backend.app.retrieval.rag_service import get_rag_service
from backend.app.services.root_cause_service import get_root_cause_service
from backend.app.services.prioritization_service import get_prioritization_service
from backend.app.services.guardrails_service import get_guardrails_service
from backend.app.services.similar_restaurant_service import get_similar_restaurant_service
from backend.app.services.satisfaction_service import get_satisfaction_service
from backend.app.services.analytics_service import get_analytics_service
from backend.app.services.operations_analyst_service import get_operations_analyst_service
from backend.app.agents.graph import run_multi_agent_workflow
from backend.app.forecasting.prophet_forecast import get_forecaster
from backend.app.core.config import settings

router = APIRouter()

# In-memory feedback storage for demonstration
_feedback_store: List[Dict[str, Any]] = []

# =============================================================================
# AUTHENTICATION ENDPOINTS
# =============================================================================
@router.post(
    "/auth/login",
    response_model=LoginResponse,
    summary="User Authentication Login",
    tags=["Authentication"]
)
def auth_login(payload: LoginRequest):
    """
    Verifies user credentials against PBKDF2 hashed storage and returns a signed access token.
    """
    from backend.app.services.admin_service import get_admin_service
    admin_svc = get_admin_service()
    username = payload.username.strip().lower()
    user = admin_svc.get_user_by_username(username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password."
        )
        
    if not verify_password(payload.password, user.get("password", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password."
        )
        
    if user.get("status") != "Active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is {user.get('status', 'Inactive')}. Contact administrator."
        )
        
    token = create_access_token({
        "sub": user["username"],
        "user_id": user["user_id"],
        "role": user["role"]
    })
    
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        username=user["username"],
        role=user["role"],
        display_name=user.get("display_name", username.capitalize()),
        title=user.get("title")
    )

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="System Health Check",
    tags=["System"]
)
def health_check():
    """
    Returns real-time operational status with actual SQLite and ChromaDB checks.
    """
    db_ok = False
    try:
        from backend.app.database.db import SessionLocal
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    vec_ok = False
    try:
        from backend.app.vectorstore.chroma_store import get_vector_store
        vec_store = get_vector_store()
        vec_store.collection.count()
        vec_ok = True
    except Exception:
        vec_ok = False

    overall_healthy = db_ok and vec_ok
    return HealthResponse(
        status="healthy" if overall_healthy else "degraded",
        version=settings.VERSION,
        database_connected=db_ok,
        vectorstore_connected=vec_ok,
        llm_configured=bool(settings.OPENROUTER_API_KEY)
    )

@router.get(
    "/dashboard-stats",
    response_model=DashboardStatsResponse,
    summary="Live Dynamic KPI Dashboard Stats",
    tags=["Analytics"]
)
def get_dashboard_stats():
    """
    Returns real-time aggregated metrics computed directly from SQLite review records.
    """
    analytics = get_analytics_service()
    data = analytics.get_dashboard_kpis()
    return DashboardStatsResponse(**data)

@router.post(
    "/analyze-query",
    response_model=AnalyzeQueryResponse,
    summary="Executive Natural-Language Query Operations Analysis",
    tags=["Operations Analyst"]
)
def analyze_operations_query(payload: AnalyzeQueryRequest):
    """
    Central Managerial Workflow: Processes natural language query against Yelp dataset,
    computes hybrid retrieval, statistics, trends, priority, root causes, and generates
    a structured operational intelligence report.
    """
    analyst = get_operations_analyst_service()
    result = analyst.analyze_operations_query(query=payload.query, k=payload.k)
    return AnalyzeQueryResponse(**result)

@router.post(
    "/validate-query",
    response_model=ValidateQueryResponse,
    summary="Validate Query & Apply Guardrails",
    tags=["Guardrails"]
)
def validate_query(payload: ValidateQueryRequest):
    """
    Validates user query against prompt injection, length, and domain scope.
    """
    guard = get_guardrails_service()
    res = guard.validate_query(payload.query)
    return ValidateQueryResponse(**res)

@router.post(
    "/search",
    response_model=SearchResponse,
    summary="Hybrid Search (Dense + Sparse BM25 RRF)",
    tags=["Retrieval"]
)
def search_reviews(payload: SearchRequest):
    """
    Executes hybrid retrieval over indexed restaurant reviews using Reciprocal Rank Fusion.
    """
    guard = get_guardrails_service()
    v_res = guard.validate_query(payload.query)
    if not v_res["is_valid"]:
        raise HTTPException(status_code=400, detail=v_res["message"])

    filter_dict = {}
    if payload.category and payload.category != "All":
        filter_dict["category"] = payload.category
    if payload.business_id:
        filter_dict["business_id"] = payload.business_id

    retriever = get_hybrid_retriever()
    results = retriever.search(
        query=payload.query,
        k=payload.k,
        filter_dict=filter_dict if filter_dict else None
    )

    doc_items = [
        SearchDocItem(
            id=doc.get("id", str(uuid.uuid4())),
            text=doc.get("text", ""),
            score=round(doc.get("score", 0.0), 4),
            metadata=doc.get("metadata", {})
        )
        for doc in results
    ]

    return SearchResponse(
        query=payload.query,
        total_results=len(doc_items),
        results=doc_items
    )

@router.post(
    "/query",
    response_model=RAGQueryResponse,
    summary="RAG Grounded Operational Q&A",
    tags=["RAG Assistant"]
)
def answer_query(payload: RAGQueryRequest):
    """
    Answers complex restaurant operational queries using RAG context citations and OpenRouter LLM.
    """
    guard = get_guardrails_service()
    v_res = guard.validate_query(payload.query)
    if not v_res["is_valid"]:
        raise HTTPException(status_code=400, detail=v_res["message"])

    filter_dict = {}
    if payload.category and payload.category != "All":
        filter_dict["category"] = payload.category
    if payload.business_id:
        filter_dict["business_id"] = payload.business_id

    rag_service = get_rag_service()
    res = rag_service.answer_query(
        query=payload.query,
        k=payload.k,
        filter_dict=filter_dict if filter_dict else None,
        model=payload.model_name
    )

    return RAGQueryResponse(
        query=payload.query,
        answer=res.get("answer", ""),
        model=res.get("model_used", settings.DEFAULT_LLM_MODEL),
        citations_count=res.get("evidence_count", 0),
        citations=res.get("citations", [])
    )

@router.post(
    "/analyze",
    response_model=RootCauseResponse,
    summary="Root Cause Analysis & Evidence Linkage",
    tags=["Root Cause"]
)
def analyze_root_cause(payload: RootCauseRequest):
    """
    Analyzes observed operational symptoms against domain taxonomy and review evidence.
    """
    if not payload.symptom_query.strip():
        raise HTTPException(status_code=400, detail="Symptom query cannot be empty.")

    rc_service = get_root_cause_service()
    res = rc_service.analyze_root_cause(
        symptom_query=payload.symptom_query,
        k=payload.k,
        category=payload.category,
        business_id=payload.business_id
    )

    return RootCauseResponse(
        symptom=res.get("symptom", payload.symptom_query),
        top_root_cause=res.get("top_root_cause", "Operational Latency"),
        root_causes=res.get("root_causes", []),
        evidence_documents_count=res.get("evidence_documents_count", 0)
    )

@router.post(
    "/prioritize",
    response_model=PrioritizeResponse,
    summary="Complaint Prioritization & Ranking",
    tags=["Prioritization"]
)
def prioritize_complaints(payload: PrioritizeRequest):
    """
    Returns prioritized reviews from SQLite filtered by business, category, or priority tier.
    """
    prioritization_service = get_prioritization_service()
    res = prioritization_service.get_prioritized_complaints(
        business_id=payload.business_id,
        category=payload.category,
        priority_tier=payload.priority_tier,
        limit=payload.limit
    )

    return PrioritizeResponse(
        total_found=res.get("total_found", 0),
        summary_by_tier=res.get("summary_by_tier", {}),
        reviews=res.get("reviews", [])
    )

@router.post(
    "/agent/workflow",
    response_model=MultiAgentResponse,
    summary="Execute 5-Agent LangGraph Workflow",
    tags=["Multi-Agent"]
)
def execute_agent_workflow(payload: MultiAgentRequest):
    """
    Runs the end-to-end 5-Agent LangGraph workflow:
    Classifier -> Root Cause -> Recommendations -> Business Impact -> LLM Judge.
    """
    guard = get_guardrails_service()
    v_res = guard.validate_query(payload.complaint_text)
    if not v_res["is_valid"]:
        raise HTTPException(status_code=400, detail=v_res["message"])

    result = run_multi_agent_workflow(
        complaint_text=payload.complaint_text,
        business_id=payload.business_id,
        restaurant_name=payload.restaurant_name
    )

    judge_eval = result.get("judge_evaluation", {})

    return MultiAgentResponse(
        category=result.get("category", "Waiting Time"),
        severity_score=result.get("severity_score", 3.0),
        priority_tier=result.get("priority_tier", "Medium"),
        top_root_cause=result.get("top_root_cause", "Operational Latency"),
        recommendations=result.get("recommendations", []),
        guest_recovery_script=result.get("guest_recovery_script", ""),
        churn_risk_level=result.get("churn_risk_level", "Moderate"),
        revenue_risk_pct=result.get("revenue_risk_pct", 10.0),
        operational_urgency=result.get("operational_urgency", "P2 - Shift Manager Action"),
        judge_verdict=judge_eval.get("verdict", "APPROVED"),
        overall_quality_score=result.get("overall_quality_score") or result.get("composite_quality_score"),
        judge_mode=judge_eval.get("judge_mode", "unavailable"),
        compliance_flags=result.get("compliance_flags", []),
        retry_count=result.get("retry_count", 0),
        requires_human_review=result.get("requires_human_review", False),
        review_reasons=result.get("review_reasons", []),
        execution_trace=result.get("execution_trace", []),
        final_summary=result.get("final_summary", "")
    )

@router.post(
    "/forecast",
    response_model=ForecastResponse,
    summary="Prophet Time-Series Trend Projections",
    tags=["Forecasting"]
)
def forecast_trends(payload: ForecastRequest):
    """
    Generates 3-month (90 days) or 6-month (180 days) complaint volume or severity forecasts.
    """
    forecaster = get_forecaster()
    res = forecaster.forecast(
        business_id=payload.business_id,
        category=payload.category if payload.category != "All Categories" else None,
        metric=payload.metric,
        horizon_days=payload.horizon_days,
        freq=payload.freq
    )

    return ForecastResponse(
        status=res.get("status", "success"),
        model=res.get("model", "Prophet"),
        category=res.get("category", payload.category or "All Categories"),
        metric=res.get("metric", payload.metric),
        horizon_days=res.get("horizon_days", payload.horizon_days),
        current_avg_level=res.get("current_avg_level", 0.0),
        projected_avg_level=res.get("projected_avg_level", 0.0),
        pct_change=res.get("pct_change", 0.0),
        trend_direction=res.get("trend_direction", "Stable"),
        projected_peak=res.get("projected_peak", {}),
        historical_datapoints=res.get("historical_datapoints", 0),
        forecast_datapoints=res.get("forecast_datapoints", 0),
        forecast=res.get("forecast", []),
        history=res.get("history", [])
    )

@router.post(
    "/similar-restaurants",
    response_model=SimilarRestaurantsResponse,
    summary="Find Restaurants with Similar Operational Problems",
    tags=["Similar Restaurants"]
)
def find_similar_restaurants(payload: SimilarRestaurantsRequest):
    """
    Finds actual restaurants from the Yelp database sharing similar operational complaint profiles.
    """
    sim_svc = get_similar_restaurant_service()
    res = sim_svc.find_similar_restaurants(
        restaurant_name=payload.restaurant_name,
        business_id=payload.business_id,
        target_category=payload.target_category,
        max_stars=payload.max_stars,
        limit=payload.limit
    )

    items = [
        SimilarRestaurantItem(
            business_id=r["business_id"],
            restaurant_name=r["restaurant_name"],
            location=r["location"],
            avg_rating=r["avg_rating"],
            total_reviews=r["total_reviews"],
            complaint_count=r["complaint_count"],
            complaint_rate_pct=r["complaint_rate_pct"],
            top_complaint=r["top_complaint"],
            similarity_score=r["similarity_score"],
            recommended_action=r["recommended_action"]
        )
        for r in res.get("similar_restaurants", [])
    ]

    return SimilarRestaurantsResponse(
        status=res.get("status", "success"),
        target_restaurant=res.get("target_restaurant", "Target Profile"),
        total_evaluated=res.get("total_evaluated", 0),
        similar_restaurants=items
    )

@router.post(
    "/customer-satisfaction",
    response_model=SatisfactionResponse,
    summary="Analyze Customer Satisfaction & Churn Propensity",
    tags=["Satisfaction"]
)
def analyze_customer_satisfaction(payload: SatisfactionRequest):
    """
    Estimates customer satisfaction score and churn risk from review ratings and complaint severity.
    """
    sat_svc = get_satisfaction_service()
    res = sat_svc.analyze_satisfaction_risk(
        restaurant_name=payload.restaurant_name,
        business_id=payload.business_id
    )

    return SatisfactionResponse(
        status=res.get("status", "success"),
        restaurant_name=res.get("restaurant_name", "Aggregate"),
        total_reviews_analyzed=res.get("total_reviews_analyzed", 0),
        average_rating=res.get("average_rating", 0.0),
        complaint_rate_pct=res.get("complaint_rate_pct", 0.0),
        satisfaction_score=res.get("satisfaction_score", 0.0),
        churn_risk_tier=res.get("churn_risk_tier", "Moderate"),
        operational_urgency=res.get("operational_urgency", "Standard"),
        primary_churn_drivers=res.get("primary_churn_drivers", []),
        methodology_note=res.get("methodology_note", "")
    )

@router.post(
    "/feedback",
    response_model=FeedbackResponse,
    summary="Submit User Feedback",
    tags=["Feedback"]
)
def submit_feedback(
    payload: FeedbackRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Logs user feedback and quality ratings to SQLite and supports continuous model evaluation.
    Authenticated operational users only.
    """
    from backend.app.services.admin_service import get_admin_service
    admin_svc = get_admin_service()
    res = admin_svc.add_user_feedback(
        rating=payload.rating,
        feedback_type=payload.feedback_type,
        comment=payload.comment,
        interaction_id=payload.interaction_id
    )

    return FeedbackResponse(
        status="recorded",
        feedback_id=res.get("feedback_id", f"fb_{uuid.uuid4().hex[:8]}"),
        rating=payload.rating,
        feedback_type=payload.feedback_type,
        message="Feedback logged successfully to repository."
    )

@router.get(
    "/feedback",
    summary="List User Feedbacks",
    tags=["Feedback"]
)
@router.get(
    "/admin/feedback",
    summary="List User Feedbacks (Admin)",
    tags=["Admin", "Feedback"]
)
def list_feedbacks(
    status: Optional[str] = Query(None, description="Filter by status (Pending, Resolved, Actioned)"),
    feedback_type: Optional[str] = Query(None, description="Filter by feedback category"),
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Retrieves all feedback records submitted by operational users. Requires admin role."""
    from backend.app.services.admin_service import get_admin_service
    admin_svc = get_admin_service()
    records = admin_svc.get_feedbacks(status_filter=status, type_filter=feedback_type)
    return {"status": "success", "count": len(records), "feedbacks": records}

@router.patch(
    "/admin/feedback/{feedback_id}/status",
    summary="Update Feedback Status",
    tags=["Admin"]
)
def update_feedback_status(
    feedback_id: str,
    payload: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(require_admin)
):
    from backend.app.services.admin_service import get_admin_service
    admin_svc = get_admin_service()
    new_status = payload.get("status", "Resolved")
    success = admin_svc.update_feedback_status(feedback_id, new_status)
    if not success:
        raise HTTPException(status_code=404, detail="Feedback ID not found")
    return {"status": "success", "feedback_id": feedback_id, "new_status": new_status}

@router.delete(
    "/admin/feedback/{feedback_id}",
    summary="Delete Feedback",
    tags=["Admin"]
)
def delete_feedback(
    feedback_id: str,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    from backend.app.services.admin_service import get_admin_service
    admin_svc = get_admin_service()
    success = admin_svc.delete_feedback(feedback_id)
    if not success:
        raise HTTPException(status_code=404, detail="Feedback ID not found")
    return {"status": "success", "message": f"Feedback {feedback_id} deleted"}

@router.get(
    "/admin/reviews",
    summary="CRUD: List Reviews",
    tags=["Admin"]
)
def admin_list_reviews(
    search: str = Query("", description="Search text in reviews or restaurants"),
    category: str = Query("All", description="Operational category filter"),
    limit: int = Query(15, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Dict[str, Any] = Depends(require_admin)
):
    from backend.app.services.admin_service import get_admin_service
    admin_svc = get_admin_service()
    return admin_svc.list_reviews(search_query=search, category=category, limit=limit, offset=offset)

@router.post(
    "/admin/reviews",
    summary="CRUD: Create Review",
    tags=["Admin"]
)
def admin_create_review(
    payload: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(require_admin)
):
    from backend.app.services.admin_service import get_admin_service
    admin_svc = get_admin_service()
    return admin_svc.create_review(payload)

@router.put(
    "/admin/reviews/{review_id}",
    summary="CRUD: Update Review",
    tags=["Admin"]
)
def admin_update_review(
    review_id: str,
    payload: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(require_admin)
):
    from backend.app.services.admin_service import get_admin_service
    admin_svc = get_admin_service()
    return admin_svc.update_review(review_id, payload)

@router.delete(
    "/admin/reviews/{review_id}",
    summary="CRUD: Delete Review",
    tags=["Admin"]
)
def admin_delete_review(
    review_id: str,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    from backend.app.services.admin_service import get_admin_service
    admin_svc = get_admin_service()
    return admin_svc.delete_review(review_id)

@router.get(
    "/admin/logs",
    summary="Get System Logs",
    tags=["Admin"]
)
def admin_get_logs(
    level: Optional[str] = Query(None, description="Log level filter: INFO, WARNING, ERROR, AUDIT"),
    search: Optional[str] = Query(None, description="Search query"),
    limit: int = Query(100, ge=1, le=500),
    current_user: Dict[str, Any] = Depends(require_admin)
):
    from backend.app.services.admin_service import get_admin_service
    admin_svc = get_admin_service()
    logs = admin_svc.get_logs(level_filter=level, search_term=search, limit=limit)
    return {"status": "success", "count": len(logs), "logs": logs}

@router.get(
    "/admin/metrics",
    summary="Get System Telemetry & Metrics",
    tags=["Admin"]
)
def admin_get_metrics(
    current_user: Dict[str, Any] = Depends(require_admin)
):
    from backend.app.services.admin_service import get_admin_service
    admin_svc = get_admin_service()
    return admin_svc.get_system_telemetry()

# =============================================================================
# USER MANAGEMENT (CRUD) ENDPOINTS
# =============================================================================
@router.get(
    "/admin/users",
    summary="CRUD: List Users",
    tags=["Admin", "Users"]
)
def admin_list_users(
    search: str = Query("", description="Search username, display name, email, department"),
    role: str = Query("All", description="Role filter (admin, operations_analyst, store_manager, user)"),
    status: str = Query("All", description="Status filter (Active, Inactive, Suspended)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Retrieves operational users with optional role, status, and text search filters."""
    from backend.app.services.admin_service import get_admin_service
    admin_svc = get_admin_service()
    return admin_svc.list_users(search_query=search, role=role, status=status, limit=limit, offset=offset)

@router.post(
    "/admin/users",
    summary="CRUD: Create User",
    tags=["Admin", "Users"]
)
def admin_create_user(
    payload: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Registers a new user record in the database."""
    from backend.app.services.admin_service import get_admin_service
    admin_svc = get_admin_service()
    res = admin_svc.create_user(payload)
    if res.get("status") == "error":
        raise HTTPException(status_code=400, detail=res.get("message", "Failed to create user"))
    return res

@router.put(
    "/admin/users/{user_id}",
    summary="CRUD: Update User",
    tags=["Admin", "Users"]
)
def admin_update_user(
    user_id: str,
    payload: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Updates profile attributes, role, or credentials for an existing user."""
    from backend.app.services.admin_service import get_admin_service
    admin_svc = get_admin_service()
    res = admin_svc.update_user(user_id, payload)
    if res.get("status") == "error":
        raise HTTPException(status_code=400, detail=res.get("message", "Failed to update user"))
    return res

@router.delete(
    "/admin/users/{user_id}",
    summary="CRUD: Delete User",
    tags=["Admin", "Users"]
)
def admin_delete_user(
    user_id: str,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Deletes an operational user from the system."""
    from backend.app.services.admin_service import get_admin_service
    admin_svc = get_admin_service()
    res = admin_svc.delete_user(user_id)
    if res.get("status") == "error":
        raise HTTPException(status_code=400, detail=res.get("message", "Failed to delete user"))
    return res

@router.get(
    "/admin/evaluation/latest",
    summary="Get Latest Evaluation Benchmark Results",
    tags=["Admin", "Evaluation"]
)
def get_latest_evaluation_results(
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Returns the latest empirically computed evaluation and benchmark results JSON."""
    from pathlib import Path
    import json
    
    candidates = [
        Path("data/eval_results/latest.json"),
        Path(__file__).resolve().parent.parent.parent.parent / "data" / "eval_results" / "latest.json"
    ]
    latest_file = None
    for cand in candidates:
        if cand.exists():
            latest_file = cand
            break
            
    if not latest_file:
        raise HTTPException(
            status_code=404,
            detail="No evaluation results found. Please run backend/scripts/run_evaluation.py first."
        )
        
    with open(latest_file, "r", encoding="utf-8") as f:
        return json.load(f)

# =============================================================================
# CHAT HISTORY PERSISTENCE ENDPOINTS
# =============================================================================
@router.get(
    "/chat/history",
    summary="Get Persistent User Chat History",
    tags=["Chat History"]
)
def get_chat_history(
    username: Optional[str] = Query(None, description="Username to filter history (or None for all)"),
    limit: int = Query(50, ge=1, le=200)
):
    """Fetches persistent user inquiries and AI diagnostic answers from SQLite."""
    from backend.app.services.chat_history_service import get_chat_history_service
    svc = get_chat_history_service()
    records = svc.get_history(username=username, limit=limit)
    return {"status": "success", "count": len(records), "history": records}

@router.post(
    "/chat/history",
    summary="Save User Chat Interaction",
    tags=["Chat History"]
)
def save_chat_interaction(
    payload: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Persists a new user inquiry and AI diagnostic report into SQLite."""
    from backend.app.services.chat_history_service import get_chat_history_service
    svc = get_chat_history_service()
    query = payload.get("query", "")
    report = payload.get("report", {})
    username = payload.get("username") or current_user.get("username", "user")
    user_name = payload.get("user_name") or current_user.get("display_name", "Operations Analyst")
    user_role = payload.get("user_role") or current_user.get("role", "user")
    category = payload.get("category")
    page_source = payload.get("page_source", "Central Operations Analyst")

    entry = svc.add_interaction(
        query=query,
        report=report,
        username=username,
        user_name=user_name,
        user_role=user_role,
        category=category,
        page_source=page_source
    )
    return {
        "status": "success",
        "interaction_id": entry.get("interaction_id") or entry.get("id"),
        "id": entry.get("id"),
        "interaction": entry
    }

@router.delete(
    "/chat/history",
    summary="Clear User Chat History",
    tags=["Chat History"]
)
def clear_chat_history(
    username: Optional[str] = Query(None, description="Username whose history to clear"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Clears persistent chat history for the specified user."""
    from backend.app.services.chat_history_service import get_chat_history_service
    svc = get_chat_history_service()
    success = svc.clear_history(username=username or current_user.get("username"))
    return {"status": "success", "cleared": success}

@router.delete(
    "/chat/history/{interaction_id}",
    summary="Delete Single Chat Interaction",
    tags=["Chat History"]
)
def delete_single_chat_interaction(
    interaction_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Removes a single chat interaction from SQLite."""
    from backend.app.services.chat_history_service import get_chat_history_service
    svc = get_chat_history_service()
    success = svc.delete_interaction(interaction_id)
    return {"status": "success", "deleted": success}

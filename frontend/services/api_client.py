"""
Frontend API Client Service
Handles HTTP communication with FastAPI backend with seamless direct Python service fallback.
"""
import os
import requests
from typing import Any, Dict, List, Optional

# Backend URL configuration
BACKEND_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000")

class FrontendAPIClient:
    def __init__(self, base_url: str = BACKEND_URL):
        self.base_url = base_url.rstrip("/")

    def _is_backend_live(self) -> bool:
        try:
            r = requests.get(f"{self.base_url}/health", timeout=1.0)
            if r.status_code == 200:
                data = r.json()
                return data.get("service") == "AI-Powered Restaurant Operations & Review Assistant" or data.get("database_connected") is True
            return False
        except Exception:
            return False

    def get_health(self) -> Dict[str, Any]:
        if self._is_backend_live():
            try:
                r = requests.get(f"{self.base_url}/api/v1/health", timeout=2.0)
                if r.status_code == 200:
                    return r.json()
            except Exception:
                pass
        return {"status": "healthy (direct)", "version": "1.0.0", "database_connected": True}

    def get_dashboard_stats(self) -> Dict[str, Any]:
        if self._is_backend_live():
            try:
                r = requests.get(f"{self.base_url}/api/v1/dashboard-stats", timeout=3.0)
                if r.status_code == 200:
                    return r.json()
            except Exception:
                pass
        # Direct fallback
        from backend.app.services.analytics_service import get_analytics_service
        return get_analytics_service().get_dashboard_kpis()

    def analyze_operations_query(self, query: str, k: int = 10) -> Dict[str, Any]:
        if self._is_backend_live():
            try:
                payload = {"query": query, "k": k}
                r = requests.post(f"{self.base_url}/api/v1/analyze-query", json=payload, timeout=25.0)
                if r.status_code == 200:
                    return r.json()
                elif r.status_code == 400:
                    detail = r.json().get("detail", "Query rejected by domain guardrails.")
                    return {"status": "guardrail_rejected", "is_valid": False, "message": detail}
            except Exception:
                pass
        from backend.app.services.operations_analyst_service import get_operations_analyst_service
        return get_operations_analyst_service().analyze_operations_query(query=query, k=k)

    def validate_query(self, query: str) -> Dict[str, Any]:
        if self._is_backend_live():
            try:
                r = requests.post(f"{self.base_url}/api/v1/validate-query", json={"query": query}, timeout=2.0)
                if r.status_code == 200:
                    return r.json()
            except Exception:
                pass
        from backend.app.services.guardrails_service import get_guardrails_service
        return get_guardrails_service().validate_query(query)

    def search_reviews(self, query: str, k: int = 5, category: Optional[str] = None, business_id: Optional[str] = None) -> Dict[str, Any]:
        val = self.validate_query(query)
        if not val.get("is_valid", True):
            return {
                "query": query,
                "is_valid": False,
                "total_results": 0,
                "results": [],
                "warning": val.get("message", "This search query is outside the restaurant operations domain.")
            }

        if self._is_backend_live():
            try:
                payload = {"query": query, "k": k, "category": category, "business_id": business_id}
                r = requests.post(f"{self.base_url}/api/v1/search", json=payload, timeout=8.0)
                if r.status_code == 200:
                    data = r.json()
                    data["is_valid"] = True
                    return data
            except Exception:
                pass
        # Direct fallback
        from backend.app.retrieval.hybrid_search import get_hybrid_retriever
        retriever = get_hybrid_retriever()
        filter_dict = {}
        if category and category != "All":
            filter_dict["category"] = category
        if business_id:
            filter_dict["business_id"] = business_id
        res = retriever.search(query=query, k=k, filter_dict=filter_dict if filter_dict else None)
        return {"query": query, "is_valid": True, "total_results": len(res), "results": res}

    def query_rag(self, query: str, k: int = 5, category: Optional[str] = None, model_name: Optional[str] = None) -> Dict[str, Any]:
        if self._is_backend_live():
            try:
                payload = {"query": query, "k": k, "category": category, "model_name": model_name}
                r = requests.post(f"{self.base_url}/api/v1/query", json=payload, timeout=20.0)
                if r.status_code == 200:
                    return r.json()
            except Exception:
                pass
        # Direct fallback
        from backend.app.retrieval.rag_service import get_rag_service
        rag = get_rag_service()
        filter_dict = {"category": category} if category and category != "All" else None
        res = rag.answer_query(query=query, k=k, filter_dict=filter_dict, model=model_name)
        return {
            "query": query,
            "answer": res.get("answer", ""),
            "model": res.get("model_used", "google/gemini-2.5-flash"),
            "citations_count": res.get("evidence_count", 0),
            "citations": res.get("citations", [])
        }

    def analyze_root_cause(self, symptom_query: str, k: int = 5, category: Optional[str] = None) -> Dict[str, Any]:
        if self._is_backend_live():
            try:
                payload = {"symptom_query": symptom_query, "k": k, "category": category}
                r = requests.post(f"{self.base_url}/api/v1/analyze", json=payload, timeout=8.0)
                if r.status_code == 200:
                    return r.json()
            except Exception:
                pass
        # Direct fallback
        from backend.app.services.root_cause_service import get_root_cause_service
        rc = get_root_cause_service()
        return rc.analyze_root_cause(symptom_query=symptom_query, k=k, category=category)

    def get_prioritized_complaints(self, category: Optional[str] = None, priority_tier: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
        if self._is_backend_live():
            try:
                payload = {"category": category, "priority_tier": priority_tier, "limit": limit}
                r = requests.post(f"{self.base_url}/api/v1/prioritize", json=payload, timeout=5.0)
                if r.status_code == 200:
                    return r.json()
            except Exception:
                pass
        # Direct fallback
        from backend.app.services.prioritization_service import get_prioritization_service
        ps = get_prioritization_service()
        return ps.get_prioritized_complaints(category=category, priority_tier=priority_tier, limit=limit)

    def find_similar_restaurants(
        self,
        restaurant_name: Optional[str] = None,
        business_id: Optional[str] = None,
        target_category: Optional[str] = None,
        max_stars: Optional[float] = None,
        limit: int = 5
    ) -> Dict[str, Any]:
        if self._is_backend_live():
            try:
                payload = {
                    "restaurant_name": restaurant_name,
                    "business_id": business_id,
                    "target_category": target_category,
                    "max_stars": max_stars,
                    "limit": limit
                }
                r = requests.post(f"{self.base_url}/api/v1/similar-restaurants", json=payload, timeout=6.0)
                if r.status_code == 200:
                    return r.json()
            except Exception:
                pass
        from backend.app.services.similar_restaurant_service import get_similar_restaurant_service
        return get_similar_restaurant_service().find_similar_restaurants(
            restaurant_name=restaurant_name,
            business_id=business_id,
            target_category=target_category,
            max_stars=max_stars,
            limit=limit
        )

    def get_all_restaurants(self, min_reviews: int = 1) -> List[Dict[str, Any]]:
        from backend.app.services.similar_restaurant_service import get_similar_restaurant_service
        return get_similar_restaurant_service().get_all_restaurants(min_reviews=min_reviews)

    def analyze_customer_satisfaction(
        self,
        restaurant_name: Optional[str] = None,
        business_id: Optional[str] = None
    ) -> Dict[str, Any]:
        if self._is_backend_live():
            try:
                payload = {"restaurant_name": restaurant_name, "business_id": business_id}
                r = requests.post(f"{self.base_url}/api/v1/customer-satisfaction", json=payload, timeout=6.0)
                if r.status_code == 200:
                    return r.json()
            except Exception:
                pass
        from backend.app.services.satisfaction_service import get_satisfaction_service
        return get_satisfaction_service().analyze_satisfaction_risk(
            restaurant_name=restaurant_name,
            business_id=business_id
        )

    def execute_agent_workflow(self, complaint_text: str, restaurant_name: Optional[str] = None) -> Dict[str, Any]:
        if self._is_backend_live():
            try:
                payload = {"complaint_text": complaint_text, "restaurant_name": restaurant_name}
                r = requests.post(f"{self.base_url}/api/v1/agent/workflow", json=payload, timeout=30.0)
                if r.status_code == 200:
                    return r.json()
            except Exception:
                pass
        # Direct fallback
        from backend.app.agents.graph import run_multi_agent_workflow
        res = run_multi_agent_workflow(complaint_text=complaint_text, restaurant_name=restaurant_name)
        judge_eval = res.get("judge_evaluation", {})
        return {
            "category": res.get("category", "Waiting Time"),
            "severity_score": res.get("severity_score", 3.0),
            "priority_tier": res.get("priority_tier", "Medium"),
            "top_root_cause": res.get("top_root_cause", "Operational Latency"),
            "recommendations": res.get("recommendations", []),
            "guest_recovery_script": res.get("guest_recovery_script", ""),
            "churn_risk_level": res.get("churn_risk_level", "Moderate"),
            "revenue_risk_pct": res.get("revenue_risk_pct", 10.0),
            "operational_urgency": res.get("operational_urgency", "P2 - Shift Manager Action"),
            "judge_verdict": judge_eval.get("verdict", "APPROVED"),
            "overall_quality_score": res.get("overall_quality_score", 0.90),
            "requires_human_review": res.get("requires_human_review", False),
            "review_reasons": res.get("review_reasons", []),
            "execution_trace": res.get("execution_trace", []),
            "final_summary": res.get("final_summary", "")
        }

    def forecast_trends(self, category: Optional[str] = None, horizon_days: int = 90) -> Dict[str, Any]:
        if self._is_backend_live():
            try:
                payload = {"category": category, "horizon_days": horizon_days, "metric": "complaint_count", "freq": "W"}
                r = requests.post(f"{self.base_url}/api/v1/forecast", json=payload, timeout=12.0)
                if r.status_code == 200:
                    return r.json()
            except Exception:
                pass
        # Direct fallback
        from backend.app.forecasting.prophet_forecast import get_forecaster
        f = get_forecaster()
        return f.forecast(category=category if category != "All Categories" else None, horizon_days=horizon_days, metric="complaint_count", freq="W")

    def submit_feedback(self, rating: int, feedback_type: str = "general", comment: Optional[str] = None, user_name: str = "Operations User") -> Dict[str, Any]:
        if self._is_backend_live():
            try:
                payload = {"rating": rating, "feedback_type": feedback_type, "comment": comment}
                r = requests.post(f"{self.base_url}/api/v1/feedback", json=payload, timeout=3.0)
                if r.status_code == 200:
                    return r.json()
            except Exception:
                pass
        from backend.app.services.admin_service import get_admin_service
        res = get_admin_service().add_user_feedback(
            rating=rating,
            feedback_type=feedback_type,
            comment=comment,
            user_name=user_name
        )
        return {
            "status": "recorded",
            "feedback_id": res.get("feedback_id"),
            "rating": rating,
            "feedback_type": feedback_type,
            "message": "Feedback logged successfully."
        }

    # -------------------------------------------------------------------------
    # ADMIN CLIENT METHODS
    # -------------------------------------------------------------------------
    def get_feedbacks(self, status: Optional[str] = None, feedback_type: Optional[str] = None) -> List[Dict[str, Any]]:
        if self._is_backend_live():
            try:
                params = {}
                if status and status != "All":
                    params["status"] = status
                if feedback_type and feedback_type != "All":
                    params["feedback_type"] = feedback_type
                r = requests.get(f"{self.base_url}/api/v1/feedback", params=params, timeout=3.0)
                if r.status_code == 200:
                    return r.json().get("feedbacks", [])
            except Exception:
                pass
        from backend.app.services.admin_service import get_admin_service
        return get_admin_service().get_feedbacks(status_filter=status, type_filter=feedback_type)

    def update_feedback_status(self, feedback_id: str, new_status: str) -> bool:
        if self._is_backend_live():
            try:
                r = requests.patch(
                    f"{self.base_url}/api/v1/admin/feedback/{feedback_id}/status",
                    json={"status": new_status},
                    timeout=3.0
                )
                if r.status_code == 200:
                    return True
            except Exception:
                pass
        from backend.app.services.admin_service import get_admin_service
        return get_admin_service().update_feedback_status(feedback_id, new_status)

    def delete_feedback(self, feedback_id: str) -> bool:
        if self._is_backend_live():
            try:
                r = requests.delete(f"{self.base_url}/api/v1/admin/feedback/{feedback_id}", timeout=3.0)
                if r.status_code == 200:
                    return True
            except Exception:
                pass
        from backend.app.services.admin_service import get_admin_service
        return get_admin_service().delete_feedback(feedback_id)

    def ingest_csv(self, df, admin_user: str = "admin") -> Dict[str, Any]:
        from backend.app.services.admin_service import get_admin_service
        return get_admin_service().ingest_csv(df, admin_user=admin_user)

    def list_admin_reviews(self, search: str = "", category: str = "All", limit: int = 15, offset: int = 0) -> Dict[str, Any]:
        if self._is_backend_live():
            try:
                params = {"search": search, "category": category, "limit": limit, "offset": offset}
                r = requests.get(f"{self.base_url}/api/v1/admin/reviews", params=params, timeout=3.0)
                if r.status_code == 200:
                    return r.json()
            except Exception:
                pass
        from backend.app.services.admin_service import get_admin_service
        return get_admin_service().list_reviews(search_query=search, category=category, limit=limit, offset=offset)

    def create_admin_review(self, data: Dict[str, Any], admin_user: str = "admin") -> Dict[str, Any]:
        if self._is_backend_live():
            try:
                r = requests.post(f"{self.base_url}/api/v1/admin/reviews", json=data, timeout=3.0)
                if r.status_code == 200:
                    return r.json()
            except Exception:
                pass
        from backend.app.services.admin_service import get_admin_service
        return get_admin_service().create_review(data, admin_user=admin_user)

    def update_admin_review(self, review_id: str, data: Dict[str, Any], admin_user: str = "admin") -> Dict[str, Any]:
        if self._is_backend_live():
            try:
                r = requests.put(f"{self.base_url}/api/v1/admin/reviews/{review_id}", json=data, timeout=3.0)
                if r.status_code == 200:
                    return r.json()
            except Exception:
                pass
        from backend.app.services.admin_service import get_admin_service
        return get_admin_service().update_review(review_id, data, admin_user=admin_user)

    def delete_admin_review(self, review_id: str, admin_user: str = "admin") -> Dict[str, Any]:
        if self._is_backend_live():
            try:
                r = requests.delete(f"{self.base_url}/api/v1/admin/reviews/{review_id}", timeout=3.0)
                if r.status_code == 200:
                    return r.json()
            except Exception:
                pass
        from backend.app.services.admin_service import get_admin_service
        return get_admin_service().delete_review(review_id, admin_user=admin_user)

    def get_admin_logs(self, level: Optional[str] = None, search: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        if self._is_backend_live():
            try:
                params = {"limit": limit}
                if level and level != "ALL":
                    params["level"] = level
                if search:
                    params["search"] = search
                r = requests.get(f"{self.base_url}/api/v1/admin/logs", params=params, timeout=3.0)
                if r.status_code == 200:
                    return r.json().get("logs", [])
            except Exception:
                pass
        from backend.app.services.admin_service import get_admin_service
        return get_admin_service().get_logs(level_filter=level, search_term=search, limit=limit)

    def get_admin_metrics(self) -> Dict[str, Any]:
        if self._is_backend_live():
            try:
                r = requests.get(f"{self.base_url}/api/v1/admin/metrics", timeout=3.0)
                if r.status_code == 200:
                    return r.json()
            except Exception:
                pass
        from backend.app.services.admin_service import get_admin_service
        return get_admin_service().get_system_telemetry()

    # -------------------------------------------------------------------------
    # USER MANAGEMENT (CRUD)
    # -------------------------------------------------------------------------
    def list_users(self, search: str = "", role: str = "All", status: str = "All", limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        if self._is_backend_live():
            try:
                params = {"search": search, "role": role, "status": status, "limit": limit, "offset": offset}
                r = requests.get(f"{self.base_url}/api/v1/admin/users", params=params, timeout=3.0)
                if r.status_code == 200:
                    return r.json()
            except Exception:
                pass
        from backend.app.services.admin_service import get_admin_service
        return get_admin_service().list_users(search_query=search, role=role, status=status, limit=limit, offset=offset)

    def create_user(self, payload: Dict[str, Any], admin_user: str = "admin") -> Dict[str, Any]:
        if self._is_backend_live():
            try:
                r = requests.post(f"{self.base_url}/api/v1/admin/users", json=payload, timeout=3.0)
                if r.status_code == 200:
                    return r.json()
            except Exception:
                pass
        from backend.app.services.admin_service import get_admin_service
        return get_admin_service().create_user(payload, admin_user=admin_user)

    def update_user(self, user_id: str, payload: Dict[str, Any], admin_user: str = "admin") -> Dict[str, Any]:
        if self._is_backend_live():
            try:
                r = requests.put(f"{self.base_url}/api/v1/admin/users/{user_id}", json=payload, timeout=3.0)
                if r.status_code == 200:
                    return r.json()
            except Exception:
                pass
        from backend.app.services.admin_service import get_admin_service
        return get_admin_service().update_user(user_id, payload, admin_user=admin_user)

    def delete_user(self, user_id: str, admin_user: str = "admin") -> Dict[str, Any]:
        if self._is_backend_live():
            try:
                r = requests.delete(f"{self.base_url}/api/v1/admin/users/{user_id}", timeout=3.0)
                if r.status_code == 200:
                    return r.json()
            except Exception:
                pass
        from backend.app.services.admin_service import get_admin_service
        return get_admin_service().delete_user(user_id, admin_user=admin_user)

    # -------------------------------------------------------------------------
    # PERSISTENT CHAT HISTORY METHODS
    # -------------------------------------------------------------------------
    def get_chat_history(self, username: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves persistent chat interactions for the user from backend or SQLite fallback."""
        if self._is_backend_live():
            try:
                params = {"limit": limit}
                if username:
                    params["username"] = username
                r = requests.get(f"{self.base_url}/api/v1/chat/history", params=params, timeout=3.0)
                if r.status_code == 200:
                    return r.json().get("history", [])
            except Exception:
                pass
        from backend.app.services.chat_history_service import get_chat_history_service
        return get_chat_history_service().get_history(username=username, limit=limit)

    def save_chat_interaction(
        self,
        query: str,
        report: Dict[str, Any],
        username: str = "user",
        user_name: str = "Operations Analyst",
        user_role: str = "user",
        category: Optional[str] = None,
        page_source: str = "Central Operations Analyst"
    ) -> Dict[str, Any]:
        """Saves a new inquiry and diagnostic report into persistent SQLite storage."""
        if self._is_backend_live():
            try:
                payload = {
                    "query": query,
                    "report": report,
                    "username": username,
                    "user_name": user_name,
                    "user_role": user_role,
                    "category": category,
                    "page_source": page_source
                }
                r = requests.post(f"{self.base_url}/api/v1/chat/history", json=payload, timeout=3.0)
                if r.status_code == 200:
                    return r.json().get("interaction", {})
            except Exception:
                pass
        from backend.app.services.chat_history_service import get_chat_history_service
        return get_chat_history_service().add_interaction(
            query=query,
            report=report,
            username=username,
            user_name=user_name,
            user_role=user_role,
            category=category,
            page_source=page_source
        )

    def clear_chat_history(self, username: Optional[str] = None) -> bool:
        """Clears chat history for the user from SQLite storage."""
        if self._is_backend_live():
            try:
                params = {}
                if username:
                    params["username"] = username
                r = requests.delete(f"{self.base_url}/api/v1/chat/history", params=params, timeout=3.0)
                if r.status_code == 200:
                    return r.json().get("cleared", True)
            except Exception:
                pass
        from backend.app.services.chat_history_service import get_chat_history_service
        return get_chat_history_service().clear_history(username=username)

    def delete_chat_interaction(self, interaction_id: str) -> bool:
        """Removes a single chat interaction from SQLite storage."""
        if self._is_backend_live():
            try:
                r = requests.delete(f"{self.base_url}/api/v1/chat/history/{interaction_id}", timeout=3.0)
                if r.status_code == 200:
                    return r.json().get("deleted", True)
            except Exception:
                pass
        from backend.app.services.chat_history_service import get_chat_history_service
        return get_chat_history_service().delete_interaction(interaction_id)


# Global client
api_client = FrontendAPIClient()

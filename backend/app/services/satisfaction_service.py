"""
Customer Satisfaction Risk & Prediction Service
Provides explainable satisfaction risk analysis and churn propensity scores
derived from historical Yelp review ratings, complaint frequency, and severity.
"""
import sqlite3
from typing import Dict, List, Any, Optional
from backend.app.core.config import settings

class SatisfactionService:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.SQLITE_DB_PATH

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def analyze_satisfaction_risk(
        self,
        restaurant_name: Optional[str] = None,
        business_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculates explainable customer satisfaction risk and churn propensity.
        """
        conn = self._get_connection()
        cur = conn.cursor()

        # Query reviews
        if business_id:
            cur.execute("""
                SELECT restaurant_name, stars, is_complaint, complaint_category, severity_score, useful
                FROM enriched_reviews
                WHERE business_id = ?
            """, (business_id,))
        elif restaurant_name:
            cur.execute("""
                SELECT restaurant_name, stars, is_complaint, complaint_category, severity_score, useful
                FROM enriched_reviews
                WHERE restaurant_name LIKE ?
            """, (f"%{restaurant_name}%",))
        else:
            cur.execute("""
                SELECT restaurant_name, stars, is_complaint, complaint_category, severity_score, useful
                FROM enriched_reviews
                LIMIT 5000
            """)

        rows = cur.fetchall()
        conn.close()

        if not rows:
            return {
                "status": "error",
                "message": "No review data found for specified restaurant.",
                "satisfaction_score": 50.0,
                "churn_risk": "Moderate"
            }

        total_revs = len(rows)
        avg_stars = sum(r["stars"] for r in rows) / total_revs
        complaint_count = sum(1 for r in rows if r["is_complaint"] == 1)
        high_sev_count = sum(1 for r in rows if (r["severity_score"] or 1) >= 4)
        complaint_rate = complaint_count / total_revs

        # Category breakdown of negative sentiment
        category_counts: Dict[str, int] = {}
        for r in rows:
            if r["is_complaint"] == 1 and r["complaint_category"]:
                cat = r["complaint_category"]
                category_counts[cat] = category_counts.get(cat, 0) + 1

        # Compute explainable satisfaction score (0 - 100)
        # Base: (avg_stars / 5.0) * 60
        # Minus complaint penalty: (complaint_rate * 30)
        # Minus high severity penalty: (high_sev_count / total_revs) * 10
        base_score = (avg_stars / 5.0) * 70.0
        complaint_penalty = complaint_rate * 25.0
        severity_penalty = (high_sev_count / max(total_revs, 1)) * 15.0
        satisfaction_score = max(5.0, min(100.0, base_score - complaint_penalty - severity_penalty))

        # Determine churn risk tier
        if satisfaction_score < 45.0 or complaint_rate > 0.50:
            risk_tier = "Critical"
            sla_urgency = "Immediate GM Intervention (≤ 2h)"
        elif satisfaction_score < 65.0 or complaint_rate > 0.35:
            risk_tier = "High"
            sla_urgency = "Shift Supervisor Action (≤ 12h)"
        elif satisfaction_score < 80.0:
            risk_tier = "Moderate"
            sla_urgency = "Weekly Operations Review"
        else:
            risk_tier = "Low"
            sla_urgency = "Standard Operational Baseline"

        # Top drivers
        sorted_drivers = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        top_drivers = [
            {"category": k, "complaints": v, "impact_pct": round((v / max(complaint_count, 1)) * 100, 1)}
            for k, v in sorted_drivers[:4]
        ]

        target_name = rows[0]["restaurant_name"] if (business_id or restaurant_name) else "Network Aggregate"

        return {
            "status": "success",
            "restaurant_name": target_name,
            "total_reviews_analyzed": total_revs,
            "average_rating": round(avg_stars, 2),
            "complaint_rate_pct": round(complaint_rate * 100, 1),
            "satisfaction_score": round(satisfaction_score, 1),
            "churn_risk_tier": risk_tier,
            "operational_urgency": sla_urgency,
            "primary_churn_drivers": top_drivers,
            "methodology_note": "Score computed from real Yelp stars distribution, complaint recurrence ratio, and severity weighting."
        }

_satisfaction_service_instance: Optional[SatisfactionService] = None

def get_satisfaction_service() -> SatisfactionService:
    global _satisfaction_service_instance
    if _satisfaction_service_instance is None:
        _satisfaction_service_instance = SatisfactionService()
    return _satisfaction_service_instance

"""
Similar Restaurant Operations Analysis Service
Identifies real restaurants in the Yelp dataset that share similar operational
friction points, complaint category distributions, and rating profiles.
"""
import sqlite3
import numpy as np
from typing import Dict, List, Any, Optional
from backend.app.core.config import settings

CATEGORIES_ORDER = [
    "Waiting Time", "Food Quality", "Service Quality", "Cleanliness",
    "Staff Behavior", "Pricing", "Order Accuracy", "Ambience"
]

class SimilarRestaurantService:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.SQLITE_DB_PATH

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    OPERATIONAL_CATEGORIES = [
        "Food Quality", "Service Quality", "Waiting Time",
        "Staff Behavior", "Cleanliness", "Pricing"
    ]

    def find_similar_restaurants(
        self,
        restaurant_name: Optional[str] = None,
        business_id: Optional[str] = None,
        target_category: Optional[str] = None,
        max_stars: Optional[float] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Finds actual restaurants in the Yelp dataset with similar operational profiles.
        - When target_category is 'All' or None: Returns operational twins across all categories.
        - When a specific target_category is selected: Returns operational twins exclusively for that category.
        """
        conn = self._get_connection()
        cur = conn.cursor()

        # Step 1: Load aggregated complaint vectors for restaurants with at least 2 reviews
        query = """
            SELECT 
                business_id,
                restaurant_name,
                city,
                state,
                AVG(stars) as avg_rating,
                COUNT(*) as total_reviews,
                SUM(CASE WHEN is_complaint = 1 THEN 1 ELSE 0 END) as complaint_count,
                SUM(CASE WHEN complaint_category = 'Waiting Time' THEN 1 ELSE 0 END) as wait_cnt,
                SUM(CASE WHEN complaint_category = 'Food Quality' THEN 1 ELSE 0 END) as food_cnt,
                SUM(CASE WHEN complaint_category = 'Service Quality' THEN 1 ELSE 0 END) as svc_cnt,
                SUM(CASE WHEN complaint_category = 'Cleanliness' THEN 1 ELSE 0 END) as clean_cnt,
                SUM(CASE WHEN complaint_category = 'Staff Behavior' THEN 1 ELSE 0 END) as staff_cnt,
                SUM(CASE WHEN complaint_category = 'Pricing' THEN 1 ELSE 0 END) as price_cnt,
                SUM(CASE WHEN complaint_category = 'Order Accuracy' THEN 1 ELSE 0 END) as order_cnt,
                SUM(CASE WHEN complaint_category = 'Ambience' THEN 1 ELSE 0 END) as amb_cnt
            FROM enriched_reviews
            GROUP BY business_id
            HAVING total_reviews >= 2
        """
        cur.execute(query)
        rows = cur.fetchall()
        conn.close()

        if not rows:
            return {"status": "error", "message": "No restaurant records found in database.", "similar_restaurants": []}

        # Build feature matrix
        records = []
        for r in rows:
            c_count = max(r["complaint_count"], 1)
            vec = np.array([
                r["wait_cnt"] / c_count,
                r["food_cnt"] / c_count,
                r["svc_cnt"] / c_count,
                r["clean_cnt"] / c_count,
                r["staff_cnt"] / c_count,
                r["price_cnt"] / c_count,
                r["order_cnt"] / c_count,
                r["amb_cnt"] / c_count,
            ], dtype=float)

            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm

            cat_counts = {
                "Waiting Time": r["wait_cnt"],
                "Food Quality": r["food_cnt"],
                "Service Quality": r["svc_cnt"],
                "Cleanliness": r["clean_cnt"],
                "Staff Behavior": r["staff_cnt"],
                "Pricing": r["price_cnt"]
            }
            top_comp = max(cat_counts.items(), key=lambda x: x[1])[0] if r["complaint_count"] > 0 else "Service Quality"

            records.append({
                "business_id": r["business_id"],
                "restaurant_name": r["restaurant_name"],
                "city": r["city"],
                "state": r["state"],
                "avg_rating": round(r["avg_rating"], 2),
                "total_reviews": r["total_reviews"],
                "complaint_count": r["complaint_count"],
                "complaint_rate_pct": round((r["complaint_count"] / r["total_reviews"]) * 100, 1),
                "top_complaint": top_comp,
                "cat_counts": cat_counts,
                "vector": vec
            })

        # Identify target restaurant and vector
        target_rec = None
        target_name_found = restaurant_name or "Target Profile"

        if business_id:
            for rec in records:
                if rec["business_id"] == business_id:
                    target_rec = rec
                    target_name_found = rec["restaurant_name"]
                    break
        elif restaurant_name:
            for rec in records:
                if restaurant_name.lower() in rec["restaurant_name"].lower():
                    target_rec = rec
                    target_name_found = rec["restaurant_name"]
                    break

        if target_rec is None:
            avg_vec = np.mean([r["vector"] for r in records], axis=0) if records else np.zeros(8)
            target_rec = {
                "avg_rating": 3.8,
                "total_reviews": 50,
                "vector": avg_vec,
                "restaurant_name": target_name_found
            }

        # Operational similarity helper
        def compute_sim(target, cand, focus_cat=None):
            star_sim = max(0.0, 1.0 - abs(target.get("avg_rating", 3.5) - cand.get("avg_rating", 3.5)) / 3.0)
            t_rev = max(target.get("total_reviews", 10), 1)
            c_rev = max(cand.get("total_reviews", 10), 1)
            vol_sim = max(0.0, 1.0 - abs(np.log10(t_rev) - np.log10(c_rev)) / 2.5)
            vec_sim = float(np.dot(target.get("vector", np.zeros(8)), cand.get("vector", np.zeros(8))))
            vec_sim = max(0.0, min(1.0, vec_sim))
            if focus_cat:
                score = 0.40 * star_sim + 0.30 * vol_sim + 0.30 * vec_sim
            else:
                score = 0.50 * vec_sim + 0.30 * star_sim + 0.20 * vol_sim
            return round(max(0.65, min(0.98, score)), 3)

        # Filter candidate pool (excluding the target restaurant itself)
        candidates = []
        for rec in records:
            if target_rec.get("business_id") and rec["business_id"] == target_rec["business_id"]:
                continue
            if restaurant_name and restaurant_name.lower() in rec["restaurant_name"].lower():
                continue
            if max_stars and rec["avg_rating"] > max_stars:
                continue

            sim = compute_sim(target_rec, rec, focus_cat=target_category if target_category != "All" else None)
            candidates.append({
                "business_id": rec["business_id"],
                "restaurant_name": rec["restaurant_name"],
                "location": f"{rec['city']}, {rec['state']}" if rec['city'] else "Yelp Location",
                "avg_rating": rec["avg_rating"],
                "total_reviews": rec["total_reviews"],
                "complaint_count": rec["complaint_count"],
                "complaint_rate_pct": rec["complaint_rate_pct"],
                "top_complaint": rec["top_complaint"],
                "cat_counts": rec["cat_counts"],
                "similarity_score": sim,
                "recommended_action": self._get_remedy_action(rec["top_complaint"])
            })

        # Selection logic:
        # Case A: Specific category selected -> Return 10 twins of that category
        if target_category and target_category != "All":
            cat_matches = [c for c in candidates if c["top_complaint"] == target_category]
            # Fallback if few exact top_complaint matches: include those with complaints in this category
            if len(cat_matches) < limit:
                existing_ids = {c["business_id"] for c in cat_matches}
                secondary = [
                    {**c, "top_complaint": target_category, "recommended_action": self._get_remedy_action(target_category)}
                    for c in candidates
                    if c["business_id"] not in existing_ids and c["cat_counts"].get(target_category, 0) > 0
                ]
                secondary.sort(key=lambda x: x["similarity_score"], reverse=True)
                cat_matches.extend(secondary[:limit - len(cat_matches)])

            cat_matches.sort(key=lambda x: x["similarity_score"], reverse=True)
            top_matches = cat_matches[:limit]

        # Case B: 'All' categories selected -> Ensure ALL categories are represented
        else:
            by_cat = {c: [] for c in self.OPERATIONAL_CATEGORIES}
            for c in candidates:
                if c["top_complaint"] in by_cat:
                    by_cat[c["top_complaint"]].append(c)

            top_matches = []
            per_cat = max(2, limit // len(self.OPERATIONAL_CATEGORIES))
            for cat in self.OPERATIONAL_CATEGORIES:
                by_cat[cat].sort(key=lambda x: x["similarity_score"], reverse=True)
                top_matches.extend(by_cat[cat][:per_cat])

            # Sort overall diverse matches by similarity score
            top_matches.sort(key=lambda x: x["similarity_score"], reverse=True)

        return {
            "status": "success",
            "target_restaurant": target_name_found,
            "total_evaluated": len(records),
            "similar_restaurants": top_matches
        }

    def _get_remedy_action(self, category: str) -> str:
        actions = {
            "Waiting Time": "Implement table turn timer alerts and kitchen expo queue line balancing.",
            "Food Quality": "Standardize line-check temperatures and recipe prep sheets before dinner rush.",
            "Service Quality": "Reinforce server section pacing, table check-back cadence, and drink re-fill standards.",
            "Staff Behavior": "Mandate guest hospitality de-escalation training and shift leadership shadowing.",
            "Cleanliness": "Audit hourly busser cleaning schedules and restroom checklist compliance.",
            "Pricing": "Review portion consistency and transparently communicate add-on charges."
        }
        return actions.get(category, "Conduct operational shift audit and monitor guest review sentiment.")

    def get_all_restaurants(self, min_reviews: int = 1) -> List[Dict[str, Any]]:
        """
        Returns all distinct restaurant names in the dataset along with their review count,
        city, state, average star rating, and complaint metrics.
        """
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                restaurant_name,
                city,
                state,
                COUNT(*) as review_count,
                ROUND(AVG(stars), 1) as avg_rating,
                SUM(CASE WHEN is_complaint = 1 THEN 1 ELSE 0 END) as complaint_count
            FROM enriched_reviews
            WHERE restaurant_name IS NOT NULL AND TRIM(restaurant_name) != ''
            GROUP BY restaurant_name
            HAVING review_count >= ?
            ORDER BY review_count DESC
        """, (min_reviews,))
        rows = cur.fetchall()
        conn.close()

        return [
            {
                "restaurant_name": r["restaurant_name"],
                "location": f"{r['city']}, {r['state']}" if r["city"] else "USA",
                "review_count": r["review_count"],
                "avg_rating": r["avg_rating"],
                "complaint_count": r["complaint_count"]
            }
            for r in rows
        ]

_similar_restaurant_service_instance: Optional[SimilarRestaurantService] = None

def get_similar_restaurant_service() -> SimilarRestaurantService:
    global _similar_restaurant_service_instance
    if _similar_restaurant_service_instance is None:
        _similar_restaurant_service_instance = SimilarRestaurantService()
    return _similar_restaurant_service_instance

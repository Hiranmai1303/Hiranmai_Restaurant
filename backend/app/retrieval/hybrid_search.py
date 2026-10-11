"""
Hybrid Search Retriever using Reciprocal Rank Fusion (RRF)
Combines BM25 Keyword Search with Dense Vector Retrieval from ChromaDB.
Supports automatic Hotel/Restaurant entity detection to filter results
exclusively to that hotel when mentioned, and fleet-wide across all when absent.
"""
import re
import sqlite3
from typing import Any, Dict, List, Optional
from backend.app.core.config import settings
from backend.app.retrieval.bm25_search import BM25Retriever, get_bm25_retriever
from backend.app.vectorstore.chroma_store import ChromaVectorStore, get_vector_store

class HybridRetriever:
    def __init__(
        self,
        vector_store: Optional[ChromaVectorStore] = None,
        bm25_retriever: Optional[BM25Retriever] = None,
        rrf_k: int = 60,
        vector_weight: float = 0.5,
        bm25_weight: float = 0.5,
        db_path: Optional[str] = None
    ):
        self.vector_store = vector_store or get_vector_store()
        self.bm25 = bm25_retriever or get_bm25_retriever()
        self.rrf_k = rrf_k
        self.vector_weight = vector_weight
        self.bm25_weight = bm25_weight
        self.db_path = db_path or settings.SQLITE_DB_PATH
        self._known_restaurants: Optional[List[str]] = None

    def _get_known_restaurants(self) -> List[str]:
        """Loads and caches known restaurant/hotel names sorted by string length descending."""
        if self._known_restaurants is None:
            rests = []
            try:
                conn = sqlite3.connect(self.db_path)
                cur = conn.cursor()
                cur.execute("SELECT DISTINCT restaurant_name FROM enriched_reviews WHERE restaurant_name IS NOT NULL")
                rows = cur.fetchall()
                conn.close()
                for r in rows:
                    if r[0] and len(r[0].strip()) >= 3:
                        rests.append(r[0].strip())
            except Exception:
                pass
            # Sort by length descending so longer specific names match first
            self._known_restaurants = sorted(rests, key=lambda x: len(x), reverse=True)
        return self._known_restaurants

    def detect_restaurant(self, query: str) -> Optional[str]:
        """Detects if any hotel or restaurant name is explicitly mentioned in the query using whole word boundary matching."""
        if not query:
            return None
        q_lower = query.lower()
        for rest in self._get_known_restaurants():
            # Whole-word regex match prevents false positives (e.g., 'lukewarm' matching restaurant 'Luke')
            pattern = rf"\b{re.escape(rest.lower())}\b"
            if re.search(pattern, q_lower):
                return rest
        return None

    def search(
        self,
        query: str,
        k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None,
        fetch_k: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Execute Hybrid Search combining BM25 and Vector Search using Reciprocal Rank Fusion (RRF).
        If a hotel/restaurant name is mentioned in the query, restricts results ONLY to that hotel.
        """
        if not query or not query.strip():
            return []

        # Make a shallow copy of filter_dict
        f_dict = dict(filter_dict) if filter_dict else {}

        # Detect hotel/restaurant name if not explicitly provided
        detected_restaurant = f_dict.get("restaurant") or self.detect_restaurant(query)
        if detected_restaurant:
            f_dict["restaurant"] = detected_restaurant
            fetch_k = max(fetch_k, k * 3)

        # 1. Retrieve top candidates from Dense Vector Store
        vector_results = self.vector_store.similarity_search(
            query=query,
            k=fetch_k,
            filter_dict=f_dict if f_dict else None
        )

        # 2. Retrieve top candidates from Sparse BM25
        bm25_results = self.bm25.search(
            query=query,
            k=fetch_k
        )

        # 3. Apply Reciprocal Rank Fusion (RRF)
        doc_pool: Dict[str, Dict[str, Any]] = {}
        rrf_scores: Dict[str, float] = {}

        # Process Vector Ranks
        for rank, item in enumerate(vector_results, 1):
            doc_id = item["id"]
            if not doc_id:
                continue
            doc_pool[doc_id] = {
                "id": doc_id,
                "text": item["text"],
                "metadata": item["metadata"],
                "vector_rank": rank,
                "vector_score": item["score"],
                "bm25_rank": None,
                "bm25_score": None
            }
            score_contrib = self.vector_weight / (self.rrf_k + rank)
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + score_contrib

        # Process BM25 Ranks
        for rank, item in enumerate(bm25_results, 1):
            doc_id = item["id"]
            if not doc_id:
                continue
            if doc_id in doc_pool:
                doc_pool[doc_id]["bm25_rank"] = rank
                doc_pool[doc_id]["bm25_score"] = item["score"]
            else:
                doc_pool[doc_id] = {
                    "id": doc_id,
                    "text": item["text"],
                    "metadata": item["metadata"],
                    "vector_rank": None,
                    "vector_score": None,
                    "bm25_rank": rank,
                    "bm25_score": item["score"]
                }
            score_contrib = self.bm25_weight / (self.rrf_k + rank)
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + score_contrib

        # Apply metadata filtering (including restaurant restriction)
        if f_dict:
            filtered_ids = set()
            for doc_id, doc in doc_pool.items():
                match = True
                meta = doc.get("metadata", {})
                for k_filter, v_filter in f_dict.items():
                    if k_filter == "category" and v_filter and v_filter != "All":
                        if meta.get("category") != v_filter:
                            match = False
                            break
                    elif k_filter == "restaurant" and v_filter:
                        doc_rest = str(meta.get("restaurant", "")).lower()
                        target_rest = str(v_filter).lower()
                        if doc_rest != target_rest and target_rest not in doc_rest and doc_rest not in target_rest:
                            match = False
                            break
                    elif meta.get(k_filter) != v_filter:
                        match = False
                        break
                if match:
                    filtered_ids.add(doc_id)
            rrf_scores = {doc_id: s for doc_id, s in rrf_scores.items() if doc_id in filtered_ids}

        # 4. Direct SQLite Fallback if fewer results than k for a specific detected hotel
        if detected_restaurant and len(rrf_scores) < k:
            try:
                conn = sqlite3.connect(self.db_path)
                cur = conn.cursor()
                cat_filter = f_dict.get("category")
                if cat_filter and cat_filter != "All":
                    cur.execute("""
                        SELECT review_id, text, stars, date, complaint_category, aspect, restaurant_name, city, state, severity_score, priority_score
                        FROM enriched_reviews
                        WHERE LOWER(restaurant_name) LIKE ? AND complaint_category = ?
                        ORDER BY is_complaint DESC, severity_score DESC, stars ASC
                        LIMIT ?
                    """, (f"%{detected_restaurant.lower()}%", cat_filter, k))
                else:
                    cur.execute("""
                        SELECT review_id, text, stars, date, complaint_category, aspect, restaurant_name, city, state, severity_score, priority_score
                        FROM enriched_reviews
                        WHERE LOWER(restaurant_name) LIKE ?
                        ORDER BY is_complaint DESC, severity_score DESC, stars ASC
                        LIMIT ?
                    """, (f"%{detected_restaurant.lower()}%", k))
                rows = cur.fetchall()
                conn.close()

                for row in rows:
                    r_id, r_text, r_stars, r_date, r_cat, r_aspect, r_name, r_city, r_state, r_sev, r_prio = row
                    if r_id and r_id not in doc_pool:
                        doc_pool[r_id] = {
                            "id": r_id,
                            "text": r_text,
                            "metadata": {
                                "restaurant": r_name,
                                "rating": r_stars,
                                "date": r_date,
                                "category": r_cat,
                                "complaint_type": r_aspect,
                                "city": r_city,
                                "state": r_state,
                                "severity_score": r_sev,
                                "priority_score": r_prio
                            },
                            "vector_rank": None,
                            "vector_score": None,
                            "bm25_rank": None,
                            "bm25_score": None
                        }
                        rrf_scores[r_id] = 0.5
            except Exception:
                pass

        # 5. Sort documents by final combined RRF score
        sorted_doc_ids = sorted(
            rrf_scores.keys(),
            key=lambda d_id: rrf_scores[d_id],
            reverse=True
        )[:k]

        # 6. Format output
        results = []
        for doc_id in sorted_doc_ids:
            doc_info = doc_pool[doc_id]
            doc_info["rrf_score"] = round(rrf_scores[doc_id], 6)
            doc_info["retrieval_type"] = "hybrid_rrf"
            results.append(doc_info)

        return results

# Global singleton
_hybrid_instance: Optional[HybridRetriever] = None

def get_hybrid_retriever() -> HybridRetriever:
    global _hybrid_instance
    if _hybrid_instance is None:
        _hybrid_instance = HybridRetriever()
    return _hybrid_instance

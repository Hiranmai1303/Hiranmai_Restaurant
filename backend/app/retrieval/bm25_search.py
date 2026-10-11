"""
BM25 Keyword Search Retrieval Module
Implements BM25Okapi search over restaurant complaint corpus with tokenization,
stemming/normalization, and keyword relevance scoring.
"""
import re
from typing import Any, Dict, List, Optional
from rank_bm25 import BM25Okapi
from backend.app.database.db import SessionLocal
from backend.app.models.review import EnrichedReviewORM

class BM25Retriever:
    def __init__(self, corpus_limit: int = 10000):
        self.corpus_limit = corpus_limit
        self.documents: List[str] = []
        self.doc_ids: List[str] = []
        self.metadatas: List[Dict[str, Any]] = []
        self.tokenized_corpus: List[List[str]] = []
        self.bm25: Optional[BM25Okapi] = None
        self._load_corpus()

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Simple and effective regex tokenizer with lowercase normalization."""
        if not text:
            return []
        # Split on non-alphanumeric characters and lowercase
        tokens = re.findall(r'\b[a-z0-9]+\b', text.lower())
        # Remove ultra-common 1-letter stopwords
        return [t for t in tokens if len(t) > 1]

    def _load_corpus(self):
        """Load enriched reviews from SQLite into memory for BM25 indexing."""
        db = SessionLocal()
        # Query complaints first, followed by general reviews
        records = db.query(EnrichedReviewORM).order_by(
            EnrichedReviewORM.is_complaint.desc(),
            EnrichedReviewORM.priority_score.desc()
        ).limit(self.corpus_limit).all()

        for r in records:
            self.documents.append(r.text)
            self.doc_ids.append(r.review_id)
            self.metadatas.append({
                "restaurant": str(r.restaurant_name or "Unknown"),
                "city": str(r.city or "Unknown"),
                "state": str(r.state or "Unknown"),
                "rating": float(r.stars or 0.0),
                "category": str(r.complaint_category or "General"),
                "complaint_type": str(r.aspect or "general"),
                "priority_score": float(r.priority_score or 0.0),
                "severity_score": int(r.severity_score or 1),
                "business_id": str(r.business_id or ""),
                "review_id": str(r.review_id or ""),
                "date": str(r.date or "")
            })
            self.tokenized_corpus.append(self.tokenize(r.text))

        db.close()

        if self.tokenized_corpus:
            self.bm25 = BM25Okapi(self.tokenized_corpus)

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search the corpus using BM25Okapi scoring."""
        if not self.bm25 or not self.documents:
            return []

        tokenized_query = self.tokenize(query)
        if not tokenized_query:
            return []

        scores = self.bm25.get_scores(tokenized_query)
        
        # Rank document indices by BM25 score in descending order
        ranked_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )[:k]

        results = []
        for idx in ranked_indices:
            score = float(scores[idx])
            if score > 0.0: # Only return non-zero relevance
                results.append({
                    "id": self.doc_ids[idx],
                    "text": self.documents[idx],
                    "metadata": self.metadatas[idx],
                    "score": round(score, 4),
                    "retrieval_type": "bm25"
                })

        return results

# Global singleton
_bm25_instance: Optional[BM25Retriever] = None

def get_bm25_retriever(corpus_limit: int = 10000) -> BM25Retriever:
    global _bm25_instance
    if _bm25_instance is None:
        _bm25_instance = BM25Retriever(corpus_limit=corpus_limit)
    return _bm25_instance

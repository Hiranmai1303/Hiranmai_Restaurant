import pytest
from backend.app.retrieval.hybrid_search import HybridRetriever, get_hybrid_retriever

class MockVectorStore:
    def similarity_search(self, query: str, k: int = 5, filter_dict=None):
        return [
            {"id": "doc_A", "text": "Slow wait time for drinks", "metadata": {"category": "Waiting Time", "restaurant": "Cafe A"}, "score": 0.85},
            {"id": "doc_B", "text": "Cold pizza and bad cheese", "metadata": {"category": "Food Quality", "restaurant": "Pizzeria B"}, "score": 0.75}
        ]

class MockBM25Retriever:
    def search(self, query: str, k: int = 5):
        return [
            {"id": "doc_A", "text": "Slow wait time for drinks", "metadata": {"category": "Waiting Time", "restaurant": "Cafe A"}, "score": 8.5},
            {"id": "doc_C", "text": "Slow service by waiter", "metadata": {"category": "Service Quality", "restaurant": "Diner C"}, "score": 5.0}
        ]

def test_rrf_scoring_math_and_fusion():
    mock_vec = MockVectorStore()
    mock_bm25 = MockBM25Retriever()
    
    hybrid = HybridRetriever(
        vector_store=mock_vec,
        bm25_retriever=mock_bm25,
        rrf_k=60,
        vector_weight=0.5,
        bm25_weight=0.5
    )

    results = hybrid.search("slow drinks", k=3)
    assert len(results) == 3

    # doc_A appears at Rank 1 in Vector (0.5 / (60 + 1)) AND Rank 1 in BM25 (0.5 / (60 + 1))
    # Total expected RRF score for doc_A = (0.5/61) + (0.5/61) = 1.0 / 61 = 0.016393
    top_doc = results[0]
    assert top_doc["id"] == "doc_A"
    assert top_doc["vector_rank"] == 1
    assert top_doc["bm25_rank"] == 1
    assert top_doc["rrf_score"] == pytest.approx(round(1.0 / 61, 6), abs=1e-5)

    # doc_B and doc_C appear in only one system each, so their scores are lower than doc_A
    assert results[1]["rrf_score"] < top_doc["rrf_score"]
    assert results[2]["rrf_score"] < top_doc["rrf_score"]

def test_hybrid_search_production():
    hybrid = get_hybrid_retriever()
    results = hybrid.search("slow service and cold food", k=5)
    
    assert len(results) > 0
    assert "rrf_score" in results[0]
    assert "text" in results[0]
    assert "metadata" in results[0]
    assert "category" in results[0]["metadata"]
    
    # Ensure descending score order
    scores = [r["rrf_score"] for r in results]
    assert scores == sorted(scores, reverse=True)

def test_hybrid_search_empty_query():
    hybrid = get_hybrid_retriever()
    assert hybrid.search("", k=5) == []
    assert hybrid.search("   ", k=5) == []

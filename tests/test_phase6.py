import pytest
from backend.app.retrieval.bm25_search import BM25Retriever

def test_bm25_tokenizer():
    tokens = BM25Retriever.tokenize("Slow service, 45 minutes delay and rude waitress!")
    assert "slow" in tokens
    assert "service" in tokens
    assert "45" in tokens
    assert "minutes" in tokens
    assert "delay" in tokens
    assert "rude" in tokens
    assert "waitress" in tokens
    
    assert BM25Retriever.tokenize("") == []
    assert BM25Retriever.tokenize(None) == []

def test_bm25_search_slow_service():
    retriever = BM25Retriever(corpus_limit=2000)
    assert len(retriever.documents) > 0
    assert retriever.bm25 is not None

    query = "slow service"
    results = retriever.search(query, k=5)
    
    assert len(results) > 0
    assert results[0]["score"] > 0
    assert "text" in results[0]
    assert "metadata" in results[0]
    assert "restaurant" in results[0]["metadata"]
    
    # Verify that results are ordered in descending score
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)

    # Verify that returned documents match operational delay/waiting keywords
    found_relevance_keyword = False
    for r in results:
        text_lower = r["text"].lower()
        if any(kw in text_lower for kw in ["slow", "service", "wait", "delay", "ignored", "took forever"]):
            found_relevance_keyword = True
            break
    assert found_relevance_keyword is True

def test_bm25_search_edge_cases():
    retriever = BM25Retriever(corpus_limit=500)
    
    # Empty query
    assert retriever.search("", k=5) == []
    assert retriever.search("   ", k=5) == []
    
    # Non-matching gibberish query
    res = retriever.search("xyzzyqwertyfoobar123456789", k=5)
    assert len(res) == 0

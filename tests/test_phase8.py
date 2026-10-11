import pytest
from backend.app.retrieval.rag_service import RAGService, get_rag_service
from backend.app.core.llm_client import OpenRouterLLMClient

def test_rag_build_context():
    rag = RAGService()
    
    mock_docs = [
        {
            "id": "REV_101",
            "text": "Waited 50 minutes for appetizer, server ignored us.",
            "metadata": {
                "restaurant": "Trattoria Mario",
                "category": "Waiting Time",
                "complaint_type": "slow",
                "rating": 1.0,
                "priority_score": 88.0,
                "date": "2023-05-12 18:00:00"
            }
        },
        {
            "id": "REV_102",
            "text": "Soup was completely cold upon arrival.",
            "metadata": {
                "restaurant": "Pasta House",
                "category": "Food Quality",
                "complaint_type": "cold",
                "rating": 2.0,
                "priority_score": 75.0,
                "date": "2023-05-14 19:30:00"
            }
        }
    ]

    context = rag.build_context(mock_docs)
    
    assert "[Source #1 | ID: REV_101]" in context
    assert "Restaurant: Trattoria Mario" in context
    assert "Category: Waiting Time" in context
    assert "[Source #2 | ID: REV_102]" in context
    assert "Restaurant: Pasta House" in context
    assert "Soup was completely cold upon arrival." in context

def test_rag_answer_query_pipeline():
    rag = get_rag_service()
    
    query = "Why are customers complaining about slow service?"
    response = rag.answer_query(query=query, k=3, model="google/gemini-2.5-flash")
    
    assert response["query"] == query
    assert "answer" in response
    assert len(response["answer"]) > 50
    assert "retrieved_reviews" in response
    assert len(response["retrieved_reviews"]) > 0
    assert "citations" in response
    assert len(response["citations"]) == len(response["retrieved_reviews"])
    assert response["model_used"] == "google/gemini-2.5-flash"

def test_rag_pro_model_selection():
    rag = get_rag_service()
    response = rag.answer_query(
        query="What are cleanliness issues in dining area?",
        k=2,
        model="google/gemini-2.5-pro"
    )
    assert response["model_used"] == "google/gemini-2.5-pro"
    assert len(response["citations"]) > 0

def test_rag_empty_query():
    rag = get_rag_service()
    response = rag.answer_query(query="", k=2)
    assert response["evidence_count"] == 0
    assert response["citations"] == []

import pytest
from pathlib import Path
from chromadb.utils import embedding_functions
from backend.app.vectorstore.chroma_store import ChromaVectorStore, get_vector_store

def test_minilm_embeddings_dimension():
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    samples = ["The food was cold and service was slow.", "Clean restroom and friendly staff."]
    embeddings = embed_fn(samples)
    
    assert len(embeddings) == 2
    assert len(embeddings[0]) == 384 # 384 dimensions for all-MiniLM-L6-v2
    assert len(embeddings[1]) == 384

def test_chroma_vector_store_crud_and_search():
    # Use dedicated test collection in persistent chroma
    test_store = ChromaVectorStore(collection_name="test_verification_collection")
    
    texts = [
        "We waited for over forty minutes to get a glass of water.",
        "The steak was charred to a crisp and completely inedible.",
        "Restroom had a terrible odor and was not sanitized properly."
    ]
    metadatas = [
        {"restaurant": "Bistro A", "city": "Philadelphia", "rating": 1.0, "category": "Waiting Time", "complaint_type": "wait"},
        {"restaurant": "Steakhouse B", "city": "Tampa", "rating": 1.5, "category": "Food Quality", "complaint_type": "burnt"},
        {"restaurant": "Diner C", "city": "Nashville", "rating": 2.0, "category": "Cleanliness", "complaint_type": "odor"}
    ]
    ids = ["test_id_1", "test_id_2", "test_id_3"]
    
    test_store.add_documents(texts=texts, metadatas=metadatas, ids=ids)
    assert test_store.count() >= 3

    # Semantic query for slow waiting time
    results = test_store.similarity_search("delayed drinks and long wait", k=2)
    assert len(results) > 0
    top_match = results[0]
    assert top_match["metadata"]["category"] == "Waiting Time"
    assert top_match["metadata"]["restaurant"] == "Bistro A"
    assert top_match["metadata"]["complaint_type"] == "wait"
    assert "score" in top_match

    # Test metadata filtered query
    filtered_results = test_store.similarity_search("bad meal", k=2, filter_dict={"category": "Food Quality"})
    assert len(filtered_results) >= 1
    assert filtered_results[0]["metadata"]["category"] == "Food Quality"

def test_production_vector_store_queries():
    store = get_vector_store()
    assert store.count() > 0
    
    # Test realistic operational queries
    queries = [
        "cold food served late",
        "rude server and hostile manager",
        "cockroach in dining room"
    ]
    for q in queries:
        res = store.similarity_search(q, k=3)
        assert len(res) > 0
        assert "restaurant" in res[0]["metadata"]
        assert "category" in res[0]["metadata"]
        assert "complaint_type" in res[0]["metadata"]

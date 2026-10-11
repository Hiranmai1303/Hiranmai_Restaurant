"""
Hybrid Search Benchmark Script
Compares Pure BM25, Pure Vector Search, and Hybrid RRF Retrieval.
"""
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.retrieval.bm25_search import get_bm25_retriever
from backend.app.vectorstore.chroma_store import get_vector_store
from backend.app.retrieval.hybrid_search import get_hybrid_retriever

def main():
    print("1. Initializing Retrievers...")
    bm25 = get_bm25_retriever()
    vector = get_vector_store()
    hybrid = get_hybrid_retriever()

    test_queries = [
        "cold food and extremely slow kitchen delay",
        "arrogant manager yelled and rude staff",
        "dirty restroom sanitation cockroach bug",
        "overpriced bill unauthorized charge"
    ]

    for q in test_queries:
        print("\n" + "="*70)
        print(f"QUERY: '{q}'")
        print("="*70)

        bm25_res = bm25.search(q, k=2)
        print("\n--- PURE BM25 (Keyword) ---")
        for idx, r in enumerate(bm25_res, 1):
            print(f"[{idx}] Score: {r['score']} | {r['metadata']['category']} | {r['metadata']['restaurant']}")
            print(f"    Text: {r['text'][:110]}...")

        vec_res = vector.similarity_search(q, k=2)
        print("\n--- PURE VECTOR (Dense Semantic) ---")
        for idx, r in enumerate(vec_res, 1):
            print(f"[{idx}] Score: {r['score']} | {r['metadata']['category']} | {r['metadata']['restaurant']}")
            print(f"    Text: {r['text'][:110]}...")

        hyb_res = hybrid.search(q, k=3)
        print("\n--- HYBRID RRF (Reciprocal Rank Fusion) ---")
        for idx, r in enumerate(hyb_res, 1):
            print(f"[{idx}] RRF Score: {r['rrf_score']} (Vector Rank: {r.get('vector_rank')}, BM25 Rank: {r.get('bm25_rank')}) | {r['metadata']['category']} | {r['metadata']['restaurant']}")
            print(f"    Text: {r['text'][:110]}...")

if __name__ == "__main__":
    main()

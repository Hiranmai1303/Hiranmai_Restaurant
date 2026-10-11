"""
BM25 Search Benchmark Script
Executes sample queries (e.g., 'slow service', 'cold food', 'rude manager')
and displays retrieved documents and BM25 relevance scores.
"""
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.retrieval.bm25_search import BM25Retriever

def main():
    print("1. Initializing BM25 Retriever and indexing SQLite corpus...")
    retriever = BM25Retriever(corpus_limit=10000)
    print(f"   Indexed {len(retriever.documents)} documents in BM25 index.")

    test_queries = [
        "slow service",
        "delay long wait ignored",
        "raw meat food poisoning",
        "overpriced bill hidden fees"
    ]

    for q in test_queries:
        print(f"\n==================================================")
        print(f"Query: '{q}'")
        print(f"==================================================")
        results = retriever.search(q, k=3)
        for i, res in enumerate(results, 1):
            print(f"[{i}] BM25 Score: {res['score']} | Category: {res['metadata']['category']} | Restaurant: {res['metadata']['restaurant']}")
            print(f"    Text: {res['text'][:140]}...\n")

if __name__ == "__main__":
    main()

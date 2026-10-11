"""
RAG System Demonstration Script
Executes sample restaurant operations queries through the complete RAG pipeline
and prints grounded diagnosis, evidence citations, and recommendations.
"""
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.retrieval.rag_service import get_rag_service

def main():
    rag = get_rag_service()
    
    sample_queries = [
        "Why are customers complaining about slow service during weekend dinner hours?",
        "What are the main causes of food quality complaints in our Italian pasta dishes?",
        "How can we resolve staff attitude issues reported in recent reviews?"
    ]

    for q in sample_queries:
        print("\n" + "="*80)
        print(f"MANAGER QUESTION: {q}")
        print("="*80)

        response = rag.answer_query(query=q, k=3)
        
        print("\n--- GROUNDED OPERATIONAL DIAGNOSIS ---")
        print(response["answer"])
        
        print("\n--- RETRIEVED EVIDENCE CITATIONS ---")
        for cit in response["citations"]:
            print(f"  * [Source #{cit['source_index']}] {cit['restaurant']} | Rating: {cit['rating']} Stars | Category: {cit['category']} | Aspect: {cit['aspect']}")
        print()

if __name__ == "__main__":
    main()

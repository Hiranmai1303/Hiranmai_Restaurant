"""
Vector Store Indexing Script
Reads enriched reviews from SQLite and populates ChromaDB with 384-dimensional embeddings
using sentence-transformers/all-MiniLM-L6-v2 and comprehensive operational metadata.
"""
import sys
from pathlib import Path
from tqdm import tqdm

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.database.db import SessionLocal
from backend.app.models.review import EnrichedReviewORM
from backend.app.vectorstore.chroma_store import ChromaVectorStore

def build_vector_index(max_records: int = 500, batch_size: int = 128):
    print(f"1. Connecting to SQLite and querying up to {max_records} records...")
    db = SessionLocal()
    # Prioritize complaints first, followed by remaining reviews
    complaints = db.query(EnrichedReviewORM).filter(
        EnrichedReviewORM.is_complaint == True
    ).order_by(EnrichedReviewORM.priority_score.desc()).limit(max_records).all()
    
    if len(complaints) < max_records:
        remaining_needed = max_records - len(complaints)
        other_reviews = db.query(EnrichedReviewORM).filter(
            EnrichedReviewORM.is_complaint == False
        ).limit(remaining_needed).all()
        records = complaints + other_reviews
    else:
        records = complaints
        
    db.close()
    print(f"   Selected {len(records)} records for vector indexing.")

    print("2. Initializing ChromaDB and sentence-transformers/all-MiniLM-L6-v2...")
    store = ChromaVectorStore()

    texts = []
    metadatas = []
    ids = []

    for r in records:
        texts.append(r.text)
        ids.append(r.review_id)
        metadatas.append({
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

    print(f"3. Generating embeddings and indexing {len(texts)} documents in batches of {batch_size}...")
    for i in tqdm(range(0, len(texts), batch_size), desc="Vector Indexing"):
        batch_texts = texts[i:i+batch_size]
        batch_meta = metadatas[i:i+batch_size]
        batch_ids = ids[i:i+batch_size]
        store.add_documents(texts=batch_texts, metadatas=batch_meta, ids=batch_ids)

    total_count = store.count()
    print(f"4. Indexing complete! Total vectors in ChromaDB: {total_count}")

    # Test retrieval
    test_query = "slow service and waited long time for food"
    print(f"\n5. Testing retrieval for query: '{test_query}'")
    results = store.similarity_search(test_query, k=3)
    for idx, res in enumerate(results, 1):
        print(f"   [{idx}] Score: {res['score']} | Category: {res['metadata'].get('category')} | Restaurant: {res['metadata'].get('restaurant')}")
        print(f"       Text: {res['text'][:120]}...\n")

if __name__ == "__main__":
    build_vector_index()

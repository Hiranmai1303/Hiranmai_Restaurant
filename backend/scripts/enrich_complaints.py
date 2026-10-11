"""
Batch Complaint Enrichment and SQLite Database Ingestion Script
Enriches processed reviews and persists them into SQLite.
"""
import sys
from pathlib import Path
import pandas as pd
from tqdm import tqdm

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.database.db import init_db, SessionLocal, engine
from backend.app.models.review import EnrichedReviewORM
from backend.app.services.enrichment_service import ComplaintEnrichmentService

def run_enrichment(input_csv_path: Path, max_records: int = 50000):
    print("1. Initializing SQLite Database tables...")
    init_db()

    if not input_csv_path.exists():
        raise FileNotFoundError(f"Input file {input_csv_path.name} not found.")

    print(f"2. Loading processed reviews from {input_csv_path.name}...")
    df = pd.read_csv(input_csv_path, nrows=max_records)
    print(f"   Loaded {len(df)} records for enrichment.")

    service = ComplaintEnrichmentService()
    db = SessionLocal()

    print("3. Enriching reviews and inserting into SQLite...")
    batch_size = 2000
    current_batch = []
    
    # Clear existing records to ensure fresh state
    db.query(EnrichedReviewORM).delete()
    db.commit()

    for _, row in tqdm(df.iterrows(), total=len(df), desc="Enriching & Storing"):
        rec_dict = row.to_dict()
        enriched = service.enrich_record(rec_dict)
        
        orm_obj = EnrichedReviewORM(
            review_id=str(enriched["review_id"]),
            business_id=str(enriched["business_id"]),
            restaurant_name=str(enriched.get("restaurant_name", "Unknown")),
            city=str(enriched.get("city", "")),
            state=str(enriched.get("state", "")),
            categories=str(enriched.get("categories", "")),
            stars=float(enriched.get("stars", 3.0)),
            business_stars=float(enriched.get("business_stars", 3.5)) if pd.notna(enriched.get("business_stars")) else None,
            business_review_count=int(enriched.get("business_review_count", 0)) if pd.notna(enriched.get("business_review_count")) else None,
            date=str(enriched.get("date", "")),
            useful=int(enriched.get("useful", 0)) if pd.notna(enriched.get("useful")) else 0,
            text=str(enriched.get("text", "")),
            is_complaint=bool(enriched.get("is_complaint", False)),
            sentiment=str(enriched.get("sentiment", "Neutral")),
            complaint_category=str(enriched.get("complaint_category", "General Operational")),
            aspect=str(enriched.get("aspect", "general")),
            severity_score=int(enriched.get("severity_score", 1)),
            priority_score=float(enriched.get("priority_score", 1.0))
        )
        current_batch.append(orm_obj)

        if len(current_batch) >= batch_size:
            db.bulk_save_objects(current_batch)
            db.commit()
            current_batch = []

    if current_batch:
        db.bulk_save_objects(current_batch)
        db.commit()

    total_in_db = db.query(EnrichedReviewORM).count()
    complaints_count = db.query(EnrichedReviewORM).filter(EnrichedReviewORM.is_complaint == True).count()
    db.close()

    print(f"4. Successfully enriched and inserted {total_in_db} records into SQLite.")
    print(f"   Identified {complaints_count} actionable operational complaints.")

if __name__ == "__main__":
    csv_file = BASE_DIR / "data" / "processed" / "processed_reviews.csv"
    run_enrichment(csv_file)

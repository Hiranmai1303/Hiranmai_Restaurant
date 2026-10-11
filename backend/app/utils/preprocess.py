"""
Data Preprocessing Pipeline for Yelp Restaurant Reviews
Merges businesses with reviews, filters restaurant categories, cleans review text,
removes null values, and outputs processed data for downstream embeddings and enrichment.
"""
import html
import os
import re
from pathlib import Path
from typing import Dict, Generator, List, Optional
import pandas as pd
from backend.app.utils.dataset_loader import YelpDataLoader

class ReviewPreprocessor:
    def __init__(self, data_dir: Optional[Path] = None, output_dir: Optional[Path] = None):
        self.loader = YelpDataLoader(data_dir=data_dir)
        if output_dir is None:
            self.output_dir = Path(__file__).resolve().parent.parent.parent.parent / "data" / "processed"
        else:
            self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def clean_text(text: Optional[str]) -> str:
        """Clean and normalize review text."""
        if not text or pd.isna(text):
            return ""
        
        # Unescape HTML entities (e.g. &amp;, &quot;)
        text = html.unescape(str(text))
        
        # Remove URLs
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        
        # Remove HTML tags if any
        text = re.sub(r'<.*?>', '', text)
        
        # Normalize whitespace and excessive newlines
        text = re.sub(r'[\r\n\t]+', ' ', text)
        text = re.sub(r'\s{2,}', ' ', text)
        
        # Strip leading/trailing whitespace
        return text.strip()

    def process_and_merge(
        self,
        max_businesses: Optional[int] = None,
        max_reviews: Optional[int] = 50000,
        output_csv_name: str = "processed_reviews.csv"
    ) -> Path:
        """
        Merge restaurant businesses with reviews, clean review text,
        filter nulls, and save to CSV.
        """
        print("1. Loading restaurant businesses...")
        df_biz = self.loader.load_businesses(filter_restaurants_only=True, max_records=max_businesses)
        if df_biz.empty:
            raise ValueError("No restaurant businesses found in dataset.")

        # Create quick lookup map for businesses
        biz_map = df_biz.set_index("business_id").to_dict("index")
        print(f"   Found {len(biz_map)} restaurant businesses.")

        print(f"2. Streaming and cleaning reviews (limit: {max_reviews})...")
        processed_records = []
        
        for review in self.loader.stream_reviews(max_reviews=max_reviews):
            b_id = review.get("business_id")
            if b_id in biz_map:
                raw_text = review.get("text")
                cleaned_text = self.clean_text(raw_text)
                
                # Filter out empty or ultra-short reviews
                if not cleaned_text or len(cleaned_text) < 15:
                    continue
                
                biz_info = biz_map[b_id]
                
                processed_records.append({
                    "review_id": review.get("review_id"),
                    "business_id": b_id,
                    "restaurant_name": biz_info.get("name"),
                    "categories": biz_info.get("categories"),
                    "city": biz_info.get("city"),
                    "state": biz_info.get("state"),
                    "business_stars": biz_info.get("stars"),
                    "business_review_count": biz_info.get("review_count"),
                    "user_id": review.get("user_id"),
                    "stars": review.get("stars"),
                    "date": review.get("date"),
                    "useful": review.get("useful", 0),
                    "text": cleaned_text
                })

        df_processed = pd.DataFrame(processed_records)
        
        # Deduplicate reviews by review_id
        df_processed.drop_duplicates(subset=["review_id"], inplace=True)
        
        # Ensure date format is standardized ISO format
        df_processed["date"] = pd.to_datetime(df_processed["date"], errors="coerce")
        df_processed.dropna(subset=["date", "text", "stars"], inplace=True)
        df_processed["date"] = df_processed["date"].dt.strftime("%Y-%m-%d %H:%M:%S")

        output_path = self.output_dir / output_csv_name
        df_processed.to_csv(output_path, index=False, encoding="utf-8")
        print(f"3. Preprocessing complete! Saved {len(df_processed)} cleaned records to {output_path.name}")
        
        # Also create a sample subset for fast tests & demonstrations
        sample_path = self.output_dir.parent / "sample_data" / "processed_reviews_sample.csv"
        sample_path.parent.mkdir(parents=True, exist_ok=True)
        df_processed.head(500).to_csv(sample_path, index=False, encoding="utf-8")
        
        return output_path

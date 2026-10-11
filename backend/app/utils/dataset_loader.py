"""
Yelp Dataset Ingestion and Loading Utilities
Handles memory-efficient streaming, restaurant filtering, and linkage between businesses and reviews.
"""
import json
import os
from pathlib import Path
from typing import Dict, Generator, List, Optional, Tuple
import pandas as pd

class YelpDataLoader:
    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            self.data_dir = Path(__file__).resolve().parent.parent.parent.parent / "datasets"
        else:
            self.data_dir = Path(data_dir)
            
        self.business_file = self.data_dir / "yelp_academic_dataset_business.json"
        self.review_file = self.data_dir / "yelp_academic_dataset_review.json"

    def is_restaurant(self, categories: Optional[str]) -> bool:
        """Check if business categories contain restaurant or food related tags."""
        if not categories or pd.isna(categories):
            return False
        cats = [c.strip().lower() for c in str(categories).split(",")]
        restaurant_keywords = {
            "restaurants", "food", "bars", "cafes", "bakeries",
            "fast food", "coffee & tea", "diner", "pub", "eatery",
            "italian", "mexican", "chinese", "japanese", "american (traditional)",
            "american (new)", "pizza", "sandwiches", "burgers", "seafood"
        }
        return any(any(kw in cat for kw in restaurant_keywords) for cat in cats)

    def load_businesses(self, filter_restaurants_only: bool = True, max_records: Optional[int] = None) -> pd.DataFrame:
        """Load business JSON into a Pandas DataFrame."""
        if not self.business_file.exists():
            raise FileNotFoundError(f"Business dataset not found at {self.business_file}")

        records = []
        with open(self.business_file, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if max_records and i >= max_records:
                    break
                try:
                    data = json.loads(line)
                    if filter_restaurants_only:
                        if self.is_restaurant(data.get("categories")):
                            records.append({
                                "business_id": data.get("business_id"),
                                "name": data.get("name"),
                                "categories": data.get("categories"),
                                "city": data.get("city"),
                                "state": data.get("state"),
                                "stars": data.get("stars"),
                                "review_count": data.get("review_count"),
                                "is_open": data.get("is_open")
                            })
                    else:
                        records.append({
                            "business_id": data.get("business_id"),
                            "name": data.get("name"),
                            "categories": data.get("categories"),
                            "city": data.get("city"),
                            "state": data.get("state"),
                            "stars": data.get("stars"),
                            "review_count": data.get("review_count"),
                            "is_open": data.get("is_open")
                        })
                except json.JSONDecodeError:
                    continue

        return pd.DataFrame(records)

    def stream_reviews(self, max_reviews: Optional[int] = None) -> Generator[Dict, None, None]:
        """Stream review JSON lines one by one."""
        if not self.review_file.exists():
            raise FileNotFoundError(f"Review dataset not found at {self.review_file}")

        with open(self.review_file, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if max_reviews and i >= max_reviews:
                    break
                try:
                    review = json.loads(line)
                    yield {
                        "review_id": review.get("review_id"),
                        "user_id": review.get("user_id"),
                        "business_id": review.get("business_id"),
                        "stars": review.get("stars"),
                        "text": review.get("text"),
                        "date": review.get("date"),
                        "useful": review.get("useful", 0)
                    }
                except json.JSONDecodeError:
                    continue

    def get_dataset_eda_summary(self, max_business: Optional[int] = 50000, max_reviews: Optional[int] = 100000) -> Dict:
        """Perform comprehensive Exploratory Data Analysis (EDA) on Yelp Dataset."""
        total_businesses = 0
        restaurant_businesses = 0
        category_counts: Dict[str, int] = {}
        city_counts: Dict[str, int] = {}
        business_stars: List[float] = []
        valid_restaurant_ids = set()
        restaurant_metadata = {}

        # Business EDA
        with open(self.business_file, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if max_business and i >= max_business:
                    break
                total_businesses += 1
                try:
                    b = json.loads(line)
                    cats = b.get("categories") or ""
                    is_rest = self.is_restaurant(cats)
                    if is_rest:
                        restaurant_businesses += 1
                        b_id = b.get("business_id")
                        valid_restaurant_ids.add(b_id)
                        restaurant_metadata[b_id] = {
                            "name": b.get("name"),
                            "city": b.get("city"),
                            "state": b.get("state"),
                            "stars": b.get("stars")
                        }
                        if b.get("stars") is not None:
                            business_stars.append(float(b.get("stars")))
                        city = b.get("city", "Unknown")
                        city_counts[city] = city_counts.get(city, 0) + 1
                        for cat in cats.split(","):
                            cat_clean = cat.strip()
                            if cat_clean:
                                category_counts[cat_clean] = category_counts.get(cat_clean, 0) + 1
                except Exception:
                    continue

        # Review EDA & Linking
        total_reviews_scanned = 0
        linked_reviews_count = 0
        review_stars_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

        for review in self.stream_reviews(max_reviews=max_reviews):
            total_reviews_scanned += 1
            b_id = review.get("business_id")
            if b_id in valid_restaurant_ids:
                linked_reviews_count += 1
                stars = int(review.get("stars", 0))
                if stars in review_stars_dist:
                    review_stars_dist[stars] += 1

        top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        top_cities = sorted(city_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            "total_businesses_sampled": total_businesses,
            "restaurant_businesses_count": restaurant_businesses,
            "total_reviews_scanned": total_reviews_scanned,
            "linked_reviews_count": linked_reviews_count,
            "avg_restaurant_star_rating": round(sum(business_stars) / max(len(business_stars), 1), 2),
            "top_categories": top_categories,
            "top_cities": top_cities,
            "review_stars_distribution": review_stars_dist
        }

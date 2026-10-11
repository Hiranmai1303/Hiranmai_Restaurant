"""
Standalone execution script for Data Preprocessing Pipeline
Merges Yelp businesses + reviews, removes nulls, cleans text, and generates data/processed/processed_reviews.csv
"""
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.utils.preprocess import ReviewPreprocessor

def main():
    preprocessor = ReviewPreprocessor()
    print("Starting Yelp Restaurant Preprocessing Pipeline...")
    output_path = preprocessor.process_and_merge(
        max_businesses=50000,
        max_reviews=60000,
        output_csv_name="processed_reviews.csv"
    )
    print(f"Pipeline executed successfully. Output created at: {output_path.name}")

if __name__ == "__main__":
    main()

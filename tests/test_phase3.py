import os
from pathlib import Path
import pytest
import pandas as pd
from backend.app.utils.preprocess import ReviewPreprocessor

def test_clean_text_utility():
    preprocessor = ReviewPreprocessor()
    
    raw = "   Great food &amp; drinks! <br/> Visit http://example.com for more.\n\nVery fast service.  "
    cleaned = preprocessor.clean_text(raw)
    
    assert "Great food & drinks!" in cleaned
    assert "http://example.com" not in cleaned
    assert "<br/>" not in cleaned
    assert "\n" not in cleaned
    assert cleaned == "Great food & drinks! Visit for more. Very fast service."

def test_clean_text_edge_cases():
    preprocessor = ReviewPreprocessor()
    assert preprocessor.clean_text(None) == ""
    assert preprocessor.clean_text("") == ""
    assert preprocessor.clean_text("   ") == ""

def test_preprocessing_and_merge_pipeline():
    preprocessor = ReviewPreprocessor()
    
    output_path = preprocessor.process_and_merge(
        max_businesses=1000,
        max_reviews=2000,
        output_csv_name="test_processed_reviews.csv"
    )
    
    assert output_path.exists()
    df = pd.read_csv(output_path)
    assert not df.empty
    
    # Verify required schema
    expected_cols = [
        "review_id", "business_id", "restaurant_name", "categories",
        "city", "state", "business_stars", "business_review_count",
        "user_id", "stars", "date", "useful", "text"
    ]
    for col in expected_cols:
        assert col in df.columns, f"Missing column {col} in processed data"
        
    # Verify no nulls in critical fields
    assert df["text"].isna().sum() == 0
    assert df["stars"].isna().sum() == 0
    assert df["business_id"].isna().sum() == 0
    assert df["restaurant_name"].isna().sum() == 0

    # Cleanup test output file
    if output_path.exists():
        output_path.unlink()

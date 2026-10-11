import os
from pathlib import Path
import pytest
from backend.app.utils.dataset_loader import YelpDataLoader
from backend.scripts.dataset_eda import run_eda, generate_dataset_details_pdf

def test_yelp_data_files_exist():
    loader = YelpDataLoader()
    assert loader.business_file.exists(), f"Missing {loader.business_file}"
    assert loader.review_file.exists(), f"Missing {loader.review_file}"

def test_is_restaurant_classifier():
    loader = YelpDataLoader()
    assert loader.is_restaurant("Restaurants, Fast Food, Burgers") is True
    assert loader.is_restaurant("Doctors, Health & Medical") is False
    assert loader.is_restaurant("Bars, Nightlife, Pub Food") is True
    assert loader.is_restaurant(None) is False
    assert loader.is_restaurant("") is False

def test_business_and_review_loading_and_linking():
    loader = YelpDataLoader()
    # Load 500 businesses
    df_biz = loader.load_businesses(filter_restaurants_only=True, max_records=500)
    assert not df_biz.empty
    assert "business_id" in df_biz.columns
    assert "name" in df_biz.columns
    assert "stars" in df_biz.columns
    
    # Check that streamed reviews contain business_id and valid fields
    reviews_sample = list(loader.stream_reviews(max_reviews=50))
    assert len(reviews_sample) == 50
    first_review = reviews_sample[0]
    assert "business_id" in first_review
    assert "text" in first_review
    assert "stars" in first_review

def test_eda_summary_and_pdf_generation():
    loader = YelpDataLoader()
    eda_summary = loader.get_dataset_eda_summary(max_business=5000, max_reviews=10000)
    
    assert eda_summary["total_businesses_sampled"] > 0
    assert eda_summary["restaurant_businesses_count"] > 0
    assert eda_summary["linked_reviews_count"] > 0
    assert eda_summary["avg_restaurant_star_rating"] > 0
    assert len(eda_summary["top_categories"]) > 0
    
    # Test PDF generation
    pdf_path = Path(__file__).resolve().parent.parent / "docs" / "Dataset_Details.pdf"
    res = generate_dataset_details_pdf(eda_summary, pdf_path)
    assert res is True
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 1000 # Valid non-empty PDF

"""
Phase 12 Unit Tests: Time Series Forecasting with Prophet
Validates time series extraction, 90-day and 180-day forecast models,
category-specific projections, and fallback handlers.
"""
import pytest
import pandas as pd
from backend.app.forecasting.prophet_forecast import ComplaintForecaster, get_forecaster

def test_load_time_series_structure():
    forecaster = get_forecaster()
    df_ts = forecaster.load_time_series(metric="complaint_count", freq="W")
    
    assert isinstance(df_ts, pd.DataFrame)
    assert not df_ts.empty
    assert "ds" in df_ts.columns
    assert "y" in df_ts.columns
    assert df_ts["y"].dtype in [int, float, "int64", "float64"]
    assert len(df_ts) > 10

def test_prophet_90_day_forecast():
    forecaster = get_forecaster()
    res = forecaster.forecast(
        metric="complaint_count",
        horizon_days=90,
        freq="W"
    )
    
    assert res["status"] == "success"
    assert res["horizon_days"] == 90
    assert res["forecast_datapoints"] >= 12  # ~13 weeks in 90 days
    assert "trend_direction" in res
    assert "projected_peak" in res
    assert len(res["forecast"]) == res["forecast_datapoints"]
    assert all("lower_bound" in p and "upper_bound" in p for p in res["forecast"])

def test_prophet_180_day_forecast():
    forecaster = get_forecaster()
    res = forecaster.forecast(
        metric="complaint_count",
        horizon_days=180,
        freq="W"
    )
    
    assert res["status"] == "success"
    assert res["horizon_days"] == 180
    assert res["forecast_datapoints"] >= 24  # ~26 weeks in 180 days
    assert res["projected_avg_level"] >= 0.0

def test_category_trend_forecast():
    forecaster = get_forecaster()
    cat_trends = forecaster.forecast_all_categories(horizon_days=90)
    
    assert len(cat_trends) == 8
    categories_found = [c["category"] for c in cat_trends]
    assert "Waiting Time" in categories_found
    assert "Food Quality" in categories_found
    assert all("current_avg" in c and "projected_avg" in c for c in cat_trends)

def test_sparse_data_fallback_forecast():
    forecaster = get_forecaster()
    # Query with a non-existent business_id to trigger fallback
    res = forecaster.forecast(
        business_id="non_existent_fake_business_id_999",
        horizon_days=90,
        freq="W"
    )
    
    assert res["status"] == "success"
    assert res["forecast_datapoints"] >= 12
    assert res["trend_direction"] == "Stable"
    assert len(res["forecast"]) >= 12

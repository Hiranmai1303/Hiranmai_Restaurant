"""
Phase 12 Demo: Facebook Prophet Time Series Forecasting
Generates 90-day (3-Month) and 180-day (6-Month) complaint volume and risk projections.
"""
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.forecasting.prophet_forecast import get_forecaster

def main():
    print("==================================================================")
    print("   AI RESTAURANT OPERATIONS: PROPHET TIME SERIES FORECASTING     ")
    print("==================================================================")

    forecaster = get_forecaster()

    # 1. Overall 90-day forecast
    print("\n>>> 1. Overall System Complaint Volume (90-Day Horizon):")
    res_90 = forecaster.forecast(metric="complaint_count", horizon_days=90, freq="W")
    print(f"Model Type           : {res_90['model']}")
    print(f"Historical Datapoints: {res_90['historical_datapoints']} weekly periods")
    print(f"Forecast Datapoints  : {res_90['forecast_datapoints']} weekly periods")
    print(f"Current Avg Volume   : {res_90['current_avg_level']} complaints/week")
    print(f"Projected Avg Volume : {res_90['projected_avg_level']} complaints/week")
    print(f"Projected Change     : {res_90['pct_change']}% ({res_90['trend_direction']})")
    print(f"Projected Peak       : {res_90['projected_peak']['value']} complaints on {res_90['projected_peak']['date']}")

    # 2. Overall 180-day forecast
    print("\n>>> 2. Overall System Complaint Volume (180-Day / 6-Month Horizon):")
    res_180 = forecaster.forecast(metric="complaint_count", horizon_days=180, freq="W")
    print(f"Projected Avg Volume : {res_180['projected_avg_level']} complaints/week")
    print(f"Projected Change     : {res_180['pct_change']}% ({res_180['trend_direction']})")

    # 3. Category-level Risk Trajectory Rankings
    print("\n>>> 3. Operational Category Risk Rankings (Next 90 Days):")
    cat_trends = forecaster.forecast_all_categories(horizon_days=90)
    print(f"{'Category':<20} | {'Current':<8} | {'Projected':<10} | {'Change %':<10} | {'Trend Status'}")
    print("-" * 72)
    for cat in cat_trends:
        print(f"{cat['category']:<20} | {cat['current_avg']:<8.1f} | {cat['projected_avg']:<10.1f} | {cat['pct_change']:<+9.1f}% | {cat['trend_direction']}")

    print("\n==================================================================")
    print("   PHASE 12 FORECASTING BENCHMARK COMPLETE                        ")
    print("==================================================================")

if __name__ == "__main__":
    main()

"""
Time Series Forecasting Service using Facebook Prophet.
Forecasts complaint volume, category trends, and severity trajectories
over 3-month (90 days) and 6-month (180 days) horizons.
"""
import os
import sqlite3
import logging
from typing import Any, Dict, List, Optional
import pandas as pd
import numpy as np

# Suppress cmdstanpy and prophet verbose logging
logging.getLogger("cmdstanpy").setLevel(logging.WARNING)
logging.getLogger("prophet").setLevel(logging.WARNING)

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False

from backend.app.core.config import settings

class ComplaintForecaster:
    """
    Production-grade Time Series Forecaster for Restaurant Operations.
    """
    CATEGORIES = [
        "Waiting Time",
        "Food Quality",
        "Service Quality",
        "Staff Behavior",
        "Cleanliness",
        "Pricing",
        "Order Accuracy",
        "Ambience"
    ]

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(settings.PROCESSED_DATA_DIR / "restaurant_operations.db")

    def _get_connection(self) -> sqlite3.Connection:
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database not found at {self.db_path}")
        return sqlite3.connect(self.db_path)

    def load_time_series(
        self,
        business_id: Optional[str] = None,
        category: Optional[str] = None,
        metric: str = "complaint_count",
        freq: str = "W"
    ) -> pd.DataFrame:
        """
        Extract and aggregate historical review time series from SQLite.
        Returns DataFrame with ['ds', 'y'].
        """
        conn = self._get_connection()
        query = "SELECT date, is_complaint, complaint_category, severity_score FROM enriched_reviews WHERE date IS NOT NULL"
        params = []

        if business_id:
            query += " AND business_id = ?"
            params.append(business_id)

        if category and category != "All":
            query += " AND complaint_category = ?"
            params.append(category)

        df = pd.read_sql_query(query, conn, params=params)
        conn.close()

        if df.empty:
            return pd.DataFrame(columns=["ds", "y"])

        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"]).sort_values("date")

        if df.empty:
            return pd.DataFrame(columns=["ds", "y"])

        # Filter for complaints if metric is complaint_count
        if metric == "complaint_count":
            df_metric = df[df["is_complaint"] == 1].copy()
            if df_metric.empty:
                df_metric = df.copy()
            # Resample by date frequency
            df_metric.set_index("date", inplace=True)
            resampled = df_metric.resample(freq).size().reset_index(name="y")
            resampled.rename(columns={"date": "ds"}, inplace=True)
        elif metric == "avg_severity":
            df.set_index("date", inplace=True)
            resampled = df["severity_score"].resample(freq).mean().reset_index(name="y")
            resampled.rename(columns={"date": "ds"}, inplace=True)
            resampled["y"] = resampled["y"].ffill().fillna(2.5)
        else:
            df.set_index("date", inplace=True)
            resampled = df.resample(freq).size().reset_index(name="y")
            resampled.rename(columns={"date": "ds"}, inplace=True)

        # Fill missing dates with 0 for counts
        if metric != "avg_severity":
            resampled["y"] = resampled["y"].fillna(0)

        return resampled

    def forecast(
        self,
        business_id: Optional[str] = None,
        category: Optional[str] = None,
        metric: str = "complaint_count",
        horizon_days: int = 90,
        freq: str = "W"
    ) -> Dict[str, Any]:
        """
        Fit Prophet model and project future trend over horizon_days.
        """
        df_ts = self.load_time_series(business_id=business_id, category=category, metric=metric, freq=freq)

        if len(df_ts) < 5 or not PROPHET_AVAILABLE:
            # Fallback linear / moving average projection for small datasets or no prophet
            return self._fallback_forecast(df_ts, horizon_days=horizon_days, freq=freq, metric=metric, category=category)

        # Periods to forecast based on frequency
        periods = max(4, int(horizon_days / 7)) if freq == "W" else max(3, int(horizon_days / 30))

        model = Prophet(
            yearly_seasonality="auto",
            weekly_seasonality=False if freq in ["W", "M"] else "auto",
            daily_seasonality=False,
            interval_width=0.95
        )

        model.fit(df_ts)
        future = model.make_future_dataframe(periods=periods, freq=freq)
        forecast_df = model.predict(future)

        # Separate historical vs forecast portions
        historical_len = len(df_ts)
        history_part = forecast_df.iloc[:historical_len]
        future_part = forecast_df.iloc[historical_len:]

        # Summary statistics
        recent_avg = float(df_ts["y"].iloc[-min(4, len(df_ts)):].mean())
        projected_avg = float(future_part["yhat"].clip(lower=0).mean())
        
        if recent_avg > 0:
            pct_change = round(((projected_avg - recent_avg) / recent_avg) * 100.0, 1)
        else:
            pct_change = 0.0

        if pct_change > 5.0:
            trend_direction = "Increasing (Elevated Risk)"
        elif pct_change < -5.0:
            trend_direction = "Decreasing (Improving)"
        else:
            trend_direction = "Stable"

        peak_idx = future_part["yhat"].idxmax()
        peak_row = future_part.loc[peak_idx]

        # Structure historical and forecast datapoints for charts
        historical_points = [
            {"date": row["ds"].strftime("%Y-%m-%d"), "actual": round(float(df_ts.iloc[i]["y"]), 2), "trend": round(float(row["trend"]), 2)}
            for i, (_, row) in enumerate(history_part.iterrows())
        ]

        forecast_points = [
            {
                "date": row["ds"].strftime("%Y-%m-%d"),
                "forecast": max(0.0, round(float(row["yhat"]), 2)),
                "lower_bound": max(0.0, round(float(row["yhat_lower"]), 2)),
                "upper_bound": max(0.0, round(float(row["yhat_upper"]), 2))
            }
            for _, row in future_part.iterrows()
        ]

        return {
            "status": "success",
            "model": "Prophet",
            "category": category or "All Categories",
            "metric": metric,
            "horizon_days": horizon_days,
            "frequency": freq,
            "historical_datapoints": len(historical_points),
            "forecast_datapoints": len(forecast_points),
            "current_avg_level": round(recent_avg, 2),
            "projected_avg_level": round(projected_avg, 2),
            "pct_change": pct_change,
            "trend_direction": trend_direction,
            "projected_peak": {
                "date": peak_row["ds"].strftime("%Y-%m-%d"),
                "value": max(0.0, round(float(peak_row["yhat"]), 2))
            },
            "history": historical_points,
            "forecast": forecast_points
        }

    def _fallback_forecast(
        self,
        df_ts: pd.DataFrame,
        horizon_days: int,
        freq: str,
        metric: str,
        category: Optional[str]
    ) -> Dict[str, Any]:
        """Simple statistical fallback when time series is sparse."""
        periods = max(4, int(horizon_days / 7))
        base_val = float(df_ts["y"].mean()) if not df_ts.empty else 5.0
        last_date = df_ts["ds"].max() if not df_ts.empty else pd.Timestamp.now()
        
        future_dates = pd.date_range(start=last_date + pd.Timedelta(days=7), periods=periods, freq=freq)
        forecast_points = [
            {
                "date": d.strftime("%Y-%m-%d"),
                "forecast": round(base_val, 2),
                "lower_bound": round(max(0.0, base_val * 0.8), 2),
                "upper_bound": round(base_val * 1.2, 2)
            }
            for d in future_dates
        ]
        
        return {
            "status": "success",
            "model": "Baseline-Moving-Average",
            "category": category or "All Categories",
            "metric": metric,
            "horizon_days": horizon_days,
            "frequency": freq,
            "historical_datapoints": len(df_ts),
            "forecast_datapoints": len(forecast_points),
            "current_avg_level": round(base_val, 2),
            "projected_avg_level": round(base_val, 2),
            "pct_change": 0.0,
            "trend_direction": "Stable",
            "projected_peak": {
                "date": future_dates[0].strftime("%Y-%m-%d") if len(future_dates) > 0 else "N/A",
                "value": round(base_val, 2)
            },
            "history": [{"date": str(row["ds"]), "actual": float(row["y"]), "trend": float(row["y"])} for _, row in df_ts.iterrows()],
            "forecast": forecast_points
        }

    def forecast_all_categories(
        self,
        business_id: Optional[str] = None,
        horizon_days: int = 90
    ) -> List[Dict[str, Any]]:
        """
        Forecast trends across all 8 operational categories to identify high-risk emerging issues.
        """
        category_forecasts = []
        for cat in self.CATEGORIES:
            res = self.forecast(
                business_id=business_id,
                category=cat,
                metric="complaint_count",
                horizon_days=horizon_days,
                freq="W"
            )
            category_forecasts.append({
                "category": cat,
                "current_avg": res["current_avg_level"],
                "projected_avg": res["projected_avg_level"],
                "pct_change": res["pct_change"],
                "trend_direction": res["trend_direction"],
                "projected_peak_date": res["projected_peak"]["date"],
                "projected_peak_value": res["projected_peak"]["value"]
            })

        # Sort by highest projected growth rate
        return sorted(category_forecasts, key=lambda x: x["pct_change"], reverse=True)

# Global singleton
_forecaster_instance: Optional[ComplaintForecaster] = None

def get_forecaster() -> ComplaintForecaster:
    global _forecaster_instance
    if _forecaster_instance is None:
        _forecaster_instance = ComplaintForecaster()
    return _forecaster_instance

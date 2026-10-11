"""
Script: Run Complete Benchmark Evaluation
Executes:
1. Empirical Retrieval Metrics (Recall@5, Precision@5, MRR) for BM25, Vector, Hybrid RRF across 40 benchmark test cases.
2. Real DeepEval Metrics (Faithfulness, Answer Relevancy, Contextual Precision, Contextual Recall, GEval Recommendation Quality).
3. Prophet Time Series Forecast Accuracy (MAE, RMSE, MAPE) via held-out backtesting.
4. Outputs data/eval_results/eval_results_<timestamp>.json and data/eval_results/latest.json.
"""
import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from backend.app.evaluation.evaluator import get_rag_evaluator
from backend.app.forecasting.prophet_forecast import get_forecaster

def main():
    print("=" * 80)
    print("AI RESTAURANT OPERATIONS ASSISTANT: PRODUCTION EVALUATION RUNNER")
    print("=" * 80)
    print(f"Timestamp: {datetime.utcnow().isoformat()}Z")
    
    eval_dir = os.path.join(str(PROJECT_ROOT), "data", "eval_results")
    os.makedirs(eval_dir, exist_ok=True)
    
    evaluator = get_rag_evaluator()
    forecaster = get_forecaster()
    
    # 1. Run RAG and Retrieval Benchmark Evaluation
    print("\n[Step 1/3] Running RAG retrieval benchmarks and DeepEval evaluations (40 test cases)...")
    eval_results = evaluator.run_benchmark_evaluation(output_dir=eval_dir)
    
    # 2. Run Prophet Backtesting Accuracy
    print("\n[Step 2/3] Running Prophet time series held-out backtest evaluation...")
    prophet_metrics = forecaster.evaluate_backtest_accuracy(holdout_periods=12, metric="complaint_count", freq="W")
    eval_results["prophet_forecast_accuracy"] = prophet_metrics
    
    # 3. Update saved files with Prophet results
    latest_path = os.path.join(eval_dir, "latest.json")
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(eval_results, f, indent=2)
        
    print("\n[Step 3/3] Results saved successfully:")
    print("  -> Latest: data/eval_results/latest.json")
    
    # Print Executive Summary Tables
    print("\n" + "=" * 80)
    print("RETRIEVAL BENCHMARK RESULTS (Empirically Measured Across Ground-Truth Reviews)")
    print("=" * 80)
    print(f"{'Retrieval Engine':<20} | {'Recall@5':<12} | {'Precision@5':<14} | {'MRR':<10}")
    print("-" * 65)
    for engine, metrics in eval_results.get("retrieval_benchmarks", {}).items():
        print(f"{engine.upper():<20} | {metrics['recall_at_5']:<12.4f} | {metrics['precision_at_5']:<14.4f} | {metrics['mrr']:<10.4f}")
        
    print("\n" + "=" * 80)
    print("DEEPEVAL QUALITY SCORES (Grounded LLM Metrics vs Target Thresholds)")
    print("=" * 80)
    print(f"{'Metric':<26} | {'Target':<10} | {'Actual':<12} | {'Verdict'}")
    print("-" * 65)
    for m_name, v_data in eval_results.get("verdict_by_target", {}).items():
        actual_str = f"{v_data.get('actual'):.4f}" if v_data.get('actual') is not None else "N/A"
        target_str = f"{v_data.get('target'):.2f}"
        verdict_str = "PASS" if v_data.get("passed") is True else ("FAIL" if v_data.get("passed") is False else "NOT EVALUATED")
        print(f"{m_name:<26} | {target_str:<10} | {actual_str:<12} | {verdict_str}")
        
    print("\n" + "=" * 80)
    print("PROPHET FORECAST ACCURACY (12-Period Held-Out Backtest)")
    print("=" * 80)
    if prophet_metrics.get("status") == "evaluated":
        print(f"MAE  : {prophet_metrics.get('mae')} complaints/period")
        print(f"RMSE : {prophet_metrics.get('rmse')} complaints/period")
        print(f"MAPE : {prophet_metrics.get('mape')}%")
    else:
        print(f"Status: {prophet_metrics.get('status')}")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()

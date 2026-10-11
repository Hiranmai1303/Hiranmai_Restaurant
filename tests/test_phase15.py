"""
Phase 15 Unit Tests: System Evaluation (DeepEval & RAGAS)
Validates benchmark test cases, scoring calculations, metric bounds,
evaluator runner, and PDF report generation.
"""
import os
import pytest
from backend.app.evaluation.benchmark_dataset import BENCHMARK_TEST_CASES
from backend.app.evaluation.evaluator import RAGEvaluator, get_evaluator
from backend.app.evaluation.generate_eval_report import generate_evaluation_pdf

def test_benchmark_dataset_integrity():
    assert len(BENCHMARK_TEST_CASES) == 8
    categories = [tc["category"] for tc in BENCHMARK_TEST_CASES]
    assert "Waiting Time" in categories
    assert "Food Quality" in categories
    assert "Cleanliness" in categories
    assert all("query" in tc and "ground_truth" in tc for tc in BENCHMARK_TEST_CASES)

def test_evaluator_individual_metrics():
    evaluator = get_evaluator()
    
    # Test faithfulness
    context = "The entrees were served lukewarm because they sat under the heating lamp for 20 minutes."
    answer = "The food arrived cold due to holding temperature issues under the heat lamp."
    f_score = evaluator.compute_faithfulness(answer, context)
    assert 0.0 <= f_score <= 1.0
    assert f_score >= 0.70

    # Test answer relevancy
    query = "Why did the food arrive cold?"
    r_score = evaluator.compute_answer_relevancy(query, answer)
    assert 0.0 <= r_score <= 1.0
    assert r_score >= 0.75

    # Test context recall
    expected_causes = ["holding_temperature_lapse", "expo_station_delays"]
    c_recall = evaluator.compute_context_recall(expected_causes, context)
    assert 0.0 <= c_recall <= 1.0

def test_evaluator_single_test_case():
    evaluator = get_evaluator()
    sample_case = BENCHMARK_TEST_CASES[0]
    
    result = evaluator.evaluate_test_case(sample_case)
    assert result["category"] == "Waiting Time"
    assert "metrics" in result
    assert result["metrics"]["faithfulness"] >= 0.70
    assert result["metrics"]["overall_rag_score"] >= 0.75
    assert result["citations_count"] >= 1

def test_evaluation_pdf_report_exists_and_valid():
    pdf_path = "docs/Evaluation_Report.pdf"
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 3000  # Non-trivial PDF size (>3KB)

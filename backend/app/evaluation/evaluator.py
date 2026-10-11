"""
RAG System Evaluator (Real DeepEval & RAGAS Metrics Engine)
Computes production DeepEval quality metrics (Faithfulness, Answer Relevancy,
Contextual Precision, Contextual Recall, and GEval Recommendation Quality)
using an OpenRouterGemini custom judge wrapper.
Also computes measured retrieval metrics (Recall@5, Precision@5, MRR) across BM25,
Vector, and Hybrid retrieval engines.
"""
import os
import re
import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
import numpy as np


from deepeval.models.base_model import DeepEvalBaseLLM
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import (
    FaithfulnessMetric,
    AnswerRelevancyMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    GEval
)

from backend.app.core.config import settings
from backend.app.core.llm_client import get_llm_client
from backend.app.evaluation.benchmark_dataset import BENCHMARK_TEST_CASES
from backend.app.retrieval.rag_service import get_rag_service
from backend.app.retrieval.bm25_search import get_bm25_retriever
from backend.app.vectorstore.chroma_store import get_vector_store
from backend.app.retrieval.hybrid_search import get_hybrid_retriever


class OpenRouterGemini(DeepEvalBaseLLM):
    """
    Custom DeepEval Base LLM model wrapper routing judge requests directly
    through OpenRouterLLMClient in backend/app/core/llm_client.py.
    """
    def __init__(self, model_name: Optional[str] = None):
        self.llm_client = get_llm_client()
        self.model_name = model_name or self.llm_client.default_model
        super().__init__(model=self.model_name)

    def load_model(self) -> Any:
        return self.llm_client

    def get_model_name(self) -> str:
        return self.model_name

    def generate(self, prompt: str, schema: Optional[Any] = None) -> str:
        """Executes a synchronous LLM call via OpenRouterLLMClient."""
        return self.llm_client.call_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model=self.model_name,
            temperature=0.0,
            max_tokens=1200
        )

    async def a_generate(self, prompt: str, schema: Optional[Any] = None) -> str:
        """Asynchronous execution delegating to synchronous completion."""
        return self.generate(prompt, schema=schema)


class RAGEvaluator:
    """
    Comprehensive evaluation engine for RAG retrieval and generation quality.
    Replaces fabricated heuristic floors with real DeepEval metrics and measured retrieval benchmarks.
    """

    TARGET_METRICS = {
        "faithfulness": 0.85,
        "answer_relevancy": 0.85,
        "context_precision": 0.80,
        "context_recall": 0.80,
        "recommendation_quality": 0.80
    }

    def __init__(self, judge_model_name: Optional[str] = None):
        self.judge_model_name = judge_model_name or settings.DEFAULT_LLM_MODEL
        self._judge_llm: Optional[OpenRouterGemini] = None

    def get_judge_llm(self) -> OpenRouterGemini:
        if self._judge_llm is None:
            self._judge_llm = OpenRouterGemini(model_name=self.judge_model_name)
        return self._judge_llm

    # -------------------------------------------------------------------------
    # 1. Computed Retrieval Metrics (Precision@5, Recall@5, MRR)
    # -------------------------------------------------------------------------
    def compute_retrieval_benchmarks(
        self,
        benchmark_cases: Optional[List[Dict[str, Any]]] = None,
        k: int = 5
    ) -> Dict[str, Any]:
        """
        Computes empirical Precision@5, Recall@5, and MRR across BM25, Vector, and Hybrid engines.
        All scores are strictly computed against ground-truth relevant review IDs.
        """
        cases = benchmark_cases or BENCHMARK_TEST_CASES
        # Filter to operational cases with ground truth review IDs
        valid_cases = [c for c in cases if not c.get("is_out_of_scope", False) and c.get("relevant_review_ids")]

        bm25_retriever = get_bm25_retriever()
        vector_store = get_vector_store()
        hybrid_retriever = get_hybrid_retriever()

        engines = {
            "bm25": {"precisions": [], "recalls": [], "mrrs": []},
            "vector": {"precisions": [], "recalls": [], "mrrs": []},
            "hybrid": {"precisions": [], "recalls": [], "mrrs": []}
        }

        for case in valid_cases:
            query = case["query"]
            gt_ids = set(case["relevant_review_ids"])
            if not gt_ids:
                continue

            # Query each retriever
            bm25_res = bm25_retriever.search(query, k=k)
            vec_res = vector_store.search(query, k=k)
            hyb_res = hybrid_retriever.search(query, k=k)

            b_ids = [r.get("id") or r.get("metadata", {}).get("review_id", "") for r in bm25_res]
            v_ids = [r.get("id") for r in vec_res]
            h_ids = [r.get("id") for r in hyb_res]

            engine_runs = [("bm25", b_ids), ("vector", v_ids), ("hybrid", h_ids)]

            for name, retrieved_ids in engine_runs:
                hits = [d_id for d_id in retrieved_ids if d_id in gt_ids]
                precision = len(hits) / float(k)
                recall = len(hits) / float(len(gt_ids)) if gt_ids else 0.0

                mrr = 0.0
                for rank, d_id in enumerate(retrieved_ids, start=1):
                    if d_id in gt_ids:
                        mrr = 1.0 / rank
                        break

                engines[name]["precisions"].append(precision)
                engines[name]["recalls"].append(recall)
                engines[name]["mrrs"].append(mrr)

        results = {}
        for name, data in engines.items():
            p_mean = round(float(np.mean(data["precisions"])) if data["precisions"] else 0.0, 4)
            r_mean = round(float(np.mean(data["recalls"])) if data["recalls"] else 0.0, 4)
            m_mean = round(float(np.mean(data["mrrs"])) if data["mrrs"] else 0.0, 4)
            results[name] = {
                "precision_at_5": p_mean,
                "recall_at_5": r_mean,
                "mrr": m_mean,
                "evaluated_queries": len(data["precisions"])
            }

        return results

    # -------------------------------------------------------------------------
    # 2. DeepEval Real LLM Evaluation (Faithfulness, Relevancy, Precision, Recall, GEval)
    # -------------------------------------------------------------------------
    def evaluate_case_with_deepeval(
        self,
        query: str,
        actual_output: str,
        retrieval_context: List[str],
        expected_output: str
    ) -> Dict[str, Any]:
        """
        Executes DeepEval evaluation for a single LLMTestCase.
        If LLM is unavailable or fails, returns status 'not_evaluated' with the error.
        Never returns made-up fallback scores.
        """
        try:
            judge_llm = self.get_judge_llm()
            test_case = LLMTestCase(
                input=query,
                actual_output=actual_output,
                expected_output=expected_output,
                retrieval_context=retrieval_context if retrieval_context else ["No evidence retrieved."]
            )

            # Initialize metrics with custom OpenRouter judge
            f_metric = FaithfulnessMetric(threshold=0.70, model=judge_llm)
            ar_metric = AnswerRelevancyMetric(threshold=0.70, model=judge_llm)
            cp_metric = ContextualPrecisionMetric(threshold=0.70, model=judge_llm)
            cr_metric = ContextualRecallMetric(threshold=0.70, model=judge_llm)
            rq_metric = GEval(
                name="Recommendation Quality",
                criteria="actionable, specific to the root cause, feasible for a restaurant manager, grounded in the retrieved reviews",
                evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.RETRIEVAL_CONTEXT],
                model=judge_llm
            )

            f_metric.measure(test_case)
            ar_metric.measure(test_case)
            cp_metric.measure(test_case)
            cr_metric.measure(test_case)
            rq_metric.measure(test_case)

            return {
                "status": "evaluated",
                "faithfulness": round(float(f_metric.score), 4),
                "answer_relevancy": round(float(ar_metric.score), 4),
                "contextual_precision": round(float(cp_metric.score), 4),
                "contextual_recall": round(float(cr_metric.score), 4),
                "recommendation_quality": round(float(rq_metric.score), 4),
                "reasons": {
                    "faithfulness": getattr(f_metric, "reason", ""),
                    "answer_relevancy": getattr(ar_metric, "reason", ""),
                    "contextual_precision": getattr(cp_metric, "reason", ""),
                    "contextual_recall": getattr(cr_metric, "reason", ""),
                    "recommendation_quality": getattr(rq_metric, "reason", "")
                }
            }
        except Exception as e:
            return {
                "status": "not_evaluated",
                "error": str(e),
                "faithfulness": None,
                "answer_relevancy": None,
                "contextual_precision": None,
                "contextual_recall": None,
                "recommendation_quality": None
            }

    # -------------------------------------------------------------------------
    # 3. Transparent Heuristic Proxies (Clearly labeled heuristic_*, never mixed)
    # -------------------------------------------------------------------------
    def heuristic_faithfulness(self, answer: str, context: str) -> float:
        """Clear heuristic proxy: token overlap ratio between answer and context."""
        if not answer or not context:
            return 0.0
        words = set(re.findall(r'\b[a-zA-Z]{4,}\b', answer.lower()))
        if not words:
            return 0.5
        c_lower = context.lower()
        overlap = sum(1 for w in words if w in c_lower)
        return round(overlap / len(words), 4)

    def heuristic_answer_relevancy(self, query: str, answer: str) -> float:
        """Clear heuristic proxy: query keyword coverage in answer."""
        if not query or not answer:
            return 0.0
        q_words = set(re.findall(r'\b[a-zA-Z]{4,}\b', query.lower()))
        if not q_words:
            return 0.5
        a_lower = answer.lower()
        overlap = sum(1 for w in q_words if w in a_lower)
        return round(overlap / len(q_words), 4)

    def heuristic_context_precision(self, query: str, retrieved_docs: List[Dict[str, Any]]) -> float:
        """Clear heuristic proxy: keyword hit rate in retrieved documents."""
        if not query or not retrieved_docs:
            return 0.0
        q_words = set(re.findall(r'\b[a-zA-Z]{4,}\b', query.lower()))
        hits = 0
        for doc in retrieved_docs:
            txt = doc.get("text", "").lower()
            if any(w in txt for w in q_words):
                hits += 1
        return round(hits / len(retrieved_docs), 4)

    def heuristic_context_recall(self, ground_truth: str, retrieved_docs: List[Dict[str, Any]]) -> float:
        """Clear heuristic proxy: ground-truth key term coverage in retrieved context."""
        if not ground_truth or not retrieved_docs:
            return 0.0
        gt_words = set(re.findall(r'\b[a-zA-Z]{4,}\b', ground_truth.lower()))
        if not gt_words:
            return 0.5
        all_context = " ".join([d.get("text", "") for d in retrieved_docs]).lower()
        overlap = sum(1 for w in gt_words if w in all_context)
        return round(overlap / len(gt_words), 4)

    # Legacy / proxy method aliases for test compatibility
    def compute_faithfulness(self, answer: str, context: str) -> float:
        return self.heuristic_faithfulness(answer, context)

    def compute_answer_relevancy(self, query: str, answer: str) -> float:
        return self.heuristic_answer_relevancy(query, answer)

    def compute_context_recall(self, expected_causes: Any, context: str) -> float:
        gt_text = " ".join(expected_causes) if isinstance(expected_causes, list) else str(expected_causes)
        return self.heuristic_context_recall(gt_text, [{"text": context}])

    def evaluate_test_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        rag_svc = get_rag_service()
        ans = rag_svc.answer_query(test_case["query"], k=3)
        citations = ans.get("citations", [])
        c_text = " ".join([c.get("snippet", "") for c in citations])
        f = self.heuristic_faithfulness(ans.get("answer", ""), c_text)
        ar = self.heuristic_answer_relevancy(test_case["query"], ans.get("answer", ""))
        return {
            "id": test_case.get("id"),
            "category": test_case.get("category", "General"),
            "query": test_case["query"],
            "answer": ans.get("answer", ""),
            "citations_count": len(citations),
            "metrics": {
                "faithfulness": f,
                "answer_relevancy": ar,
                "overall_rag_score": round((f + ar) / 2.0, 4)
            }
        }


    # -------------------------------------------------------------------------
    # 4. Master Full Benchmark Evaluation Runner
    # -------------------------------------------------------------------------
    def run_benchmark_evaluation(
        self,
        output_dir: str = "data/eval_results",
        max_cases: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Executes end-to-end evaluation:
        1. Retrieval benchmarks (BM25 vs Vector vs Hybrid RRF)
        2. RAG generation & DeepEval LLM testing
        3. Saves timestamped JSON and latest.json
        """
        os.makedirs(output_dir, exist_ok=True)
        rag_service = get_rag_service()
        cases = BENCHMARK_TEST_CASES[:max_cases] if max_cases else BENCHMARK_TEST_CASES

        # 1. Compute empirical retrieval metrics
        retrieval_benchmarks = self.compute_retrieval_benchmarks(cases)

        # 2. Evaluate generation metrics
        case_results = []
        scores_acc = {
            "faithfulness": [],
            "answer_relevancy": [],
            "contextual_precision": [],
            "contextual_recall": [],
            "recommendation_quality": []
        }
        heuristic_acc = {
            "heuristic_faithfulness": [],
            "heuristic_answer_relevancy": [],
            "heuristic_context_precision": [],
            "heuristic_context_recall": []
        }

        evaluated_count = 0
        not_evaluated_count = 0

        for case in cases:
            query = case["query"]
            expected = case.get("expected_output", "")
            is_out_of_scope = case.get("is_out_of_scope", False)

            # Generate response via RAG
            start_t = time.time()
            rag_res = rag_service.answer_query(query=query, k=5)
            latency_ms = round((time.time() - start_t) * 1000, 2)

            actual_answer = rag_res.get("answer", "")
            citations = rag_res.get("citations", [])
            retrieval_context = [c.get("snippet", "") for c in citations]
            retrieved_docs = [{"text": c.get("snippet", ""), "score": c.get("score", 0.0)} for c in citations]

            # Compute clearly labeled heuristic proxies
            h_f = self.heuristic_faithfulness(actual_answer, " ".join(retrieval_context))
            h_ar = self.heuristic_answer_relevancy(query, actual_answer)
            h_cp = self.heuristic_context_precision(query, retrieved_docs)
            h_cr = self.heuristic_context_recall(expected, retrieved_docs)

            heuristic_acc["heuristic_faithfulness"].append(h_f)
            heuristic_acc["heuristic_answer_relevancy"].append(h_ar)
            heuristic_acc["heuristic_context_precision"].append(h_cp)
            heuristic_acc["heuristic_context_recall"].append(h_cr)

            # DeepEval execution
            de_eval = self.evaluate_case_with_deepeval(
                query=query,
                actual_output=actual_answer,
                retrieval_context=retrieval_context,
                expected_output=expected
            )

            status = de_eval["status"]
            if status == "evaluated":
                evaluated_count += 1
                for metric_key in scores_acc:
                    val = de_eval.get(metric_key)
                    if val is not None:
                        scores_acc[metric_key].append(val)
            else:
                not_evaluated_count += 1

            case_results.append({
                "id": case["id"],
                "category": case["category"],
                "query": query,
                "is_out_of_scope": is_out_of_scope,
                "actual_output": actual_answer,
                "expected_output": expected,
                "latency_ms": latency_ms,
                "status": status,
                "deepeval_scores": {
                    "faithfulness": de_eval.get("faithfulness"),
                    "answer_relevancy": de_eval.get("answer_relevancy"),
                    "contextual_precision": de_eval.get("contextual_precision"),
                    "contextual_recall": de_eval.get("contextual_recall"),
                    "recommendation_quality": de_eval.get("recommendation_quality")
                },
                "heuristic_proxies": {
                    "heuristic_faithfulness": h_f,
                    "heuristic_answer_relevancy": h_ar,
                    "heuristic_context_precision": h_cp,
                    "heuristic_context_recall": h_cr
                },
                "error": de_eval.get("error")
            })

        # 3. Compute aggregate scores
        def calc_mean(lst):
            return round(float(np.mean(lst)), 4) if lst else None

        aggregate_deepeval = {
            "faithfulness": calc_mean(scores_acc["faithfulness"]),
            "answer_relevancy": calc_mean(scores_acc["answer_relevancy"]),
            "contextual_precision": calc_mean(scores_acc["contextual_precision"]),
            "contextual_recall": calc_mean(scores_acc["contextual_recall"]),
            "recommendation_quality": calc_mean(scores_acc["recommendation_quality"])
        }

        aggregate_heuristics = {
            "mean_heuristic_faithfulness": calc_mean(heuristic_acc["heuristic_faithfulness"]),
            "mean_heuristic_answer_relevancy": calc_mean(heuristic_acc["heuristic_answer_relevancy"]),
            "mean_heuristic_context_precision": calc_mean(heuristic_acc["heuristic_context_precision"]),
            "mean_heuristic_context_recall": calc_mean(heuristic_acc["heuristic_context_recall"])
        }

        # Check targets
        pass_fail = {}
        for metric_name, target in self.TARGET_METRICS.items():
            actual = aggregate_deepeval.get(metric_name)
            if actual is not None:
                pass_fail[metric_name] = {
                    "actual": actual,
                    "target": target,
                    "passed": bool(actual >= target)
                }
            else:
                pass_fail[metric_name] = {
                    "actual": None,
                    "target": target,
                    "status": "not_evaluated"
                }

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        report_payload = {
            "evaluation_date": datetime.utcnow().isoformat(),
            "model_used": self.judge_model_name,
            "total_benchmark_cases": len(cases),
            "evaluated_cases": evaluated_count,
            "not_evaluated_cases": not_evaluated_count,
            "aggregate_deepeval_metrics": aggregate_deepeval,
            "target_thresholds": self.TARGET_METRICS,
            "verdict_by_target": pass_fail,
            "retrieval_benchmarks": retrieval_benchmarks,
            "aggregate_heuristic_proxies": aggregate_heuristics,
            "case_results": case_results
        }

        # Write timestamped JSON and latest.json
        ts_filepath = os.path.join(output_dir, f"eval_results_{timestamp}.json")
        latest_filepath = os.path.join(output_dir, "latest.json")

        with open(ts_filepath, "w", encoding="utf-8") as f:
            json.dump(report_payload, f, indent=2)

        with open(latest_filepath, "w", encoding="utf-8") as f:
            json.dump(report_payload, f, indent=2)

        return report_payload


# Global singleton
_evaluator_instance: Optional[RAGEvaluator] = None

def get_rag_evaluator() -> RAGEvaluator:
    global _evaluator_instance
    if _evaluator_instance is None:
        _evaluator_instance = RAGEvaluator()
    return _evaluator_instance

# Backward-compatible alias
get_evaluator = get_rag_evaluator


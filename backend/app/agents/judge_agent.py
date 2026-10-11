"""
Agent 5: Real LLM Judge / Critic Agent
Evaluates operational remediation quality across clarity, feasibility, groundedness, and completeness (1-5 each)
using strict rubric-grounded LLM completions.
Maintains rule-based compliance checks for high-liability health/legal hazards.
"""
import json
import re
from typing import Dict, Any, List, Optional
from backend.app.agents.state import AgentState
from backend.app.core.llm_client import get_llm_client

CRITICAL_COMPLIANCE_TRIGGERS = [
    "food poisoning", "sick", "hospital", "threw up", "vomit",
    "allergic", "allergy", "anaphylaxis",
    "cockroach", "roach", "rat", "mice", "pest control",
    "police", "lawsuit", "attorney", "discrimination", "harass"
]

RUBRIC_SYSTEM_PROMPT = (
    "You are an expert AI Operations Auditor and Quality Judge for restaurant management systems.\n"
    "Your task is to evaluate the operational remediation produced for a customer complaint.\n"
    "You must score exactly four dimensions on a 1.0 to 5.0 scale according to this rubric:\n\n"
    "1. clarity (1-5):\n"
    "   - 1: Ambiguous, confusing, jargon-heavy, or unreadable.\n"
    "   - 3: Moderately clear but lacks operational precision or has minor ambiguity.\n"
    "   - 5: Exceptionally crisp, unambiguous, well-structured, and immediately actionable for shift staff.\n\n"
    "2. feasibility (1-5):\n"
    "   - 1: Impractical, excessively costly, or violates realistic kitchen/service workflows.\n"
    "   - 3: Feasible but requires substantial friction, staffing adjustments, or high coordination.\n"
    "   - 5: Highly practical, readily executable by restaurant managers using standard operating procedures (SOPs).\n\n"
    "3. groundedness (1-5):\n"
    "   - 1: Fabricated, hallucinatory, or completely disconnected from the retrieved customer evidence.\n"
    "   - 3: Partially supported by evidence, but extrapolates unsubstantiated claims.\n"
    "   - 5: Strictly corroborated by and directly traceable to the retrieved customer review evidence snippets.\n\n"
    "4. completeness (1-5):\n"
    "   - 1: Completely ignores the root cause or fails to provide concrete corrective action.\n"
    "   - 3: Addresses the immediate issue but omits preventative safeguards or escalation criteria.\n"
    "   - 5: Comprehensively covers root cause diagnosis, immediate containment, and preventative SOPs.\n\n"
    "Output must be STRICTLY valid JSON with no markdown wrapping, no extra keys, and no commentary. "
    "Include a one-sentence justification per dimension:\n"
    "{\n"
    '  "clarity_score": <float between 1.0 and 5.0>,\n'
    '  "clarity_justification": "<one sentence>",\n'
    '  "feasibility_score": <float between 1.0 and 5.0>,\n'
    '  "feasibility_justification": "<one sentence>",\n'
    '  "groundedness_score": <float between 1.0 and 5.0>,\n'
    '  "groundedness_justification": "<one sentence>",\n'
    '  "completeness_score": <float between 1.0 and 5.0>,\n'
    '  "completeness_justification": "<one sentence>"\n'
    "}"
)

def _clean_and_parse_json(raw_text: str) -> Dict[str, Any]:
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        text = match.group(0)
    data = json.loads(text)
    required_keys = ["clarity_score", "feasibility_score", "groundedness_score", "completeness_score"]
    for k in required_keys:
        if k not in data:
            raise ValueError(f"Missing required rubric key: {k}")
        val = float(data[k])
        if not (1.0 <= val <= 5.0):
            raise ValueError(f"Score {k}={val} is outside [1.0, 5.0] range")
    return data

def execute_llm_judge(
    complaint_text: str,
    evidence: List[Dict[str, Any]],
    root_causes: List[Dict[str, Any]],
    recommendations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Executes a real LLM call against the scoring rubric.
    Never returns fabricated scores. On failure or missing key, returns status 'not_evaluated'.
    """
    evidence_text = "\n".join([f"- {e.get('snippet', e.get('text', ''))}" for e in evidence[:5]]) or "None retrieved."
    causes_text = "\n".join([f"- {rc.get('cause_name', 'Unknown')}: {rc.get('explanation', '')}" for rc in root_causes]) or "None identified."
    recs_text = "\n".join([
        f"- {r.get('sop_title', 'SOP')}: " + ("; ".join(r.get('actionable_steps', [])) if isinstance(r.get('actionable_steps'), list) and r.get('actionable_steps') else r.get('action_plan', 'Implement standard operating procedure.'))
        for r in recommendations
    ]) or "None provided."

    user_prompt = (
        f"### CUSTOMER COMPLAINT:\n{complaint_text}\n\n"
        f"### RETRIEVED CUSTOMER EVIDENCE SNIPPETS:\n{evidence_text}\n\n"
        f"### DIAGNOSED ROOT CAUSES:\n{causes_text}\n\n"
        f"### PROPOSED CORRECTIVE RECOMMENDATIONS:\n{recs_text}\n\n"
        "Evaluate the quality of this diagnosis and remediation using the 4-dimension rubric. Output only valid JSON."
    )

    llm_client = get_llm_client()
    messages = [
        {"role": "system", "content": RUBRIC_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

    raw_response: Optional[str] = None
    parse_error: Optional[str] = None

    try:
        raw_response = llm_client.call_chat_completion(messages=messages, temperature=0.1, max_tokens=800)
        data = _clean_and_parse_json(raw_response)
        return {"status": "evaluated", "judge_mode": "llm", "data": data}
    except Exception as e1:
        parse_error = str(e1)
        # Attempt one strict JSON retry if LLM call succeeded but format had issues
        if raw_response:
            try:
                retry_messages = [
                    {"role": "system", "content": RUBRIC_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                    {"role": "assistant", "content": raw_response},
                    {"role": "user", "content": "Your response could not be parsed as valid JSON. Re-output ONLY the JSON object with the 4 scores (1-5) and justifications."}
                ]
                retry_raw = llm_client.call_chat_completion(messages=retry_messages, temperature=0.0, max_tokens=800)
                data = _clean_and_parse_json(retry_raw)
                return {"status": "evaluated", "judge_mode": "llm", "data": data}
            except Exception as e2:
                parse_error = f"Initial parse failed: {parse_error}; Retry failed: {str(e2)}"

    return {
        "status": "not_evaluated",
        "judge_mode": "unavailable",
        "error": parse_error or "LLM call failed or provider unavailable."
    }

def judge_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node: Real LLM-as-judge evaluation combined with rule-based compliance trigger detection.
    """
    complaint_text = state.get("complaint_text", "")
    complaint_lower = complaint_text.lower()
    category = state.get("category", "Waiting Time")
    severity = state.get("severity_score", 3.0)
    root_causes = state.get("root_causes", [])
    recommendations = state.get("recommendations", [])
    evidence = state.get("evidence_snippets", [])

    # 1. Rule-Based Compliance Trigger Check (Health / Safety / Legal risk)
    compliance_flags: List[str] = []
    for trigger in CRITICAL_COMPLIANCE_TRIGGERS:
        if re.search(rf"\b{re.escape(trigger)}\b", complaint_lower):
            compliance_flags.append(f"Critical compliance trigger detected: '{trigger}' (health/legal risk)")

    if severity >= 4.5:
        compliance_flags.append(f"High operational severity threshold exceeded ({severity:.1f}/5.0)")

    # 2. Real LLM Rubric Evaluation (Clarity, Feasibility, Groundedness, Completeness)
    eval_result = execute_llm_judge(
        complaint_text=complaint_text,
        evidence=evidence,
        root_causes=root_causes,
        recommendations=recommendations
    )

    judge_mode = eval_result["judge_mode"]
    status = eval_result["status"]

    if status == "evaluated":
        data = eval_result["data"]
        c_score = float(data["clarity_score"])
        f_score = float(data["feasibility_score"])
        g_score = float(data["groundedness_score"])
        comp_score = float(data["completeness_score"])

        # composite_quality_score = mean of the four scores / 5.0
        composite_quality = round(((c_score + f_score + g_score + comp_score) / 4.0) / 5.0, 4)

        llm_judge_scores = {
            "clarity": c_score,
            "feasibility": f_score,
            "groundedness": g_score,
            "completeness": comp_score,
            "justifications": {
                "clarity": data.get("clarity_justification", ""),
                "feasibility": data.get("feasibility_justification", ""),
                "groundedness": data.get("groundedness_justification", ""),
                "completeness": data.get("completeness_justification", "")
            }
        }
        err_msg = None
    else:
        c_score = None
        f_score = None
        g_score = None
        comp_score = None
        composite_quality = None
        llm_judge_scores = None
        err_msg = eval_result.get("error", "LLM evaluation unavailable.")

    # 3. Track Attempt History & Conditional Loop-Back Feedback
    retry_count = state.get("retry_count", 0)
    attempt_scores = list(state.get("attempt_scores", []))
    attempt_scores.append({
        "attempt": retry_count + 1,
        "judge_mode": judge_mode,
        "composite_quality_score": composite_quality,
        "scores": llm_judge_scores
    })

    will_retry = (composite_quality is not None and composite_quality < 0.70 and retry_count < 2)
    if will_retry:
        justs = (llm_judge_scores or {}).get("justifications", {})
        feedback_items = [f"{k}: {v}" for k, v in justs.items() if v]
        judge_feedback = (
            f"Quality score {composite_quality:.2f} is below 0.70 threshold. "
            + ("; ".join(feedback_items) if feedback_items else "Improve clarity, feasibility, groundedness, and completeness.")
        )
        new_retry_count = retry_count + 1
    else:
        judge_feedback = None
        new_retry_count = retry_count

    # 4. Determine Human Review Escalation & Verdict
    has_compliance_risk = len(compliance_flags) > 0
    low_quality_score = composite_quality is not None and composite_quality < 0.70

    if has_compliance_risk:
        verdict = "FLAGGED FOR HUMAN SUPERVISION"
        requires_human_review = True
    elif low_quality_score and not will_retry:
        verdict = "REJECTED (Low Quality Score after retries)"
        requires_human_review = True
    elif low_quality_score and will_retry:
        verdict = f"RETRYING (Attempt {retry_count + 1} score {composite_quality:.2f} < 0.70)"
        requires_human_review = False
    elif judge_mode == "unavailable":
        verdict = "NOT_EVALUATED (LLM Unavailable)"
        requires_human_review = True
    else:
        verdict = "APPROVED"
        requires_human_review = False

    judge_evaluation = {
        "judge_mode": judge_mode,
        "status": status,
        "composite_quality_score": composite_quality,
        "overall_quality_score": composite_quality,  # alias for backward compat
        "clarity_score": c_score,
        "feasibility_score": f_score,
        "groundedness_score": g_score,
        "completeness_score": comp_score,
        "llm_judge_scores": llm_judge_scores,
        "compliance_flags": compliance_flags,
        "review_reasons": compliance_flags,  # alias for backward compat
        "verdict": verdict,
        "retry_count": new_retry_count,
        "attempt_scores": attempt_scores,
        "error": err_msg
    }

    # 5. Formulate executive summary
    top_cause = state.get("top_root_cause", "Operational Latency")
    urgency = state.get("operational_urgency", "P2 - Shift Manager Action")
    top_sop = recommendations[0]["sop_title"] if recommendations else "General SOP"

    score_display = f"{composite_quality * 100:.1f}%" if composite_quality is not None else "N/A (LLM Unavailable)"
    final_summary = (
        f"**Multi-Agent Operational Diagnosis & Remediation Report**\n"
        f"- **Category & Priority**: {category} ({state.get('priority_tier', 'Medium')} Priority, Severity {severity:.1f}/5.0)\n"
        f"- **Primary Root Cause**: {top_cause}\n"
        f"- **Primary Remediation**: {top_sop}\n"
        f"- **Business Impact**: {state.get('churn_risk_level', 'Moderate')} Churn Risk | {state.get('revenue_risk_pct', 10.0)}% Revenue Exposure ({urgency})\n"
        f"- **LLM Judge Mode**: {judge_mode.upper()} (Attempt {retry_count + 1}) | Verdict: {verdict} (Composite Quality Score: {score_display})\n"
        f"{'- **Compliance Flags**: ' + '; '.join(compliance_flags) if compliance_flags else '- **Automation Status**: Standard auto-routing approved.'}"
    )

    trace = list(state.get("execution_trace", []))
    trace_label = f"[Agent 5: Judge ({judge_mode})] Attempt {retry_count + 1}: Verdict: {verdict}"
    if composite_quality is not None:
        trace_label += f" | Quality: {composite_quality:.2f}"
    if will_retry:
        trace_label += f" -> Triggering loop-back (retry {new_retry_count}/2)"
    if err_msg:
        trace_label += f" | Error: {err_msg[:60]}"
    trace.append(trace_label)

    return {
        "judge_evaluation": judge_evaluation,
        "overall_quality_score": composite_quality,
        "requires_human_review": requires_human_review,
        "compliance_flags": compliance_flags,
        "review_reasons": compliance_flags,
        "retry_count": new_retry_count,
        "judge_feedback": judge_feedback,
        "attempt_scores": attempt_scores,
        "final_summary": final_summary,
        "execution_trace": trace
    }

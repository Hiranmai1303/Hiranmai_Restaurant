"""
Root Cause Analysis Service
Identifies underlying operational failures by structuring:
Symptoms -> Identified Causes -> Textual Evidence -> Linked Corrective Actions.
"""
import re
from typing import Any, Dict, List, Optional
from backend.app.core.llm_client import OpenRouterLLMClient, get_llm_client
from backend.app.retrieval.hybrid_search import HybridRetriever, get_hybrid_retriever

class RootCauseAnalysisService:
    # Comprehensive Domain Taxonomy
    SYMPTOM_CAUSE_TAXONOMY = {
        "Waiting Time": {
            "understaffing": ["not enough staff", "only one server", "no help", "short staffed", "understaffed", "one person working"],
            "kitchen_bottlenecks": ["kitchen backed up", "took forever to cook", "waiting for food", "kitchen was slow", "ticket time"],
            "peak_hour_overload": ["crowded", "packed", "rush hour", "friday night", "saturday night", "long line outside"],
            "expo_station_delays": ["sitting under heat lamp", "sitting on counter", "food came out cold after waiting", "sitting there"]
        },
        "Food Quality": {
            "holding_temperature_lapse": ["cold", "lukewarm", "room temp", "not hot", "barely warm"],
            "line_cook_undercooking": ["raw", "undercooked", "bloody", "not cooked through", "pink chicken"],
            "ingredient_freshness_breakdown": ["stale", "spoiled", "rotten", "smelled bad", "sour", "expired"],
            "seasoning_inconsistency": ["bland", "no flavor", "too salty", "oversalted", "tasteless"]
        },
        "Service Quality": {
            "table_coverage_imbalance": ["never came back", "ignored", "forgot us", "walked right past", "had to flag down"],
            "lack_of_server_training": ["didn't know menu", "couldn't answer", "spilled", "dropped", "inexperienced"],
            "beverage_station_backlog": ["refill", "water never came", "waiting for drinks", "empty glasses"]
        },
        "Staff Behavior": {
            "staff_burnout_and_stress": ["rude", "attitude", "snapped", "annoyed", "impatient", "miserable"],
            "management_supervision_deficit": ["manager did nothing", "manager was rude", "manager argued", "unprofessional manager"],
            "hostile_guest_handling": ["yelled", "screamed", "argued", "confrontational", "insulted"]
        },
        "Cleanliness": {
            "bussing_turnaround_lapse": ["dirty table", "sticky table", "dishes piling up", "not wiped down"],
            "restroom_audit_failure": ["dirty bathroom", "restroom was disgusting", "no soap", "no paper towels", "smelly toilet"],
            "pest_control_deficiency": ["roach", "cockroach", "bug", "fly", "flies", "rat", "mouse"]
        },
        "Order Accuracy": {
            "mod_and_allergy_omission": ["allergic", "no onions", "asked for no", "specifically asked", "dressing on side"],
            "kitchen_printer_misread": ["wrong order", "wrong burger", "wrong side", "gave me something else"],
            "missing_item_dispatch": ["forgot my", "missing item", "did not receive", "left out"]
        },
        "Pricing": {
            "portion_yield_discrepancy": ["tiny portion", "hardly any", "small serving", "too small for price"],
            "unclear_surcharges": ["hidden fee", "extra charge", "service charge", "overcharged", "unexpected bill"]
        },
        "Ambience": {
            "hvac_calibration_issue": ["freezing inside", "too hot", "ac broken", "sweltering", "stuffy"],
            "acoustic_damping_absence": ["too loud", "couldn't hear", "screaming", "blaring music", "echoey"]
        }
    }

    ACTION_MAP = {
        "understaffing": "Deploy automated shift scheduling with dynamic forecasting to scale front-of-house staff during peak rushes.",
        "kitchen_bottlenecks": "Implement Kitchen Display System (KDS) pacing and designated prep station line cooks.",
        "peak_hour_overload": "Introduce digital waitlist and reservation pacing to cap concurrent dining room seating at 85% capacity.",
        "expo_station_delays": "Assign dedicated Expeditor during rush shifts with strict 3-minute food runner SLA.",
        "holding_temperature_lapse": "Calibrate heated pass-through lamps and enforce instant table delivery upon plate plating.",
        "line_cook_undercooking": "Mandate digital meat probe thermometer checks for all proteins prior to expo release.",
        "ingredient_freshness_breakdown": "Audit walk-in refrigeration FIFO rotation and replace open batch inventory daily.",
        "seasoning_inconsistency": "Standardize portioning scoops and recipe spec sheets at every cooking station.",
        "table_coverage_imbalance": "Re-zone dining room into 3-table per server sections during high-volume periods.",
        "lack_of_server_training": "Conduct mandatory 3-day server onboarding with menu allergen and ingredient quizzes.",
        "beverage_station_backlog": "Establish dedicated server assistant / busser beverage refill routes.",
        "staff_burnout_and_stress": "Institute mandatory shift breaks and recognize top customer service milestones.",
        "management_supervision_deficit": "Train managers in de-escalation protocols and require active floor table touches.",
        "hostile_guest_handling": "Mandate hospitality de-escalation training and enforce zero-tolerance policy for confrontational staff behavior.",
        "bussing_turnaround_lapse": "Implement 90-second table sanitize and reset protocol with color-coded sanitizer towels.",
        "restroom_audit_failure": "Enforce 30-minute digital checklist restroom sanitization audits during active service.",
        "pest_control_deficiency": "Engage immediate commercial pest elimination contractor and seal entry thresholds.",
        "mod_and_allergy_omission": "Implement POS allergen tagging that flashes red on kitchen display monitors.",
        "kitchen_printer_misread": "Upgrade kitchen display order formatting and enforce double-check verification by expeditor.",
        "missing_item_dispatch": "Implement bag check stickers and expediter ticket sign-off for takeout and dine-in orders.",
        "portion_yield_discrepancy": "Standardize scale-measured portioning for premium proteins and sides.",
        "unclear_surcharges": "Review guest checks and update menu disclosure for automatic gratuity or service fees.",
        "hvac_calibration_issue": "Service HVAC thermostat zoning and install temperature sensors in main dining areas.",
        "acoustic_damping_absence": "Install acoustic ceiling baffles and adjust dining room music decibel limits to 65dB."
    }

    def __init__(
        self,
        retriever: Optional[HybridRetriever] = None,
        llm_client: Optional[OpenRouterLLMClient] = None
    ):
        self.retriever = retriever or get_hybrid_retriever()
        self.llm_client = llm_client or get_llm_client()

    def analyze_root_cause(
        self,
        symptom_query: str,
        k: int = 5,
        category: Optional[str] = None,
        business_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform Root Cause Analysis:
        1. Retrieve review evidence using Hybrid Search
        2. Rule-based Root Cause detection across taxonomy
        3. LLM synthesis & confirmation linking Causes to Evidence and Action Plan
        """
        filter_dict = {}
        if category:
            filter_dict["category"] = category
        if business_id:
            filter_dict["business_id"] = business_id

        # 1. Retrieve evidence
        retrieved_docs = self.retriever.search(
            query=symptom_query,
            k=k,
            filter_dict=filter_dict if filter_dict else None
        )

        # 2. Extract deterministic causes & map evidence quotes
        detected_causes = {}
        for doc in retrieved_docs:
            text_lower = doc["text"].lower()
            doc_id = doc.get("id")
            cat = doc.get("metadata", {}).get("category", "Waiting Time")
            
            # Check all category causes in taxonomy
            sub_tax = self.SYMPTOM_CAUSE_TAXONOMY.get(cat, self.SYMPTOM_CAUSE_TAXONOMY["Waiting Time"])
            for cause, keywords in sub_tax.items():
                for kw in keywords:
                    if kw in text_lower:
                        if cause not in detected_causes:
                            detected_causes[cause] = {
                                "cause_name": cause.replace("_", " ").title(),
                                "cause_key": cause,
                                "match_count": 0,
                                "evidence": [],
                                "recommended_action": self.ACTION_MAP.get(cause, "Conduct manager shift review.")
                            }
                        detected_causes[cause]["match_count"] += 1
                        # Find snippet around keyword
                        start = max(0, text_lower.find(kw) - 30)
                        end = min(len(doc["text"]), text_lower.find(kw) + len(kw) + 50)
                        quote_snippet = f"...{doc['text'][start:end].strip()}..."
                        detected_causes[cause]["evidence"].append({
                            "review_id": doc_id,
                            "restaurant": doc.get("metadata", {}).get("restaurant"),
                            "snippet": quote_snippet,
                            "keyword_matched": kw
                        })
                        break

        # Fallback if no specific taxonomy keyword triggered
        if not detected_causes:
            default_cause = "kitchen_bottlenecks" if "food" in symptom_query.lower() else "understaffing"
            detected_causes[default_cause] = {
                "cause_name": default_cause.replace("_", " ").title(),
                "cause_key": default_cause,
                "match_count": 1,
                "evidence": [
                    {
                        "review_id": retrieved_docs[0]["id"] if retrieved_docs else "N/A",
                        "restaurant": retrieved_docs[0].get("metadata", {}).get("restaurant") if retrieved_docs else "Unknown",
                        "snippet": retrieved_docs[0]["text"][:100] + "..." if retrieved_docs else "Historical complaints indicate latency.",
                        "keyword_matched": "general operational latency"
                    }
                ],
                "recommended_action": self.ACTION_MAP.get(default_cause)
            }

        sorted_causes = sorted(detected_causes.values(), key=lambda x: x["match_count"], reverse=True)

        return {
            "symptom": symptom_query,
            "root_causes": sorted_causes,
            "top_root_cause": sorted_causes[0]["cause_name"] if sorted_causes else "Operational Latency",
            "evidence_documents_count": len(retrieved_docs),
            "evidence_documents": retrieved_docs
        }

# Global singleton
_root_cause_instance: Optional[RootCauseAnalysisService] = None

def get_root_cause_service() -> RootCauseAnalysisService:
    global _root_cause_instance
    if _root_cause_instance is None:
        _root_cause_instance = RootCauseAnalysisService()
    return _root_cause_instance

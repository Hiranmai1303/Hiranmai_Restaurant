"""
Evaluation Benchmark Dataset for Restaurant Operations RAG System
Standardized evaluation queries, ground truth references, and operational categories.
"""
from typing import Any, Dict, List

BENCHMARK_TEST_CASES: List[Dict[str, Any]] = [
    {
        "id": "TC_EVAL_01",
        "category": "Waiting Time",
        "query": "What are the primary factors contributing to long customer wait times during peak dinner rushes?",
        "ground_truth": "Long wait times are primarily caused by front-of-house understaffing, kitchen ticket bottlenecks, expo station delays, and dining room seating over-capacity.",
        "expected_root_causes": ["understaffing", "kitchen_bottlenecks", "peak_hour_overload", "expo_station_delays"]
    },
    {
        "id": "TC_EVAL_02",
        "category": "Food Quality",
        "query": "Why are guests reporting that hot entrees are arriving cold or lukewarm at tables?",
        "ground_truth": "Entrees are served cold due to holding temperature lapses under heat lamps, lack of dedicated food runners, and delayed table delivery after plating.",
        "expected_root_causes": ["holding_temperature_lapse", "expo_station_delays"]
    },
    {
        "id": "TC_EVAL_03",
        "category": "Service Quality",
        "query": "What causes complaints regarding server inattentiveness and slow drink refills?",
        "ground_truth": "Inattentive service stems from unbalanced server table section zoning, server onboarding deficits, and beverage station backlogs during high-volume shifts.",
        "expected_root_causes": ["table_coverage_imbalance", "lack_of_server_training", "beverage_station_backlog"]
    },
    {
        "id": "TC_EVAL_04",
        "category": "Staff Behavior",
        "query": "What operational factors trigger rude staff interactions and confrontational manager behavior?",
        "ground_truth": "Rude staff behavior is triggered by peak shift stress and burnout, lack of supervisor de-escalation training, and management supervision deficits.",
        "expected_root_causes": ["staff_burnout_and_stress", "management_supervision_deficit", "hostile_guest_handling"]
    },
    {
        "id": "TC_EVAL_05",
        "category": "Cleanliness",
        "query": "Why are customers experiencing dirty tables and unsanitary restroom conditions?",
        "ground_truth": "Cleanliness issues arise from bussing turnaround lapses during peak rushes and failure to execute scheduled 30-minute restroom sanitization audits.",
        "expected_root_causes": ["bussing_turnaround_lapse", "restroom_audit_failure", "pest_control_deficiency"]
    },
    {
        "id": "TC_EVAL_06",
        "category": "Pricing",
        "query": "What drives customer dissatisfaction with menu pricing and perceived poor value?",
        "ground_truth": "Pricing complaints are driven by portion yield discrepancies and unexpected automatic gratuity or hidden service surcharges.",
        "expected_root_causes": ["portion_yield_discrepancy", "unclear_surcharges"]
    },
    {
        "id": "TC_EVAL_07",
        "category": "Order Accuracy",
        "query": "What causes frequent incorrect orders and missing items in takeout packaging?",
        "ground_truth": "Order inaccuracies occur due to kitchen printer display misreads, omission of allergy modifications, and lack of expediter bag checklist verification.",
        "expected_root_causes": ["kitchen_printer_misread", "mod_and_allergy_omission", "missing_item_dispatch"]
    },
    {
        "id": "TC_EVAL_08",
        "category": "Ambience",
        "query": "Why are guests complaining about excessive dining room noise and uncomfortable room temperatures?",
        "ground_truth": "Ambience issues result from lack of acoustic damping baffles during peak crowds and uncalibrated HVAC dining room thermostats.",
        "expected_root_causes": ["acoustic_damping_absence", "hvac_calibration_issue"]
    }
]

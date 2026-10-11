"""
Root Cause Analysis Demonstration Script
Executes RCA queries, mapping operational symptoms to underlying causes,
textual evidence snippets, and corrective action plans.
"""
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.services.root_cause_service import get_root_cause_service

def main():
    service = get_root_cause_service()
    
    test_symptoms = [
        "Slow Service and 45 minute dinner delay",
        "Cold food and raw chicken served",
        "Rude staff and unhelpful manager",
        "Dirty restroom and uncleaned tables"
    ]

    for symptom in test_symptoms:
        print("\n" + "="*80)
        print(f"OPERATIONAL SYMPTOM: \"{symptom}\"")
        print("="*80)

        report = service.analyze_root_cause(symptom_query=symptom, k=5)
        print(f"Top Diagnosed Root Cause: {report['top_root_cause']}")
        print(f"Total Evidence Documents Analyzed: {report['evidence_documents_count']}\n")

        print("--- IDENTIFIED ROOT CAUSES & LINKED EVIDENCE ---")
        for idx, cause in enumerate(report["root_causes"], 1):
            print(f"[{idx}] Root Cause: {cause['cause_name']} (Evidence Matches: {cause['match_count']})")
            print(f"    Corrective Action: {cause['recommended_action']}")
            print("    Evidence Quotations:")
            for ev in cause["evidence"][:2]:
                print(f"      • [{ev['restaurant']} | ID: {ev['review_id']}] (Matched: \"{ev['keyword_matched']}\")")
                print(f"        \"{ev['snippet']}\"")
            print()

if __name__ == "__main__":
    main()

import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.agents import run_multi_agent_workflow

SAMPLE_COMPLAINTS = [
    (
        "Standard Operational Latency",
        "We waited over 55 minutes for our entrees on Saturday night. The kitchen was totally backed up and only one server was running around."
    ),
    (
        "Critical Food Poisoning & Hygiene Flag",
        "The chicken was completely raw in the center and undercooked! I got severe food poisoning, threw up all night, and had to visit the hospital emergency room!"
    ),
    (
        "Staff Hostility & Service Incident",
        "The manager yelled at our table when we politely asked why our bill had unauthorized hidden service fees."
    )
]

def main():
    print("==================================================================")
    print("  AI-POWERED RESTAURANT OPERATIONS: 5-AGENT LANGGRAPH PIPELINE   ")
    print("==================================================================")
    
    for title, complaint in SAMPLE_COMPLAINTS:
        print(f"\n>>> Scenario: {title}")
        print(f"Complaint Input: \"{complaint}\"")
        print("-" * 66)
        
        result = run_multi_agent_workflow(
            complaint_text=complaint,
            restaurant_name="Bistro Lumiere"
        )
        
        print(f"1. Category Detected   : {result.get('category')} (Severity: {result.get('severity_score'):.1f}/5.0 - {result.get('priority_tier')} Priority)")
        print(f"2. Top Root Cause     : {result.get('top_root_cause')}")
        print(f"3. Operational SOP     : {result.get('recommendations', [{}])[0].get('sop_title', 'N/A')}")
        print(f"4. Business Risk       : {result.get('churn_risk_level')} Churn Risk | {result.get('revenue_risk_pct')}% Rev Exposure | Urgency: {result.get('operational_urgency')}")
        print(f"5. LLM Judge Review    : Verdict={result.get('judge_evaluation', {}).get('verdict')} (Quality Score: {result.get('overall_quality_score')})")
        
        if result.get("requires_human_review"):
            print(f"   [!] ESCALATION REASONS: {result.get('review_reasons')}")
            
        print("\nExecution Trace:")
        for step in result.get("execution_trace", []):
            print(f"   -> {step}")
            
    print("\n==================================================================")
    print("  PHASE 11 MULTI-AGENT EXECUTION COMPLETE                         ")
    print("==================================================================")

if __name__ == "__main__":
    main()

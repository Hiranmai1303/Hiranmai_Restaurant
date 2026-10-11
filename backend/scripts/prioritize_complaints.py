"""
Complaint Prioritization Analysis Script
Queries SQLite database, evaluates multi-factor prioritization,
and outputs tier distribution and critical High-priority action items.
"""
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.services.prioritization_service import get_prioritization_service

def main():
    service = get_prioritization_service()
    print("1. Running Multi-Factor Complaint Prioritization Engine...")

    rankings = service.get_restaurant_priority_rankings(limit=15)
    
    tier_counts = {"High": 0, "Medium": 0, "Low": 0}
    for r in rankings:
        t = r["priority_tier"]
        tier_counts[t] = tier_counts.get(t, 0) + 1

    print("\n" + "="*80)
    print("OPERATIONAL COMPLAINT PRIORITY RANKINGS")
    print("="*80)
    print(f"Sample Tier Summary: High: {tier_counts['High']} | Medium: {tier_counts['Medium']} | Low: {tier_counts['Low']}\n")

    for i, item in enumerate(rankings, 1):
        tier = item["priority_tier"]
        color_tag = "[CRITICAL ACTION REQUIRED]" if tier == "High" else ("[ACTION RECOMMENDED]" if tier == "Medium" else "[MONITOR]")
        
        print(f"#{i} [{tier.upper()} PRIORITY - Score: {item['priority_score']}/100] {color_tag}")
        print(f"   Restaurant: {item['restaurant_name']} | Category: {item['category']} | Aspect: {item['aspect']}")
        print(f"   Rating: {item['stars']} Stars | Severity: {item['severity_score']}/5 | Recurrence: {item['recurrence_count']}x")
        print(f"   Factor Breakdown: Stars: {item['factor_breakdown']['star_factor']} | Severity: {item['factor_breakdown']['severity_factor']} | Sentiment: {item['factor_breakdown']['sentiment_factor']} | Useful: {item['factor_breakdown']['useful_factor']} | Recurrence: {item['factor_breakdown']['frequency_factor']}")
        print(f"   Excerpt: \"{item['text'][:120]}...\"\n")

if __name__ == "__main__":
    main()

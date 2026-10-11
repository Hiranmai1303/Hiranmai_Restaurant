"""
Input Validation & Guardrails Service
Provides deterministic security and domain filtering:
- Query length and empty string checks
- Prompt injection and jailbreak pattern detection
- Domain relevance guardrails (restaurant operations and customer review scope)
- Out-of-scope inquiry filtering (coding, math, general AI queries)
- Safe fallback response generation
"""
import re
import sqlite3
from typing import Dict, Any, Optional, Set
from backend.app.core.config import settings

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"system\s+prompt\s+override",
    r"reveal\s+(your\s+)?system\s+prompt",
    r"you\s+are\s+now\s+dan",
    r"bypass\s+safety",
    r"ignore\s+guardrails",
    r"act\s+as\s+an\s+unrestricted",
    r"<script>",
    r"DROP\s+TABLE",
    r"SELECT\s+\*\s+FROM",
]

EXPLICIT_OUT_OF_SCOPE_PATTERNS = [
    r"(write|generate|create|give\s+me|show\s+me|build)\s+(a\s+)?(python|javascript|js|java|c\+\+|c#|ruby|php|golang|rust|html|css|sql|code|script|function|program|algorithm|class|method|regex)",
    r"(python|javascript|js|java|c\+\+|golang|rust|html|css|sql)\s+(code|script|program|solution|implementation)",
    r"prime\s+numbers?",
    r"fibonacci",
    r"binary\s+tree",
    r"sorting\s+algorithm",
    r"how\s+to\s+(hack|code|program|build\s+an\s+app|make\s+money|invest)",
    r"stock\s+market|bitcoin|cryptocurrency|crypto|blockchain|forex",
    r"medical\s+(advice|diagnosis|prescription)|prescribe|cure\s+for",
    r"legal\s+(contract|advice|clause|lawsuit)",
    r"what\s+is\s+the\s+capital\s+of",
    r"who\s+(won|is|was|invented)\s+the",
    r"tell\s+me\s+a\s+(joke|story|poem|song)",
    r"translate\s+(this\s+)?to\s+",
    r"weather\s+(in|forecast|today)",
    r"calculate\s+\d+",
    r"solve\s+(the\s+)?equation",
]

DOMAIN_KEYWORDS = [
    # Food, Beverage & Dining
    "food", "dish", "dishes", "meal", "meals", "taste", "flavor", "drink", "drinks", "beverage", "beverages",
    "cocktail", "cocktails", "beer", "wine", "steak", "steaks", "burger", "burgers", "pizza", "pizzas",
    "pasta", "salad", "salads", "chicken", "meat", "seafood", "fish", "dessert", "desserts", "soup",
    "appetizer", "appetizers", "entree", "entrees", "menu", "menus", "portion", "portions", "ingredient",
    "raw", "undercooked", "overcooked", "cold", "salty", "spicy", "bland", "fresh", "stale", "tasty", "delicious",
    
    # Service, Staff & Hospitality
    "service", "staff", "waiter", "waiters", "waitress", "waitresses", "server", "servers", "host", "hosts",
    "hostess", "hostesses", "bartender", "bartenders", "manager", "managers", "chef", "chefs", "cook", "cooks",
    "employee", "employees", "crew", "attitude", "rude", "friendly", "polite", "neglect", "neglected", "ignored",
    "inattentive", "unprofessional", "helpful", "greet", "greeting", "hospitality",
    
    # Time, Queue & Operations
    "wait", "waiting", "delay", "delayed", "slow", "fast", "rush", "hour", "hours", "table", "tables",
    "seat", "seating", "seated", "reservation", "reservations", "line", "lines", "queue", "queues",
    "prep", "kitchen", "expo", "delivery", "takeout", "pickup", "order", "orders", "ordered", "bill",
    "bills", "check", "checks", "receipt", "receipts", "pos", "ticket", "tickets", "turnover", "turnaround",
    "sla", "shift", "bottleneck", "bottlenecks", "speed", "traffic",
    
    # Hygiene, Environment & Ambience
    "clean", "cleanliness", "dirty", "dirtiness", "hygiene", "sanitary", "sanitized", "restroom", "restrooms",
    "bathroom", "bathrooms", "floor", "floors", "smell", "sticky", "ambience", "ambiance", "atmosphere",
    "noise", "noisy", "loud", "music", "lighting", "decor", "vibe",
    
    # Financial, Value & Pricing
    "price", "prices", "pricing", "expensive", "overpriced", "cheap", "cost", "costs", "value", "charge",
    "charges", "charged", "fee", "fees", "surcharge", "surcharges", "tip", "tips", "gratuity", "gratuities",
    "refund", "refunds", "discount", "discounts", "coupon", "coupons", "bill", "billing",
    
    # Customer Feedback, Reviews & Operational Analytics
    "restaurant", "restaurants", "bistro", "bistros", "cafe", "cafes", "diner", "diners", "eatery", "eateries",
    "bar", "bars", "grill", "pub", "pubs", "yelp", "review", "reviews", "reviewer", "reviewers", "complaint",
    "complaints", "complaining", "complained", "customer", "customers", "guest", "guests", "patron", "patrons",
    "rating", "ratings", "star", "stars", "experience", "sentiment", "trend", "trends", "forecast", "forecasting",
    "priority", "prioritize", "root cause", "operational", "operations", "remedy", "sop", "action", "actions",
    "improve", "improvement", "satisfaction", "churn", "issue", "issues", "problem", "problems", "feedback",
    "defect", "defects", "accuracy", "error", "errors", "mistake", "mistakes", "incident", "incidents"
]

class GuardrailsService:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.SQLITE_DB_PATH
        self.injection_regexes = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]
        self.out_of_scope_regexes = [re.compile(p, re.IGNORECASE) for p in EXPLICIT_OUT_OF_SCOPE_PATTERNS]
        self._domain_keywords_set: Set[str] = set(k.lower() for k in DOMAIN_KEYWORDS)
        self._cached_restaurant_names: Optional[Set[str]] = None

    def _get_restaurant_names(self) -> Set[str]:
        if self._cached_restaurant_names is None:
            names: Set[str] = set()
            try:
                conn = sqlite3.connect(self.db_path)
                cur = conn.cursor()
                cur.execute("SELECT DISTINCT LOWER(restaurant_name) FROM enriched_reviews WHERE restaurant_name IS NOT NULL")
                rows = cur.fetchall()
                conn.close()
                for r in rows:
                    if r[0] and len(r[0].strip()) > 2:
                        names.add(r[0].strip())
            except Exception:
                pass
            self._cached_restaurant_names = names
        return self._cached_restaurant_names

    def validate_query(self, query: str) -> Dict[str, Any]:
        """
        Validates user query against length, prompt injection, and domain relevance rules.
        """
        if not query or not query.strip():
            return {
                "is_valid": False,
                "reason": "EMPTY_QUERY",
                "message": "Query cannot be empty. Please enter an operational question about restaurant reviews."
            }

        cleaned = query.strip()
        q_lower = cleaned.lower()

        if len(cleaned) > 1500:
            return {
                "is_valid": False,
                "reason": "QUERY_TOO_LONG",
                "message": "Query exceeds the maximum allowable length (1500 characters). Please provide a concise inquiry."
            }

        # 1. Check prompt injection
        for regex in self.injection_regexes:
            if regex.search(cleaned):
                return {
                    "is_valid": False,
                    "reason": "SECURITY_PROMPT_INJECTION",
                    "message": "Query contains restricted prompt manipulation patterns. Please ask operational questions about restaurant reviews."
                }

        # 2. Check explicit out-of-scope patterns (coding, prime numbers, math, general AI tasks)
        for regex in self.out_of_scope_regexes:
            if regex.search(cleaned):
                return {
                    "is_valid": False,
                    "reason": "OUT_OF_SCOPE",
                    "message": f"The query '{cleaned}' is outside the scope of restaurant operations and customer review analytics. Please enter an inquiry related to food quality, waiting time, customer service, cleanliness, pricing, staff behavior, or restaurant performance."
                }

        # 3. Check Domain Relevance (Keyword & Entity Match)
        # Tokenize query into words
        words = set(re.findall(r'\b[a-z]{3,}\b', q_lower))
        has_domain_keyword = bool(words.intersection(self._domain_keywords_set))

        # Check matching any known restaurant entity
        has_restaurant_match = False
        rest_names = self._get_restaurant_names()
        for name in rest_names:
            if name in q_lower:
                has_restaurant_match = True
                break

        # If query has neither restaurant domain keywords nor known restaurant names
        if not has_domain_keyword and not has_restaurant_match:
            return {
                "is_valid": False,
                "reason": "DOMAIN_IRRELEVANT",
                "message": f"The query '{cleaned}' does not appear relevant to restaurant operations or customer reviews. Please ask about operational topics such as service delays, food quality, staff performance, cleanliness, pricing, or customer complaints."
            }

        return {
            "is_valid": True,
            "reason": "PASSED",
            "message": "Query validated successfully."
        }

_guardrails_service_instance: Optional[GuardrailsService] = None

def get_guardrails_service() -> GuardrailsService:
    global _guardrails_service_instance
    if _guardrails_service_instance is None:
        _guardrails_service_instance = GuardrailsService()
    return _guardrails_service_instance

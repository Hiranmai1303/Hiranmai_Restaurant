"""
Complaint Enrichment Service
Categorizes reviews into 8 operational categories:
1. Food Quality
2. Service Quality
3. Waiting Time
4. Cleanliness
5. Pricing
6. Staff Behavior
7. Order Accuracy
8. Ambience

Generates sentiment, aspect, severity_score (1-5), and priority_score (1-100).
"""
import re
from typing import Dict, List, Tuple

class ComplaintEnrichmentService:
    CATEGORIES = [
        "Food Quality",
        "Service Quality",
        "Waiting Time",
        "Cleanliness",
        "Pricing",
        "Staff Behavior",
        "Order Accuracy",
        "Ambience"
    ]

    KEYWORD_TAXONOMY = {
        "Food Quality": [
            "raw", "undercooked", "overcooked", "burnt", "cold", "stale", "salty",
            "bland", "taste", "flavor", "sour", "spoiled", "rotten", "greasy",
            "dry", "inedible", "terrible food", "bad food", "disgusting", "poisoning", "sick", "hair in"
        ],
        "Waiting Time": [
            "slow", "wait", "waited", "waiting", "delay", "delayed", "took forever",
            "long time", "hour", "minutes", "eternity", "line", "slow service",
            "never came", "standing in line", "backed up"
        ],
        "Service Quality": [
            "service", "server", "attentive", "ignored", "neglected", "unresponsive",
            "slow service", "poor service", "horrible service", "bad service", "forgetful", "refill"
        ],
        "Staff Behavior": [
            "rude", "attitude", "disrespectful", "impolite", "arrogant", "hostile",
            "yelled", "unfriendly", "manager was rude", "waiter was rude", "waitress was rude",
            "unprofessional", "condescending", "ignored us"
        ],
        "Cleanliness": [
            "dirty", "filthy", "gross", "unclean", "smell", "stink", "odor",
            "bug", "roach", "fly", "flies", "rat", "mice", "sticky",
            "bathroom was disgusting", "restroom", "trash", "sanitation", "hair"
        ],
        "Pricing": [
            "expensive", "overpriced", "price", "cost", "rip off", "ripoff",
            "charge", "overcharged", "bill", "hidden fee", "not worth", "portion size too small"
        ],
        "Order Accuracy": [
            "wrong order", "mistake", "missing", "forgot", "wrong item", "incorrect",
            "did not order", "allergies ignored", "wrong food", "swapped", "missing item"
        ],
        "Ambience": [
            "noisy", "loud", "dark", "crowded", "cramped", "music too loud",
            "lighting", "seating", "uncomfortable", "cold inside", "hot inside", "ac broken", "smoky"
        ]
    }

    SEVERITY_KEYWORDS = {
        5: ["poisoning", "hospital", "food poisoning", "vomit", "sick", "roach", "rat", "racist", "assault", "police", "health department"],
        4: ["inedible", "disgusting", "horrible", "awful", "unacceptable", "yelled", "screamed", "swindled", "infestation", "rotten"],
        3: ["bad", "rude", "dirty", "overpriced", "ignored", "cold food", "wrong order", "slow", "terrible"],
        2: ["bland", "mediocre", "disappointing", "average", "lukewarm", "pricey", "noisy"],
        1: ["okay", "decent", "fine", "minor", "small issue"]
    }

    def analyze_sentiment(self, text: str, stars: float) -> str:
        """Determine sentiment category based on star rating and text markers."""
        if stars <= 2.0:
            return "Negative"
        elif stars == 3.0:
            lower = text.lower()
            negative_hits = sum(1 for kw in ["bad", "poor", "slow", "rude", "dirty", "disappointed", "cold"] if kw in lower)
            positive_hits = sum(1 for kw in ["good", "great", "nice", "enjoyed", "friendly", "delicious"] if kw in lower)
            if negative_hits > positive_hits:
                return "Negative"
            elif positive_hits > negative_hits:
                return "Positive"
            return "Neutral"
        else:
            return "Positive"

    def classify_complaint(self, text: str) -> Tuple[str, str]:
        """
        Classifies review into primary operational category and specific aspect.
        Returns (complaint_category, aspect).
        """
        lower = text.lower()
        scores = {}
        aspect_matches = {}

        for cat, keywords in self.KEYWORD_TAXONOMY.items():
            matched_kws = [kw for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', lower)]
            if matched_kws:
                scores[cat] = len(matched_kws)
                aspect_matches[cat] = matched_kws[0]

        if not scores:
            return ("General Operational", "general feedback")

        # Pick category with highest matched keyword frequency
        best_cat = max(scores, key=scores.get)
        aspect = aspect_matches.get(best_cat, "general " + best_cat.lower())
        return (best_cat, aspect)

    def calculate_severity_score(self, text: str, stars: float) -> int:
        """Calculate severity score on a 1-5 integer scale."""
        lower = text.lower()
        
        # Check critical 5-star severity triggers first
        for level in [5, 4, 3, 2]:
            for kw in self.SEVERITY_KEYWORDS[level]:
                if kw in lower:
                    return level

        if stars == 1.0:
            return 4
        elif stars == 2.0:
            return 3
        elif stars == 3.0:
            return 2
        else:
            return 1

    def calculate_priority_score(
        self,
        stars: float,
        severity_score: int,
        sentiment: str,
        useful_votes: int,
        is_complaint: bool
    ) -> float:
        """
        Calculate composite priority score between 1.0 and 100.0.
        Higher score = requires immediate managerial intervention.
        """
        if not is_complaint and stars >= 4.0 and sentiment == "Positive":
            return round(max(1.0, 15.0 - stars * 2), 2)

        # Base score from low stars (1 star = 40 pts, 2 stars = 30 pts, 3 stars = 20 pts)
        star_penalty = max(0.0, (5.0 - stars) * 10.0)

        # Severity contribution (1-5 scaled up to 35 pts)
        severity_contribution = severity_score * 7.0

        # Sentiment contribution
        sentiment_contribution = 15.0 if sentiment == "Negative" else (5.0 if sentiment == "Neutral" else 0.0)

        # Social validation / Useful votes multiplier (up to 10 pts)
        useful_boost = min(float(useful_votes) * 2.0, 10.0)

        raw_score = star_penalty + severity_contribution + sentiment_contribution + useful_boost
        return round(min(100.0, max(1.0, raw_score)), 2)

    def enrich_record(self, record: dict) -> dict:
        """Enrich a single review record dictionary."""
        text = record.get("text", "")
        stars = float(record.get("stars", 3.0))
        useful = int(record.get("useful", 0))

        sentiment = self.analyze_sentiment(text, stars)
        category, aspect = self.classify_complaint(text)
        is_complaint = (stars <= 3.0) or (sentiment == "Negative") or (category != "General Operational")

        severity = self.calculate_severity_score(text, stars)
        priority = self.calculate_priority_score(
            stars=stars,
            severity_score=severity,
            sentiment=sentiment,
            useful_votes=useful,
            is_complaint=is_complaint
        )

        return {
            **record,
            "is_complaint": is_complaint,
            "sentiment": sentiment,
            "complaint_category": category,
            "aspect": aspect,
            "severity_score": severity,
            "priority_score": priority
        }

    def enrich_review(self, text: str, stars: float = 2.0, useful: int = 0) -> dict:
        """Enrich a single review string directly."""
        return self.enrich_record({
            "text": text,
            "stars": stars,
            "useful": useful
        })

_enrichment_instance = None

def get_enrichment_service() -> ComplaintEnrichmentService:
    global _enrichment_instance
    if _enrichment_instance is None:
        _enrichment_instance = ComplaintEnrichmentService()
    return _enrichment_instance


"""
Complaint Prioritization Service
Multi-Factor Priority Scoring Engine combining:
1. Star Rating (Inverted penalty)
2. Severity Score (1-5 operational severity)
3. Sentiment (Negative/Neutral/Positive)
4. Useful Votes (Social validation)
5. Recurrence Frequency (Category complaint volume at the restaurant)

Outputs:
- High Priority (>= 70.0)
- Medium Priority (40.0 - 69.9)
- Low Priority (< 40.0)
"""
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import func
from backend.app.database.db import SessionLocal
from backend.app.models.review import EnrichedReviewORM

class ComplaintPrioritizationService:
    TIER_HIGH = "High"
    TIER_MEDIUM = "Medium"
    TIER_LOW = "Low"

    @classmethod
    def calculate_priority(
        cls,
        stars: float,
        severity_score: int,
        sentiment: str,
        useful_votes: int = 0,
        frequency_count: int = 1,
        is_complaint: bool = True
    ) -> Tuple[float, str, Dict[str, float]]:
        """
        Calculate multi-factor priority score (1.0 to 100.0) and assign priority tier.
        Returns: (final_score, tier, factor_breakdown)
        """
        if not is_complaint and stars >= 4.0 and sentiment == "Positive":
            return (10.0, cls.TIER_LOW, {
                "star_factor": 0.0,
                "severity_factor": 5.0,
                "sentiment_factor": 0.0,
                "useful_factor": 0.0,
                "frequency_factor": 5.0
            })

        # Factor 1: Star Rating (up to 30 pts)
        star_factor = round(max(0.0, (5.0 - stars) / 4.0) * 30.0, 2)

        # Factor 2: Severity (1-5 scaled to 30 pts)
        severity_factor = round(min(5, max(1, severity_score)) / 5.0 * 30.0, 2)

        # Factor 3: Sentiment (up to 15 pts)
        sentiment_upper = str(sentiment).capitalize()
        if sentiment_upper == "Negative":
            sentiment_factor = 15.0
        elif sentiment_upper == "Neutral":
            sentiment_factor = 5.0
        else:
            sentiment_factor = 0.0

        # Factor 4: Useful Votes (up to 15 pts)
        useful_factor = round(min(float(max(0, useful_votes)) * 2.5, 15.0), 2)

        # Factor 5: Recurrence Frequency (up to 10 pts)
        frequency_factor = round(min(float(max(1, frequency_count)) * 2.0, 10.0), 2)

        raw_score = star_factor + severity_factor + sentiment_factor + useful_factor + frequency_factor
        final_score = round(min(100.0, max(1.0, raw_score)), 2)

        # Priority Tier Assignment
        if final_score >= 70.0:
            tier = cls.TIER_HIGH
        elif final_score >= 40.0:
            tier = cls.TIER_MEDIUM
        else:
            tier = cls.TIER_LOW

        breakdown = {
            "star_factor": star_factor,
            "severity_factor": severity_factor,
            "sentiment_factor": sentiment_factor,
            "useful_factor": useful_factor,
            "frequency_factor": frequency_factor
        }

        return (final_score, tier, breakdown)

    def get_restaurant_priority_rankings(
        self,
        business_id: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Query and compute priority rankings for complaints with recurrence frequency."""
        db = SessionLocal()

        # Compute category recurrence frequencies per business
        freq_subquery = db.query(
            EnrichedReviewORM.business_id,
            EnrichedReviewORM.complaint_category,
            func.count(EnrichedReviewORM.review_id).label("cat_freq")
        ).filter(
            EnrichedReviewORM.is_complaint == True
        ).group_by(
            EnrichedReviewORM.business_id,
            EnrichedReviewORM.complaint_category
        ).subquery()

        # Main query
        query = db.query(
            EnrichedReviewORM,
            func.coalesce(freq_subquery.c.cat_freq, 1).label("frequency")
        ).outerjoin(
            freq_subquery,
            (EnrichedReviewORM.business_id == freq_subquery.c.business_id) &
            (EnrichedReviewORM.complaint_category == freq_subquery.c.complaint_category)
        ).filter(
            EnrichedReviewORM.is_complaint == True
        )

        if business_id:
            query = query.filter(EnrichedReviewORM.business_id == business_id)
        if category:
            query = query.filter(EnrichedReviewORM.complaint_category == category)

        records = query.order_by(EnrichedReviewORM.priority_score.desc()).limit(limit).all()

        results = []
        for review, freq in records:
            score, tier, factors = self.calculate_priority(
                stars=review.stars,
                severity_score=review.severity_score,
                sentiment=review.sentiment,
                useful_votes=review.useful,
                frequency_count=freq,
                is_complaint=review.is_complaint
            )

            results.append({
                "review_id": review.review_id,
                "business_id": review.business_id,
                "restaurant_name": review.restaurant_name,
                "category": review.complaint_category,
                "aspect": review.aspect,
                "stars": review.stars,
                "severity_score": review.severity_score,
                "priority_score": score,
                "priority_tier": tier,
                "factor_breakdown": factors,
                "recurrence_count": freq,
                "date": review.date,
                "text": review.text
            })

        db.close()
        
        # Sort strictly by computed multi-factor priority score descending
        return sorted(results, key=lambda x: x["priority_score"], reverse=True)

    def get_prioritized_complaints(
        self,
        business_id: Optional[str] = None,
        category: Optional[str] = None,
        priority_tier: Optional[str] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Convenience method returning summary metrics and tier-filtered list."""
        all_ranks = self.get_restaurant_priority_rankings(
            business_id=business_id,
            category=category,
            limit=limit * 3
        )

        tier_counts = {"High": 0, "Medium": 0, "Low": 0}
        for r in all_ranks:
            t = r.get("priority_tier", "Low")
            if t in tier_counts:
                tier_counts[t] += 1

        if priority_tier and priority_tier != "All":
            filtered = [r for r in all_ranks if r.get("priority_tier", "").lower() == priority_tier.lower()]
        else:
            filtered = all_ranks

        return {
            "total_found": len(filtered[:limit]),
            "summary_by_tier": tier_counts,
            "reviews": filtered[:limit]
        }

# Global singleton
_prioritization_instance: Optional[ComplaintPrioritizationService] = None

def get_prioritization_service() -> ComplaintPrioritizationService:
    global _prioritization_instance
    if _prioritization_instance is None:
        _prioritization_instance = ComplaintPrioritizationService()
    return _prioritization_instance

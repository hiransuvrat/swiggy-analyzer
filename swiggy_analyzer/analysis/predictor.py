"""Main prediction engine for recommendations."""

from typing import List, Optional

from loguru import logger

from ..data.models import ItemRecommendation
from .pattern_detector import PatternDetector
from .scoring import ItemScorer


class ItemPredictor:
    """Main prediction engine that combines pattern detection and scoring."""

    def __init__(self, detector: PatternDetector, scorer: ItemScorer):
        self.detector = detector
        self.scorer = scorer

    def get_recommendations(self, min_score: float = 50.0,
                           max_items: int = 20) -> List[ItemRecommendation]:
        """
        Get item recommendations based on buying patterns.

        Args:
            min_score: Minimum score threshold (0-100)
            max_items: Maximum number of recommendations

        Returns:
            List of ItemRecommendation objects, sorted by score (descending)
        """
        logger.info(f"Generating recommendations (min_score={min_score}, max_items={max_items})")

        # Get all patterns
        patterns = self.detector.get_patterns()

        if not patterns:
            logger.warning("No buying patterns found, need more order history")
            return []

        logger.debug(f"Found {len(patterns)} item patterns")

        # Score each pattern
        recommendations = []
        for pattern in patterns:
            recommendation = self.scorer.score_item(pattern)

            if recommendation and recommendation.score >= min_score:
                recommendations.append(recommendation)

        # Sort by score (descending)
        recommendations.sort(key=lambda x: x.score, reverse=True)

        # Limit results
        recommendations = recommendations[:max_items]

        logger.info(f"Generated {len(recommendations)} recommendations")
        return recommendations

    def get_recommendation_for_item(self, item_id: str) -> Optional[ItemRecommendation]:
        """Get recommendation for a specific item."""
        pattern = self.detector.get_pattern_for_item(item_id)
        if not pattern:
            return None

        return self.scorer.score_item(pattern)

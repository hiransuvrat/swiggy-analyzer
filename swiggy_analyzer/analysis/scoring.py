"""Recommendation scoring algorithm."""

import math
from datetime import datetime
from typing import Optional

from loguru import logger

from ..data.models import ItemPattern, ItemRecommendation


class ItemScorer:
    """Scores items for recommendation based on buying patterns."""

    def __init__(self, frequency_weight: float = 0.4, recency_weight: float = 0.4,
                 quantity_weight: float = 0.2):
        self.frequency_weight = frequency_weight
        self.recency_weight = recency_weight
        self.quantity_weight = quantity_weight

        # Ensure weights sum to 1.0
        total = frequency_weight + recency_weight + quantity_weight
        if abs(total - 1.0) > 0.01:
            logger.warning(f"Weights sum to {total}, normalizing to 1.0")
            self.frequency_weight /= total
            self.recency_weight /= total
            self.quantity_weight /= total

    def score_item(self, pattern: ItemPattern) -> Optional[ItemRecommendation]:
        """
        Score an item based on its buying pattern.

        Args:
            pattern: ItemPattern object

        Returns:
            ItemRecommendation with score and reasoning, or None if not enough data
        """
        # Need at least 2 purchases to establish a pattern
        if pattern.total_purchases < 2:
            return None

        # Calculate component scores
        frequency_score = self._calculate_frequency_score(pattern)
        recency_score = self._calculate_recency_score(pattern)
        quantity_score = self._calculate_quantity_score(pattern)

        # Weighted total
        total_score = (
            frequency_score * self.frequency_weight +
            recency_score * self.recency_weight +
            quantity_score * self.quantity_weight
        )

        # Generate reasoning
        reasoning = self._generate_reasoning(pattern, frequency_score, recency_score, quantity_score)

        # Suggest quantity (rounded average)
        suggested_quantity = max(1, round(pattern.avg_quantity))

        recommendation = ItemRecommendation(
            item_id=pattern.item_id,
            item_name=pattern.item_name,
            score=total_score,
            frequency_score=frequency_score,
            recency_score=recency_score,
            quantity_score=quantity_score,
            suggested_quantity=suggested_quantity,
            reasoning=reasoning,
            pattern=pattern,
        )

        return recommendation

    def _calculate_frequency_score(self, pattern: ItemPattern) -> float:
        """
        Calculate frequency score (0-100).

        Uses logarithmic scale based on total purchases.
        """
        # Logarithmic scale: log10(purchases + 1) * 50
        # 2 purchases = 23.8, 10 purchases = 52.3, 100 purchases = 100.5
        score = math.log10(pattern.total_purchases + 1) * 50

        # Cap at 100
        return min(100.0, score)

    def _calculate_recency_score(self, pattern: ItemPattern) -> float:
        """
        Calculate recency score (0-100).

        Based on how overdue the item is compared to expected interval.
        """
        if not pattern.last_purchase_date or pattern.avg_days_between_purchases <= 0:
            return 50.0  # Neutral score if no pattern

        # Days since last purchase
        days_since = (datetime.now() - pattern.last_purchase_date).days

        # Expected interval
        expected_interval = pattern.avg_days_between_purchases

        # Ratio of actual vs expected
        ratio = days_since / expected_interval

        if ratio < 0.5:
            # Too recent, probably don't need yet
            return 20.0

        elif ratio < 0.9:
            # Getting close but not quite time yet
            return 50.0 + (ratio - 0.5) * 100  # 50-90

        elif ratio < 1.2:
            # Sweet spot - right time to reorder
            return 90.0 + (ratio - 0.9) * 33.3  # 90-100

        else:
            # Overdue - decays exponentially
            overdue_factor = ratio - 1.2
            decay = math.exp(-overdue_factor * 0.5)  # Exponential decay
            return 100.0 * decay

    def _calculate_quantity_score(self, pattern: ItemPattern) -> float:
        """
        Calculate quantity consistency score (0-100).

        Based on coefficient of variation (std_dev / mean).
        Lower variation = higher score.
        """
        if pattern.avg_quantity <= 0:
            return 50.0

        # Coefficient of variation
        cv = pattern.std_dev_quantity / pattern.avg_quantity if pattern.avg_quantity > 0 else 0

        # Convert to score (lower CV = higher score)
        # CV of 0 = 100, CV of 1 = 50, CV > 2 = 0
        if cv <= 0:
            return 100.0
        elif cv >= 2:
            return 0.0
        else:
            return 100.0 - (cv * 50)

    def _generate_reasoning(self, pattern: ItemPattern, freq_score: float,
                           rec_score: float, qty_score: float) -> str:
        """Generate human-readable reasoning for the recommendation."""
        reasons = []

        # Frequency reasoning
        if pattern.total_purchases >= 10:
            reasons.append(f"frequently purchased ({pattern.total_purchases}x)")
        elif pattern.total_purchases >= 5:
            reasons.append(f"regularly purchased ({pattern.total_purchases}x)")
        else:
            reasons.append(f"purchased {pattern.total_purchases}x")

        # Recency reasoning
        if pattern.last_purchase_date and pattern.avg_days_between_purchases > 0:
            days_since = (datetime.now() - pattern.last_purchase_date).days
            expected = pattern.avg_days_between_purchases
            ratio = days_since / expected

            if ratio > 1.2:
                overdue_days = days_since - expected
                reasons.append(f"overdue by {int(overdue_days)} days")
            elif ratio > 0.9:
                reasons.append("due for reorder")
            elif ratio > 0.7:
                reasons.append("will need soon")

        # Quantity consistency
        if pattern.std_dev_quantity / pattern.avg_quantity < 0.3:
            reasons.append(f"consistent quantity (~{round(pattern.avg_quantity)})")

        return ", ".join(reasons)

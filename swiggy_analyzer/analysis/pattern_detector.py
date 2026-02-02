"""Buying pattern detection and analysis."""

from datetime import datetime
from typing import List, Dict, Any
from collections import defaultdict

from loguru import logger

from ..data.models import ItemPattern


class PatternDetector:
    """Detects buying patterns from order history."""

    def __init__(self, repository):
        self.repository = repository

    def calculate_patterns(self) -> List[ItemPattern]:
        """
        Calculate buying patterns for all items.

        Returns:
            List of ItemPattern objects
        """
        logger.info("Calculating buying patterns")
        patterns = self.repository.calculate_item_patterns()
        logger.info(f"Calculated patterns for {len(patterns)} items")
        return patterns

    def get_patterns(self) -> List[ItemPattern]:
        """Get cached patterns from database."""
        return self.repository.get_all_patterns()

    def get_pattern_for_item(self, item_id: str) -> ItemPattern:
        """Get pattern for a specific item."""
        patterns = self.get_patterns()
        for pattern in patterns:
            if pattern.item_id == item_id:
                return pattern
        return None

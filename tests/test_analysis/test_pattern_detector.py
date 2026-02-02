"""Tests for pattern detection."""

import pytest
from datetime import datetime, timedelta

from swiggy_analyzer.analysis.pattern_detector import PatternDetector


def test_calculate_patterns(temp_db, mock_orders):
    """Test pattern calculation."""
    # Save mock orders
    temp_db.save_orders(mock_orders)

    # Calculate patterns
    detector = PatternDetector(temp_db)
    patterns = detector.calculate_patterns()

    assert len(patterns) == 3  # milk, bread, eggs

    # Check milk pattern
    milk_pattern = next(p for p in patterns if p.item_id == "milk_1l")
    assert milk_pattern.total_purchases == 12
    assert milk_pattern.avg_quantity == 2.0
    assert 6 < milk_pattern.avg_days_between_purchases < 8  # ~7 days

    # Check bread pattern
    bread_pattern = next(p for p in patterns if p.item_id == "bread_ww")
    assert bread_pattern.total_purchases == 25
    assert bread_pattern.avg_quantity == 1.0
    assert 3 < bread_pattern.avg_days_between_purchases < 4  # ~3.5 days


def test_get_patterns(temp_db, mock_orders):
    """Test retrieving calculated patterns."""
    temp_db.save_orders(mock_orders)

    detector = PatternDetector(temp_db)
    detector.calculate_patterns()

    patterns = detector.get_patterns()
    assert len(patterns) == 3


def test_get_pattern_for_item(temp_db, mock_orders):
    """Test getting pattern for specific item."""
    temp_db.save_orders(mock_orders)

    detector = PatternDetector(temp_db)
    detector.calculate_patterns()

    pattern = detector.get_pattern_for_item("milk_1l")
    assert pattern is not None
    assert pattern.item_name == "Amul Milk 1L"

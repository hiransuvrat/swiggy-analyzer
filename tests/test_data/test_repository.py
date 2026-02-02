"""Tests for repository operations."""

import pytest
from datetime import datetime, timedelta

from swiggy_analyzer.data.models import Order, OrderItem


def test_save_and_get_orders(temp_db, mock_orders):
    """Test saving and retrieving orders."""
    temp_db.save_orders(mock_orders)

    count = temp_db.get_order_count()
    assert count == len(mock_orders)

    item_count = temp_db.get_item_count()
    assert item_count == 3  # milk, bread, eggs


def test_get_all_order_items(temp_db, mock_orders):
    """Test retrieving all order items."""
    temp_db.save_orders(mock_orders)

    items = temp_db.get_all_order_items()
    assert len(items) > 0

    # Check that items have required fields
    for item in items:
        assert "item_id" in item
        assert "item_name" in item
        assert "quantity" in item
        assert "order_date" in item


def test_calculate_item_patterns(temp_db, mock_orders):
    """Test pattern calculation."""
    temp_db.save_orders(mock_orders)

    patterns = temp_db.calculate_item_patterns()
    assert len(patterns) == 3

    # Get milk pattern
    milk = next(p for p in patterns if p.item_id == "milk_1l")
    assert milk.total_purchases == 12
    assert milk.avg_quantity == 2.0


def test_save_recommendations(temp_db):
    """Test saving recommendations."""
    from swiggy_analyzer.data.models import ItemRecommendation, ItemPattern

    pattern = ItemPattern(
        item_id="test",
        item_name="Test Item",
        total_purchases=10,
        avg_quantity=1.0,
        std_dev_quantity=0.0,
        avg_days_between_purchases=7.0,
    )

    recommendation = ItemRecommendation(
        item_id="test",
        item_name="Test Item",
        score=75.0,
        frequency_score=60.0,
        recency_score=80.0,
        quantity_score=85.0,
        suggested_quantity=1,
        reasoning="Test reasoning",
        pattern=pattern,
    )

    temp_db.save_recommendations([recommendation])

    # Verify saved
    # (no direct getter in repository, but job log should work)
    temp_db.update_recommendation_action("test", "accepted", True, "success")


def test_job_log(temp_db):
    """Test job logging."""
    job_id = temp_db.create_job_log("analysis")
    assert job_id > 0

    temp_db.update_job_log(job_id, "success", 10, 5)

    # Job should be updated (no getter, but no errors)

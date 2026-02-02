"""Tests for scoring algorithm."""

import pytest
from datetime import datetime, timedelta

from swiggy_analyzer.analysis.scoring import ItemScorer
from swiggy_analyzer.data.models import ItemPattern


def test_frequency_score():
    """Test frequency scoring."""
    scorer = ItemScorer()

    # 2 purchases
    pattern = ItemPattern(
        item_id="test",
        item_name="Test Item",
        total_purchases=2,
        avg_quantity=1.0,
        std_dev_quantity=0.0,
        avg_days_between_purchases=7.0,
    )
    score = scorer._calculate_frequency_score(pattern)
    assert 20 < score < 30  # Should be around 23.8

    # 10 purchases
    pattern.total_purchases = 10
    score = scorer._calculate_frequency_score(pattern)
    assert 50 < score < 55  # Should be around 52.3

    # 100 purchases
    pattern.total_purchases = 100
    score = scorer._calculate_frequency_score(pattern)
    assert score == 100.0  # Capped at 100


def test_recency_score():
    """Test recency scoring."""
    scorer = ItemScorer()

    base_pattern = ItemPattern(
        item_id="test",
        item_name="Test Item",
        total_purchases=10,
        avg_quantity=1.0,
        std_dev_quantity=0.0,
        avg_days_between_purchases=7.0,
        last_purchase_date=datetime.now(),
    )

    # Too recent (purchased yesterday, expect every 7 days)
    pattern = base_pattern.model_copy()
    pattern.last_purchase_date = datetime.now() - timedelta(days=1)
    score = scorer._calculate_recency_score(pattern)
    assert score < 50  # Should be low

    # Right on time (purchased 7 days ago)
    pattern = base_pattern.model_copy()
    pattern.last_purchase_date = datetime.now() - timedelta(days=7)
    score = scorer._calculate_recency_score(pattern)
    assert score >= 90  # Should be high

    # Slightly overdue (purchased 8 days ago)
    pattern = base_pattern.model_copy()
    pattern.last_purchase_date = datetime.now() - timedelta(days=8)
    score = scorer._calculate_recency_score(pattern)
    assert score >= 85  # Still high

    # Very overdue (purchased 20 days ago, expect every 7)
    pattern = base_pattern.model_copy()
    pattern.last_purchase_date = datetime.now() - timedelta(days=20)
    score = scorer._calculate_recency_score(pattern)
    assert score < 70  # Should decay


def test_quantity_score():
    """Test quantity consistency scoring."""
    scorer = ItemScorer()

    # Perfect consistency
    pattern = ItemPattern(
        item_id="test",
        item_name="Test Item",
        total_purchases=10,
        avg_quantity=2.0,
        std_dev_quantity=0.0,
        avg_days_between_purchases=7.0,
    )
    score = scorer._calculate_quantity_score(pattern)
    assert score == 100.0

    # Some variation (CV = 0.5)
    pattern.std_dev_quantity = 1.0  # avg=2, std=1, CV=0.5
    score = scorer._calculate_quantity_score(pattern)
    assert 70 < score < 80

    # High variation (CV = 2)
    pattern.std_dev_quantity = 4.0  # avg=2, std=4, CV=2
    score = scorer._calculate_quantity_score(pattern)
    assert score <= 10


def test_score_item():
    """Test overall item scoring."""
    scorer = ItemScorer()

    pattern = ItemPattern(
        item_id="milk",
        item_name="Milk 1L",
        total_purchases=10,
        first_purchase_date=datetime.now() - timedelta(days=70),
        last_purchase_date=datetime.now() - timedelta(days=7),
        avg_quantity=2.0,
        std_dev_quantity=0.2,
        avg_days_between_purchases=7.0,
        std_dev_days_between=1.0,
    )

    recommendation = scorer.score_item(pattern)

    assert recommendation is not None
    assert 0 <= recommendation.score <= 100
    assert recommendation.suggested_quantity == 2
    assert len(recommendation.reasoning) > 0


def test_score_item_insufficient_data():
    """Test that items with insufficient data are not scored."""
    scorer = ItemScorer()

    # Only 1 purchase
    pattern = ItemPattern(
        item_id="test",
        item_name="Test Item",
        total_purchases=1,
        avg_quantity=1.0,
        std_dev_quantity=0.0,
        avg_days_between_purchases=0.0,
    )

    recommendation = scorer.score_item(pattern)
    assert recommendation is None  # Should not recommend with < 2 purchases

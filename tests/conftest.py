"""Pytest fixtures and configuration."""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil

from swiggy_analyzer.data.repository import SwiggyRepository
from swiggy_analyzer.data.models import Order, OrderItem


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test.db"

    repo = SwiggyRepository(str(db_path))

    yield repo

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_orders():
    """Create mock order data for testing."""
    orders = []

    # Create orders over 3 months
    base_date = datetime.now() - timedelta(days=90)

    # Milk - purchased every 7 days
    for i in range(12):
        order = Order(
            id=f"order_milk_{i}",
            order_date=base_date + timedelta(days=i * 7),
            total_amount=116.0,
            items=[
                OrderItem(
                    item_id="milk_1l",
                    item_name="Amul Milk 1L",
                    quantity=2,
                    price=58.0,
                )
            ],
        )
        orders.append(order)

    # Bread - purchased every 3-4 days
    for i in range(25):
        order = Order(
            id=f"order_bread_{i}",
            order_date=base_date + timedelta(days=i * 3.5),
            total_amount=45.0,
            items=[
                OrderItem(
                    item_id="bread_ww",
                    item_name="Bread Whole Wheat",
                    quantity=1,
                    price=45.0,
                )
            ],
        )
        orders.append(order)

    # Eggs - purchased inconsistently
    for i in range(5):
        order = Order(
            id=f"order_eggs_{i}",
            order_date=base_date + timedelta(days=i * 18),
            total_amount=36.0,
            items=[
                OrderItem(
                    item_id="eggs_6",
                    item_name="Eggs 6 Pack",
                    quantity=1,
                    price=36.0,
                )
            ],
        )
        orders.append(order)

    return orders


class MockMCPClient:
    """Mock MCP client for testing."""

    def __init__(self):
        self.calls = []

    def call_tool(self, tool_name, arguments=None):
        """Mock tool call."""
        self.calls.append((tool_name, arguments))

        if tool_name == "get_order_history":
            return {"orders": []}

        elif tool_name == "get_basket":
            return {"items": [], "total": 0}

        elif tool_name == "add_to_basket":
            return {"success": True}

        elif tool_name == "get_item_details":
            return {
                "item": {
                    "available": True,
                    "price": 50.0,
                }
            }

        return {}

    def close(self):
        """Mock close."""
        pass

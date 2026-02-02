#!/usr/bin/env python3
"""Create test data for Swiggy Analyzer."""

from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from swiggy_analyzer.data.repository import SwiggyRepository
from swiggy_analyzer.data.models import Order, OrderItem
from swiggy_analyzer.config.settings import Settings

def create_test_data():
    """Create sample orders for testing."""
    settings = Settings()
    repo = SwiggyRepository(settings.get_db_path())

    print("Creating test data...")

    orders = []
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
                    category="Dairy",
                    brand="Amul",
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
                    category="Bakery",
                    brand="Modern",
                )
            ],
        )
        orders.append(order)

    # Eggs - purchased every 2 weeks
    for i in range(6):
        order = Order(
            id=f"order_eggs_{i}",
            order_date=base_date + timedelta(days=i * 14),
            total_amount=72.0,
            items=[
                OrderItem(
                    item_id="eggs_12",
                    item_name="Farm Fresh Eggs (12 pack)",
                    quantity=1,
                    price=72.0,
                    category="Dairy",
                    brand="Farm Fresh",
                )
            ],
        )
        orders.append(order)

    # Bananas - purchased weekly
    for i in range(12):
        order = Order(
            id=f"order_bananas_{i}",
            order_date=base_date + timedelta(days=i * 7 + 2),
            total_amount=60.0,
            items=[
                OrderItem(
                    item_id="bananas_1kg",
                    item_name="Bananas (1 kg)",
                    quantity=2,
                    price=30.0,
                    category="Fruits",
                    brand="Fresh",
                )
            ],
        )
        orders.append(order)

    # Tomatoes - purchased every 5 days
    for i in range(18):
        order = Order(
            id=f"order_tomatoes_{i}",
            order_date=base_date + timedelta(days=i * 5),
            total_amount=40.0,
            items=[
                OrderItem(
                    item_id="tomatoes_500g",
                    item_name="Tomatoes (500g)",
                    quantity=1,
                    price=40.0,
                    category="Vegetables",
                    brand="Fresh",
                )
            ],
        )
        orders.append(order)

    # Yogurt - purchased every 4 days
    for i in range(20):
        order = Order(
            id=f"order_yogurt_{i}",
            order_date=base_date + timedelta(days=i * 4),
            total_amount=50.0,
            items=[
                OrderItem(
                    item_id="yogurt_400g",
                    item_name="Amul Fresh Yogurt 400g",
                    quantity=1,
                    price=50.0,
                    category="Dairy",
                    brand="Amul",
                )
            ],
        )
        orders.append(order)

    # Mixed order
    order = Order(
        id="order_mixed_1",
        order_date=datetime.now() - timedelta(days=2),
        total_amount=350.0,
        items=[
            OrderItem(
                item_id="milk_1l",
                item_name="Amul Milk 1L",
                quantity=2,
                price=58.0,
                category="Dairy",
                brand="Amul",
            ),
            OrderItem(
                item_id="bread_ww",
                item_name="Bread Whole Wheat",
                quantity=1,
                price=45.0,
                category="Bakery",
                brand="Modern",
            ),
            OrderItem(
                item_id="butter_100g",
                item_name="Amul Butter 100g",
                quantity=1,
                price=55.0,
                category="Dairy",
                brand="Amul",
            ),
            OrderItem(
                item_id="tea_250g",
                item_name="Tata Tea Gold 250g",
                quantity=1,
                price=142.0,
                category="Beverages",
                brand="Tata",
            ),
            OrderItem(
                item_id="yogurt_400g",
                item_name="Amul Fresh Yogurt 400g",
                quantity=1,
                price=50.0,
                category="Dairy",
                brand="Amul",
            ),
        ],
    )
    orders.append(order)

    # Save all orders
    print(f"Saving {len(orders)} orders...")
    repo.save_orders(orders)

    # Calculate patterns
    print("Calculating patterns...")
    patterns = repo.calculate_item_patterns()

    print(f"\n✓ Created {len(orders)} orders")
    print(f"✓ Calculated patterns for {len(patterns)} items")
    print(f"\nTop items by purchase frequency:")

    sorted_patterns = sorted(patterns, key=lambda p: p.total_purchases, reverse=True)
    for p in sorted_patterns[:10]:
        print(f"  - {p.item_name}: {p.total_purchases} purchases, "
              f"avg every {p.avg_days_between_purchases:.1f} days")

    print("\n✓ Test data created successfully!")
    print("\nYou can now run the web UI with:")
    print("  ./run_web.sh")
    print("\nOr the CLI:")
    print("  .venv/bin/swiggy-analyzer analyze run --dry-run")

if __name__ == "__main__":
    create_test_data()

"""Swiggy Instamart MCP API endpoint wrappers."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from loguru import logger

from .client import MCPClient
from ..data.models import Order, OrderItem


class SwiggyInstamartMCP:
    """Wrapper for Swiggy Instamart MCP API endpoints."""

    def __init__(self, client: MCPClient):
        self.client = client

    def get_order_history(self, limit: int = 50, offset: int = 0,
                         days_back: Optional[int] = None) -> List[Order]:
        """
        Fetch order history.

        Args:
            limit: Maximum number of orders to fetch
            offset: Pagination offset
            days_back: Only fetch orders from last N days

        Returns:
            List of Order objects
        """
        arguments = {
            "limit": limit,
            "offset": offset,
        }

        if days_back:
            since_date = datetime.now() - timedelta(days=days_back)
            arguments["since"] = since_date.isoformat()

        try:
            logger.info(f"Fetching order history (limit={limit}, offset={offset})")
            response = self.client.call_tool("get_order_history", arguments)

            orders = []
            for order_data in response.get("orders", []):
                # Parse order items
                items = []
                for item_data in order_data.get("items", []):
                    item = OrderItem(
                        item_id=item_data.get("id", item_data.get("item_id", "")),
                        item_name=item_data.get("name", ""),
                        quantity=item_data.get("quantity", 1),
                        price=item_data.get("price"),
                        category=item_data.get("category"),
                        brand=item_data.get("brand"),
                    )
                    items.append(item)

                # Parse order
                order = Order(
                    id=order_data.get("id", ""),
                    order_date=datetime.fromisoformat(order_data.get("order_date", "")),
                    total_amount=order_data.get("total_amount"),
                    items=items,
                    raw_data=order_data,
                )
                orders.append(order)

            logger.info(f"Fetched {len(orders)} orders")
            return orders

        except Exception as e:
            logger.error(f"Failed to fetch order history: {e}")
            raise

    def get_basket(self) -> Dict[str, Any]:
        """Get current basket contents."""
        try:
            logger.info("Fetching current basket")
            response = self.client.call_tool("get_cart")

            # Parse MCP response format
            # Response is: {"content": [{"type": "text", "text": "{json...}"}]}
            import json
            if "content" in response and len(response["content"]) > 0:
                text_content = response["content"][0]["text"]
                cart_data = json.loads(text_content)

                if cart_data.get("success"):
                    data = cart_data.get("data", {})
                    items_list = []

                    # Parse items
                    for item in data.get("items", []):
                        items_list.append({
                            "id": item.get("spinId", ""),
                            "name": item.get("itemName", ""),
                            "quantity": item.get("quantity", 0),
                            "price": item.get("discountedFinalPrice", item.get("mrp", 0)),
                            "mrp": item.get("mrp", 0),
                        })

                    # Extract total from cartTotalAmount (format: "₹119")
                    cart_total_str = data.get("cartTotalAmount", "₹0")
                    cart_total = float(cart_total_str.replace("₹", "").replace(",", ""))

                    return {
                        "items": items_list,
                        "total": cart_total,
                        "address": data.get("selectedAddressDetails", {}).get("address", ""),
                    }
                else:
                    logger.warning(f"Cart fetch failed: {cart_data.get('message')}")
                    return {"items": [], "total": 0}

            return response

        except Exception as e:
            logger.error(f"Failed to fetch basket: {e}")
            raise

    def add_to_basket(self, item_id: str, quantity: int = 1) -> Dict[str, Any]:
        """
        Add item to basket.

        Args:
            item_id: Item identifier
            quantity: Quantity to add

        Returns:
            Response with basket update status
        """
        arguments = {
            "item_id": item_id,
            "quantity": quantity,
        }

        try:
            logger.info(f"Adding {quantity}x {item_id} to basket")
            response = self.client.call_tool("add_to_basket", arguments)
            return response

        except Exception as e:
            logger.error(f"Failed to add item to basket: {e}")
            raise

    def search_items(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for items by name.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of item results
        """
        arguments = {
            "query": query,
            "limit": limit,
        }

        try:
            logger.info(f"Searching for items: {query}")
            response = self.client.call_tool("search_items", arguments)
            return response.get("items", [])

        except Exception as e:
            logger.error(f"Failed to search items: {e}")
            raise

    def get_item_details(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Get item details including availability and current price.

        Args:
            item_id: Item identifier

        Returns:
            Item details or None if not found
        """
        arguments = {
            "item_id": item_id,
        }

        try:
            logger.debug(f"Fetching details for item: {item_id}")
            response = self.client.call_tool("get_item_details", arguments)
            return response.get("item")

        except Exception as e:
            logger.warning(f"Failed to get item details for {item_id}: {e}")
            return None

    def clear_basket(self) -> Dict[str, Any]:
        """Clear all items from basket."""
        try:
            logger.info("Clearing basket")
            response = self.client.call_tool("clear_basket")
            return response

        except Exception as e:
            logger.error(f"Failed to clear basket: {e}")
            raise

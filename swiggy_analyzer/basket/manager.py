"""Basket operations manager."""

from typing import List, Dict, Any

from loguru import logger

from ..data.models import ItemRecommendation
from ..mcp.endpoints import SwiggyInstamartMCP


class BasketManager:
    """Manages basket preview and add operations."""

    def __init__(self, swiggy_mcp: SwiggyInstamartMCP, repository):
        self.swiggy_mcp = swiggy_mcp
        self.repository = repository

    def preview_recommendations(self, recommendations: List[ItemRecommendation]) -> List[ItemRecommendation]:
        """
        Validate recommendations by checking availability and prices.

        Args:
            recommendations: List of recommendations to validate

        Returns:
            Updated recommendations with availability and price info
        """
        logger.info(f"Validating {len(recommendations)} recommendations")

        validated = []
        for rec in recommendations:
            try:
                # Get item details from MCP
                item_details = self.swiggy_mcp.get_item_details(rec.item_id)

                if item_details:
                    rec.available = item_details.get("available", True)
                    rec.current_price = item_details.get("price")
                else:
                    # If we can't get details, assume unavailable
                    rec.available = False

                validated.append(rec)

            except Exception as e:
                logger.warning(f"Failed to validate {rec.item_name}: {e}")
                rec.available = False
                validated.append(rec)

        available_count = sum(1 for r in validated if r.available)
        logger.info(f"Validated: {available_count}/{len(validated)} items available")

        return validated

    def add_items_to_basket(self, recommendations: List[ItemRecommendation]) -> Dict[str, Any]:
        """
        Add recommended items to basket.

        Args:
            recommendations: List of recommendations to add

        Returns:
            Dictionary with success/failure information
        """
        logger.info(f"Adding {len(recommendations)} items to basket")

        results = {
            "success": [],
            "failed": [],
            "total_price": 0.0,
        }

        for rec in recommendations:
            try:
                # Skip unavailable items
                if not rec.available:
                    results["failed"].append({
                        "name": rec.item_name,
                        "reason": "Item not available",
                    })
                    # Update recommendation log
                    self.repository.update_recommendation_action(
                        rec.item_id, "rejected", False, "unavailable"
                    )
                    continue

                # Add to basket
                response = self.swiggy_mcp.add_to_basket(rec.item_id, rec.suggested_quantity)

                if response.get("success"):
                    results["success"].append({
                        "name": rec.item_name,
                        "quantity": rec.suggested_quantity,
                        "price": rec.current_price,
                    })

                    if rec.current_price:
                        results["total_price"] += rec.current_price * rec.suggested_quantity

                    # Update recommendation log
                    self.repository.update_recommendation_action(
                        rec.item_id, "accepted", True, "success"
                    )

                    logger.info(f"Added {rec.item_name} to basket")

                else:
                    reason = response.get("error", "Unknown error")
                    results["failed"].append({
                        "name": rec.item_name,
                        "reason": reason,
                    })

                    # Update recommendation log
                    self.repository.update_recommendation_action(
                        rec.item_id, "rejected", False, reason
                    )

            except Exception as e:
                logger.error(f"Failed to add {rec.item_name}: {e}")
                results["failed"].append({
                    "name": rec.item_name,
                    "reason": str(e),
                })

                # Update recommendation log
                self.repository.update_recommendation_action(
                    rec.item_id, "rejected", False, str(e)
                )

        logger.info(f"Basket update complete: {len(results['success'])} added, {len(results['failed'])} failed")
        return results

    def get_basket(self) -> Dict[str, Any]:
        """Get current basket contents."""
        try:
            return self.swiggy_mcp.get_basket()
        except Exception as e:
            logger.error(f"Failed to get basket: {e}")
            raise

    def clear_basket(self) -> bool:
        """Clear all items from basket."""
        try:
            self.swiggy_mcp.clear_basket()
            logger.info("Basket cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear basket: {e}")
            return False

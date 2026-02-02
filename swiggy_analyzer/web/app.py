"""Flask web application for Swiggy Analyzer."""

from flask import Flask, render_template, jsonify, request
from pathlib import Path
import sys
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from swiggy_analyzer.config.settings import Settings
from swiggy_analyzer.data.repository import SwiggyRepository
from swiggy_analyzer.auth.token_store import TokenStore
from swiggy_analyzer.auth.oauth_manager import OAuthManager
from swiggy_analyzer.mcp.client import MCPClient
from swiggy_analyzer.mcp.endpoints import SwiggyInstamartMCP
from swiggy_analyzer.analysis.pattern_detector import PatternDetector
from swiggy_analyzer.analysis.scoring import ItemScorer
from swiggy_analyzer.analysis.predictor import ItemPredictor
from swiggy_analyzer.basket.manager import BasketManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'swiggy-analyzer-secret-key'

# Set up logging
logger = logging.getLogger(__name__)

# Initialize services
settings = Settings()
repository = SwiggyRepository(settings.get_db_path())
token_store = TokenStore(repository)
auth_manager = OAuthManager(token_store)

# Mock basket for test mode (in-memory storage)
mock_basket = {
    'items': [],
    'total': 0.0
}


def get_services():
    """Get initialized services."""
    mcp_client = MCPClient(
        base_url=settings.get_mcp_base_url(),
        auth_manager=auth_manager,
        timeout=settings.get("mcp.timeout"),
        max_retries=settings.get("mcp.retry_attempts"),
        rate_limit=settings.get("mcp.rate_limit"),
    )

    swiggy_mcp = SwiggyInstamartMCP(mcp_client)
    detector = PatternDetector(repository)

    weights = settings.get("analysis.weights")
    scorer = ItemScorer(
        frequency_weight=weights["frequency"],
        recency_weight=weights["recency"],
        quantity_weight=weights["quantity"],
    )

    predictor = ItemPredictor(detector, scorer)
    basket_manager = BasketManager(swiggy_mcp, repository)

    return {
        "repository": repository,
        "auth_manager": auth_manager,
        "swiggy_mcp": swiggy_mcp,
        "predictor": predictor,
        "basket_manager": basket_manager,
        "mcp_client": mcp_client,
    }


@app.route('/')
def index():
    """Home page."""
    is_authenticated = auth_manager.is_authenticated()
    return render_template('index.html', is_authenticated=is_authenticated)


@app.route('/api/status')
def api_status():
    """Get authentication and database status."""
    is_authenticated = auth_manager.is_authenticated()
    order_count = repository.get_order_count()
    item_count = repository.get_item_count()

    return jsonify({
        'authenticated': is_authenticated,
        'order_count': order_count,
        'item_count': item_count,
    })


@app.route('/api/orders')
def api_orders():
    """Get order history."""
    try:
        # Get all orders from database
        orders = repository.get_all_order_items()

        # Group by order
        orders_grouped = {}
        for item in orders:
            order_id = item['order_id']
            if order_id not in orders_grouped:
                orders_grouped[order_id] = {
                    'order_id': order_id,
                    'order_date': item['order_date'],
                    'items': []
                }

            orders_grouped[order_id]['items'].append({
                'item_name': item['item_name'],
                'quantity': item['quantity'],
                'price': item['price'],
                'category': item['category'],
                'brand': item['brand'],
            })

        # Convert to list and sort by date
        orders_list = list(orders_grouped.values())
        orders_list.sort(key=lambda x: x['order_date'], reverse=True)

        return jsonify({
            'success': True,
            'orders': orders_list[:50]  # Last 50 orders
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/recommendations')
def api_recommendations():
    """Get recommendations."""
    try:
        services = get_services()

        min_score = float(request.args.get('min_score', settings.get("analysis.min_score")))
        max_items = int(request.args.get('max_items', settings.get("analysis.max_items")))

        # Get recommendations
        recommendations = services["predictor"].get_recommendations(min_score, max_items)

        # Validate via MCP if authenticated, otherwise use mock mode
        if auth_manager.is_authenticated():
            try:
                # Real mode - validate via MCP get_item_details() calls
                logger.info("Using real MCP validation for recommendations")
                validated = services["basket_manager"].preview_recommendations(recommendations)
                logger.info(f"MCP validation complete: {len(validated)} items checked")
            except Exception as e:
                logger.error(f"MCP validation failed: {e}")
                # On MCP failure, mark all as unavailable with error
                validated = recommendations
                for rec in validated:
                    rec.available = False
                    rec.current_price = None
                # Return error indication
                return jsonify({
                    'success': False,
                    'error': f"Failed to validate items with Swiggy: {str(e)}",
                    'mode': 'error'
                }), 500
        else:
            # Test mode - use mock prices and mark all available
            logger.info("Using test mode (not authenticated) - mock validation")
            validated = recommendations
            for rec in validated:
                rec.available = True
                rec.current_price = 50.0  # Mock price

        # Convert to dict
        recs_list = []
        for rec in validated:
            recs_list.append({
                'item_id': rec.item_id,
                'item_name': rec.item_name,
                'score': round(rec.score, 1),
                'frequency_score': round(rec.frequency_score, 1),
                'recency_score': round(rec.recency_score, 1),
                'quantity_score': round(rec.quantity_score, 1),
                'suggested_quantity': rec.suggested_quantity,
                'reasoning': rec.reasoning,
                'available': rec.available,
                'current_price': rec.current_price,
            })

        # Save to log
        repository.save_recommendations(validated)

        return jsonify({
            'success': True,
            'recommendations': recs_list
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/basket', methods=['GET'])
def api_get_basket():
    """Get current basket."""
    try:
        if auth_manager.is_authenticated():
            # Real mode - get from Swiggy MCP
            try:
                services = get_services()
                basket_data = services["swiggy_mcp"].get_basket()

                # MCP response format: {items: [...], total: float}
                return jsonify({
                    'success': True,
                    'basket': basket_data,
                    'mode': 'real'
                })
            except Exception as e:
                # On MCP failure, return error (don't silently fall back to mock)
                logger.error(f"Basket fetch from MCP failed: {e}")
                return jsonify({
                    'success': False,
                    'error': f"Failed to fetch basket from Swiggy: {str(e)}",
                    'mode': 'error'
                }), 500
        else:
            # Test mode - return mock basket
            return jsonify({
                'success': True,
                'basket': mock_basket,
                'mode': 'test'
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/basket/add', methods=['POST'])
def api_add_to_basket():
    """Add items to basket."""
    try:
        data = request.json
        items = data.get('items', [])

        if not items:
            return jsonify({
                'success': False,
                'error': 'No items provided'
            }), 400

        # Check if authenticated for real basket operations
        if auth_manager.is_authenticated():
            # Real mode - use MCP to add items to Swiggy basket
            logger.info(f"Adding {len(items)} items to real Swiggy basket via MCP")

            services = get_services()

            # Convert to ItemRecommendation objects
            from swiggy_analyzer.data.models import ItemRecommendation

            recommendations = []
            for item in items:
                rec = ItemRecommendation(
                    item_id=item['item_id'],
                    item_name=item['item_name'],
                    score=item.get('score', 0),
                    frequency_score=0,
                    recency_score=0,
                    quantity_score=0,
                    suggested_quantity=item['quantity'],
                    reasoning='',
                    available=True,
                )
                recommendations.append(rec)

            # Add to basket via MCP
            results = services["basket_manager"].add_items_to_basket(recommendations)
            logger.info(f"Successfully added items to basket: {len(results.get('success', []))} succeeded, {len(results.get('failed', []))} failed")

            return jsonify({
                'success': True,
                'results': results,
                'mode': 'real'
            })
        else:
            # Test mode - add to mock basket
            results = {
                'success': [],
                'failed': [],
                'total_price': 0.0
            }

            for item in items:
                # Add to mock basket
                mock_item = {
                    'id': item['item_id'],
                    'name': item['item_name'],
                    'quantity': item['quantity'],
                    'price': 50.0
                }

                # Check if item already exists in basket
                existing_item = next((i for i in mock_basket['items'] if i['id'] == item['item_id']), None)
                if existing_item:
                    existing_item['quantity'] += item['quantity']
                else:
                    mock_basket['items'].append(mock_item)

                # Update total
                mock_basket['total'] = sum(i['quantity'] * i['price'] for i in mock_basket['items'])

                results['success'].append({
                    'name': item['item_name'],
                    'quantity': item['quantity'],
                    'price': 50.0
                })
                results['total_price'] += 50.0 * item['quantity']

            return jsonify({
                'success': True,
                'results': results,
                'mode': 'test',
                'message': 'Test mode - items added to mock basket'
            })

    except Exception as e:
        logger.exception("Add to basket failed")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/basket/clear', methods=['POST'])
def api_clear_basket():
    """Clear basket."""
    try:
        if auth_manager.is_authenticated():
            # Real mode
            try:
                services = get_services()
                services["basket_manager"].clear_basket()
            except Exception as e:
                # Fall back to clearing mock basket
                mock_basket['items'] = []
                mock_basket['total'] = 0.0
        else:
            # Test mode - clear mock basket
            mock_basket['items'] = []
            mock_basket['total'] = 0.0

        return jsonify({
            'success': True
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/sync', methods=['POST'])
def api_sync():
    """Sync order history."""
    try:
        if not auth_manager.is_authenticated():
            return jsonify({
                'success': False,
                'error': 'Not authenticated'
            }), 401

        services = get_services()

        # Sync orders
        orders = services["swiggy_mcp"].get_order_history(limit=100, days_back=30)
        repository.save_orders(orders)

        # Calculate patterns
        detector = PatternDetector(repository)
        detector.calculate_patterns()

        return jsonify({
            'success': True,
            'orders_synced': len(orders)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)

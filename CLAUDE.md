# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Swiggy Instamart Buying Pattern Analyzer - An AI-powered shopping assistant that analyzes Swiggy Instamart purchase history to predict items you're likely to need, then integrates with Swiggy MCP for real-time cart management.

**Key Technology:** This project uses the official Swiggy MCP (Model Context Protocol) server with JSON-RPC 2.0 protocol for real-time integration with Swiggy Instamart.

## Architecture

### Core Components

1. **MCP Client Layer** (`swiggy_analyzer/mcp/`)
   - `client.py`: JSON-RPC 2.0 client with proper protocol handshake
   - **Critical**: Must initialize MCP connection before calling tools
   - **Critical**: Response format is `{"content": [{"type": "text", "text": "{json...}"}]}`
   - **Critical**: Requires both `application/json` and `text/event-stream` in Accept header
   - Tools: `get_cart`, `get_orders`, `search_products`, `update_cart`, `checkout`
   - Rate limiting: 100 calls/minute default
   - Auto-retry on 401 (token refresh) and 429 (rate limit)

2. **Analysis Engine** (`swiggy_analyzer/analysis/`)
   - `pattern_detector.py`: Calculates purchase frequency and timing patterns
   - `scoring.py`: Weighted scoring (40% frequency, 40% recency, 20% quantity)
   - `predictor.py`: Generates recommendations with reasoning
   - Requires minimum 2 purchases per item to detect patterns

3. **Web Application** (`swiggy_analyzer/web/`)
   - Flask app with service layer pattern via `get_services()` function
   - Services initialized per-request (not globally) to handle auth state
   - Mock basket mode when not authenticated for testing
   - Real MCP mode when authenticated - parses JSON from MCP response
   - **Important**: Basket responses must extract data from nested JSON structure

4. **Authentication** (`swiggy_analyzer/auth/`)
   - OAuth 2.0 PKCE flow with Swiggy
   - Tokens encrypted with Fernet and stored in SQLite
   - `oauth_manager.py` handles token refresh automatically
   - Browser-based authentication via local callback server

### Data Flow

```
Web UI Request
    ↓
get_services() creates fresh service instances
    ↓
MCPClient._initialize() establishes JSON-RPC connection
    ↓
call_tool() sends {"jsonrpc": "2.0", "method": "tools/call", ...}
    ↓
Parse response: result["content"][0]["text"] contains JSON string
    ↓
Return formatted data to web UI
```

## Development Commands

### Setup & Installation

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install in development mode
pip install -e .
pip install -r requirements.txt
```

### Authentication

```bash
# Login (opens browser for OAuth)
.venv/bin/swiggy-analyzer auth login

# Check auth status
.venv/bin/swiggy-analyzer auth status

# Logout
.venv/bin/swiggy-analyzer auth logout
```

### Web Server

```bash
# Start web server
./run_web.sh
# or manually:
.venv/bin/python -m swiggy_analyzer.web.app

# Server runs on http://localhost:5000
# Logs to logs/web.log

# Stop server
lsof -ti:5000 | xargs kill -9
```

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_analysis/test_scoring.py

# Run with coverage
pytest --cov=swiggy_analyzer

# Run single test
pytest tests/test_analysis/test_scoring.py::test_score_calculation -v
```

### Database

```bash
# View database schema
sqlite3 data/swiggy.db ".schema"

# Check orders
sqlite3 data/swiggy.db "SELECT COUNT(*) FROM orders"

# Clear test data
sqlite3 data/swiggy.db "DELETE FROM orders; DELETE FROM order_items; DELETE FROM item_patterns;"
```

## Critical Implementation Details

### MCP Integration

**The Swiggy MCP uses JSON-RPC 2.0 protocol, NOT REST API:**

1. **Initialize before every session:**
   ```python
   message = {
       "jsonrpc": "2.0",
       "id": 1,
       "method": "initialize",
       "params": {
           "protocolVersion": "2024-11-05",
           "capabilities": {},
           "clientInfo": {"name": "swiggy-analyzer", "version": "0.1.0"}
       }
   }
   ```

2. **Call tools with proper format:**
   ```python
   message = {
       "jsonrpc": "2.0",
       "id": 2,
       "method": "tools/call",
       "params": {
           "name": "get_cart",
           "arguments": {}
       }
   }
   ```

3. **Parse nested response:**
   ```python
   result = response.json()  # JSON-RPC response
   text_content = result["result"]["content"][0]["text"]  # Extract text
   data = json.loads(text_content)  # Parse inner JSON
   ```

### MCP Limitations

- **Order history**: Only last 7 days available via MCP
- **Instamart only**: Grocery orders only, not food delivery
- **Authentication**: Must not use Swiggy app simultaneously (session conflicts)
- **Payment**: Checkout supports COD (Cash on Delivery) only

### Service Layer Pattern

The web app uses a service factory function instead of global services:

```python
def get_services():
    """Creates fresh service instances per request."""
    mcp_client = MCPClient(...)
    swiggy_mcp = SwiggyInstamartMCP(mcp_client)
    # ... more services
    return {"swiggy_mcp": swiggy_mcp, ...}
```

**Why:** Handles authentication state changes and allows per-request configuration.

### Authentication Flow

1. User runs `swiggy-analyzer auth login`
2. Local callback server starts on random port
3. Browser opens Swiggy OAuth page
4. After approval, token received via callback
5. Token encrypted with Fernet and stored in `oauth_tokens` table
6. Token automatically refreshed when expired (401 responses)

### Database Schema

```sql
orders (id, order_date, total_amount, raw_data, created_at, updated_at)
order_items (id, order_id, item_id, item_name, quantity, price, category, brand)
item_patterns (item_id, item_name, frequency, avg_interval_days, last_purchase_date, avg_quantity, total_purchases)
oauth_tokens (service, access_token, refresh_token, expires_at, created_at, updated_at)
```

## Configuration

Edit `config.yaml`:

```yaml
analysis:
  min_score: 50.0          # Minimum recommendation score
  weights:
    frequency: 0.40        # Purchase frequency weight
    recency: 0.40          # Time since last purchase
    quantity: 0.20         # Quantity consistency

mcp:
  base_url: "https://mcp.swiggy.com/im"
  timeout: 30
  retry_attempts: 3
  rate_limit: 100
```

## Common Pitfalls

1. **MCP 406 Error**: Missing Accept header with both content types
   - Fix: `Accept: "application/json, text/event-stream"`

2. **MCP 404 Error**: Using wrong endpoint (e.g., `/tools/call` instead of base URL)
   - Fix: POST to base URL with JSON-RPC message

3. **Empty cart/orders**: Forgot to initialize MCP connection
   - Fix: Call `_initialize()` before `call_tool()`

4. **Token errors**: Token expired but refresh failed
   - Fix: Run `swiggy-analyzer auth login` again

5. **Parsing errors**: Trying to access data directly from MCP response
   - Fix: Parse nested JSON from `result["content"][0]["text"]`

## Web UI Structure

```
web/
├── app.py              # Flask routes and API endpoints
├── templates/
│   └── index.html      # Single-page dashboard
└── static/
    ├── css/style.css   # Custom styles
    └── js/app.js       # Frontend logic (AJAX)
```

API endpoints:
- `GET /api/status` - Auth status
- `GET /api/recommendations` - AI recommendations
- `GET /api/basket` - Current cart
- `POST /api/basket/add` - Add items
- `POST /api/sync` - Sync from Swiggy

## CLI Commands

```bash
# Analysis
swiggy-analyzer analyze run [--min-score 60] [--max-items 10]

# Sync
swiggy-analyzer sync now [--full]

# Basket
swiggy-analyzer basket view
swiggy-analyzer basket clear

# Schedule (macOS only)
swiggy-analyzer schedule enable
swiggy-analyzer schedule disable
```

## Project Context

- **Python Version**: 3.9+ (MCP SDK requires 3.10+, we use manual JSON-RPC)
- **MCP Protocol**: JSON-RPC 2.0 over HTTPS
- **Database**: SQLite with encrypted OAuth tokens
- **Web Framework**: Flask with Bootstrap 5
- **Authentication**: OAuth 2.0 PKCE
- **Testing**: pytest with fixtures

## Key Files to Understand

1. `swiggy_analyzer/mcp/client.py` - MCP protocol implementation
2. `swiggy_analyzer/mcp/endpoints.py` - MCP tool wrappers with response parsing
3. `swiggy_analyzer/web/app.py` - Web API with service layer
4. `swiggy_analyzer/analysis/predictor.py` - Recommendation algorithm
5. `swiggy_analyzer/auth/oauth_manager.py` - OAuth flow implementation

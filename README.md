# Swiggy Instamart Buying Pattern Analyzer

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

AI-powered shopping assistant that analyzes your Swiggy Instamart purchase history to predict items you're likely to need, then integrates with Swiggy MCP for real-time cart management.

![Swiggy Analyzer Demo](https://img.shields.io/badge/status-active-success)

## ✨ Features

### 🧠 Smart Pattern Analysis
- **Purchase Frequency Analysis** - Tracks how often you buy each item
- **Recency Scoring** - Identifies items due for reorder based on past patterns
- **Quantity Intelligence** - Learns your typical purchase quantities
- **Weighted Algorithm** - 40% frequency + 40% recency + 20% quantity

### 🌐 Beautiful Web Interface
- **Real-time Dashboard** - See order history, recommendations, and cart
- **One-Click Add to Cart** - Add AI recommendations directly to your Swiggy cart
- **Live Cart Sync** - View your actual Swiggy Instamart cart in real-time
- **Responsive Design** - Works on desktop, tablet, and mobile

### 🔗 Swiggy MCP Integration
- **Real-time Cart Management** - Fetch and update your actual Swiggy cart
- **Order History Tracking** - Sync orders from last 7 days
- **Product Search** - Search Swiggy Instamart inventory
- **Address Management** - Use your saved delivery addresses

### 🔒 Privacy & Security
- **OAuth 2.0 PKCE** - Secure authentication flow
- **Encrypted Token Storage** - Tokens encrypted in local SQLite database
- **Local Data Only** - All analysis runs on your machine
- **No Cloud Sync** - Your data never leaves your device

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- macOS (for scheduling features)
- Swiggy Instamart account

### Installation

```bash
# Clone the repository
git clone https://github.com/hiransuvrat/swiggy-analyzer.git
cd swiggy-analyzer

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Authentication

```bash
# Login to Swiggy (opens browser for OAuth)
swiggy-analyzer auth login

# Check authentication status
swiggy-analyzer auth status
```

### Start Web UI

```bash
# Start the web server
./run_web.sh

# Open in browser
./open_web_ui.sh

# Or manually visit: http://localhost:5000
```

## 📖 Usage

### Web Interface

The web UI provides three main panels:

1. **Recommendations Panel** (Left)
   - AI-powered item suggestions
   - Color-coded scores (green = high priority)
   - One-click add to cart
   - Reasoning for each recommendation

2. **Order History Panel** (Right)
   - Chronological order list
   - Item details and quantities
   - Purchase frequency insights

3. **Cart Panel** (Bottom)
   - Real-time Swiggy cart display
   - Total price breakdown
   - Quick cart management

### CLI Commands

```bash
# Sync order history from Swiggy
swiggy-analyzer sync now

# Get AI recommendations (CLI)
swiggy-analyzer analyze run

# View basket
swiggy-analyzer basket view

# Manage authentication
swiggy-analyzer auth login
swiggy-analyzer auth status
swiggy-analyzer auth logout
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Web UI (Flask)                    │
│              Bootstrap 5 + Vanilla JS               │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│              Core Analysis Engine                   │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │   Pattern    │  │    Scoring   │  │ Predictor │ │
│  │   Detector   │  │    Engine    │  │           │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│              Swiggy MCP Client                      │
│        (JSON-RPC 2.0 over HTTPS)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │   get_cart   │  │  get_orders  │  │  search   │ │
│  │ update_cart  │  │get_addresses │  │  checkout │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│          Swiggy Instamart MCP Server                │
│         https://mcp.swiggy.com/im                   │
└─────────────────────────────────────────────────────┘
```

## 🔧 Configuration

Edit `config.yaml` to customize:

```yaml
analysis:
  min_score: 50.0          # Minimum recommendation score
  max_items: 20            # Max recommendations to show
  weights:
    frequency: 0.40        # Weight for purchase frequency
    recency: 0.40          # Weight for time since last purchase
    quantity: 0.20         # Weight for quantity patterns

mcp:
  base_url: "https://mcp.swiggy.com/im"
  timeout: 30
  retry_attempts: 3
  rate_limit: 100          # Max requests per minute
```

## 📊 API Endpoints

### Web API

- `GET  /api/status` - Authentication and database status
- `GET  /api/orders` - Order history (last 50)
- `GET  /api/recommendations` - AI recommendations
- `GET  /api/basket` - Current cart contents
- `POST /api/basket/add` - Add items to cart
- `POST /api/basket/clear` - Clear cart
- `POST /api/sync` - Sync orders from Swiggy

All endpoints return JSON with `success` field and appropriate data/error messages.

## 🛠️ Development

### Project Structure

```
swiggy-analyzer/
├── swiggy_analyzer/
│   ├── analysis/          # Pattern detection & scoring
│   ├── auth/              # OAuth authentication
│   ├── basket/            # Cart management
│   ├── cli/               # Command-line interface
│   ├── config/            # Configuration management
│   ├── mcp/               # Swiggy MCP client
│   ├── scheduler/         # Background job scheduling
│   └── web/               # Flask web application
├── tests/                 # Unit tests
├── config.yaml            # Configuration file
├── requirements.txt       # Python dependencies
└── setup.py              # Package installation
```

### Running Tests

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run tests
pytest

# With coverage
pytest --cov=swiggy_analyzer
```

### Code Style

```bash
# Format code
black swiggy_analyzer/

# Check types
mypy swiggy_analyzer/

# Lint
flake8 swiggy_analyzer/
```

## 🔐 MCP Integration Details

This project uses the official Swiggy MCP server with proper JSON-RPC 2.0 protocol:

### Available Tools

- `get_cart` - Fetch current cart with items and pricing
- `update_cart` - Add/remove items from cart
- `clear_cart` - Empty the cart
- `get_orders` - Order history (last 7 days)
- `search_products` - Search Swiggy Instamart catalog
- `get_addresses` - Saved delivery addresses
- `checkout` - Place order (COD only)

### Authentication

Uses OAuth 2.0 PKCE flow:
1. Browser opens for Swiggy login
2. User authorizes the app
3. Access token encrypted and stored locally
4. Automatic token refresh on expiry

## 📝 Important Notes

### Limitations

- **Order History**: MCP can only fetch orders from last 7 days
- **Instamart Only**: Only grocery orders (not food delivery)
- **Payment**: Checkout supports COD (Cash on Delivery) only
- **Session Conflicts**: Don't use Swiggy app while using MCP

### Data Privacy

- All data stored locally in SQLite database
- OAuth tokens encrypted with Fernet (symmetric encryption)
- No telemetry or analytics
- No cloud sync
- Your data never leaves your machine

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Swiggy](https://www.swiggy.com) for the MCP server
- [Model Context Protocol](https://modelcontextprotocol.io) specification
- [Flask](https://flask.palletsprojects.com/) web framework
- [Bootstrap](https://getbootstrap.com/) UI framework

## 🔗 Links

- **Repository**: https://github.com/hiransuvrat/swiggy-analyzer
- **Issues**: https://github.com/hiransuvrat/swiggy-analyzer/issues
- **Swiggy MCP Docs**: https://github.com/Swiggy/swiggy-mcp-server-manifest

## 📧 Contact

**Suvrat Hiran** - [@hiransuvrat](https://github.com/hiransuvrat)

---

**⭐ Star this repo if you find it useful!**

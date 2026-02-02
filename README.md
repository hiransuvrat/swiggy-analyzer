# Swiggy Instamart Buying Pattern Analyzer

A Python CLI tool that analyzes your Swiggy Instamart purchase history to predict items you're likely to need, then presents recommendations for confirmation before adding to your basket.

## Features

- **Pattern Analysis**: Analyzes purchase frequency, timing, and quantity patterns
- **Smart Recommendations**: Weighted scoring algorithm (40% frequency, 40% recency, 20% quantity)
- **Interactive CLI**: Rich terminal interface with multi-select confirmation
- **Scheduled Runs**: Daily automation via macOS launchd
- **Secure Authentication**: OAuth PKCE with encrypted token storage
- **Privacy First**: All data stored locally, no cloud sync

## Installation

### Prerequisites

- Python 3.9 or higher
- macOS (for scheduling features)
- Swiggy Instamart account

### Setup

1. Clone or navigate to the project directory:
```bash
cd /Users/suvrat.hiran/project/swiggy
```

2. Create and activate virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install the package:
```bash
pip install -e .
```

## Usage

### Authentication

First, authenticate with Swiggy MCP:

```bash
swiggy-analyzer auth login
```

This will open your browser for OAuth authentication. After successful login, tokens are securely stored.

Check authentication status:
```bash
swiggy-analyzer auth status
```

### Sync Order History

Sync your order history from Swiggy:

```bash
# Incremental sync (last 30 days)
swiggy-analyzer sync now

# Full historical sync
swiggy-analyzer sync now --full
```

### Run Analysis

Get personalized recommendations:

```bash
# Run with defaults
swiggy-analyzer analyze run

# Customize parameters
swiggy-analyzer analyze run --min-score 70 --max-items 10

# Dry run (no basket changes)
swiggy-analyzer analyze run --dry-run

# Auto-add without confirmation
swiggy-analyzer analyze run --auto-add
```

The analysis will:
1. Optionally sync latest orders
2. Calculate buying patterns
3. Generate scored recommendations
4. Validate item availability
5. Show interactive preview
6. Add selected items to basket

### Basket Management

View current basket:
```bash
swiggy-analyzer basket view
```

Clear basket:
```bash
swiggy-analyzer basket clear
```

### Scheduling

Enable daily automated analysis:

```bash
# Enable at 9:30 AM daily
swiggy-analyzer schedule enable --hour 9 --minute 30

# Check status
swiggy-analyzer schedule status

# Disable
swiggy-analyzer schedule disable
```

### Configuration

View current configuration:
```bash
swiggy-analyzer config show
```

Modify settings:
```bash
swiggy-analyzer config set analysis.min_score 60
swiggy-analyzer config set sync.auto_sync false
```

Or edit `config.yaml` directly.

## How It Works

### Scoring Algorithm

Each item gets a score (0-100) based on three factors:

1. **Frequency Score (40%)**: Logarithmic scale based on total purchases
   - 2 purchases = 23.8
   - 10 purchases = 52.3
   - 100 purchases = 100.5 (capped at 100)

2. **Recency Score (40%)**: Based on expected reorder interval
   - Too recent (<0.5× interval) = Low score
   - Sweet spot (0.9-1.2× interval) = 90-100 points
   - Overdue (>1.2× interval) = Exponential decay

3. **Quantity Score (20%)**: Consistency of order quantities
   - Low variation = High score
   - Uses coefficient of variation (std_dev / mean)

### Example Recommendations

```
┌────────────────────────────────────────────────────────┐
│ # │ Item               │ Qty │ Score │ Price │ Reasoning│
├───┼────────────────────┼─────┼───────┼───────┼──────────┤
│ 1 │ Amul Milk 1L       │ 2   │ 87.3  │ ₹58   │ frequent…│
│ 2 │ Bread Whole Wheat  │ 1   │ 79.1  │ ₹45   │ overdue… │
│ 3 │ Eggs 6 Pack        │ 1   │ 68.5  │ ₹36   │ due for… │
└────────────────────────────────────────────────────────┘
```

## Configuration

Key settings in `config.yaml`:

```yaml
analysis:
  min_score: 50.0          # Only show items with score ≥ 50
  max_items: 20            # Show max 20 recommendations

sync:
  auto_sync: true          # Sync before each analysis

basket:
  preview_required: true   # Always confirm before adding

schedule:
  enabled: false
  hour: 9
  minute: 0
```

## Project Structure

```
/Users/suvrat.hiran/project/swiggy/
├── swiggy_analyzer/        # Main package
│   ├── auth/               # OAuth authentication
│   ├── mcp/                # Swiggy MCP client
│   ├── data/               # Data models & repository
│   ├── analysis/           # Pattern detection & scoring
│   ├── basket/             # Basket operations
│   ├── scheduler/          # Launchd integration
│   ├── config/             # Configuration management
│   └── cli/                # CLI commands
├── data/
│   └── swiggy.db           # SQLite database
├── logs/
│   └── swiggy_analyzer.log
├── config.yaml             # User configuration
└── requirements.txt
```

## Security & Privacy

- **OAuth PKCE**: Secure authentication flow
- **Token Encryption**: Tokens encrypted using macOS Keychain
- **Local Storage**: All data stored locally, never transmitted elsewhere
- **No Cloud Sync**: Complete privacy and control

## Troubleshooting

### "Authentication failed"
- Check internet connection
- Ensure browser can access https://mcp.swiggy.com
- Try: `swiggy-analyzer auth logout` then login again

### "No recommendations"
- Need at least 2 orders with repeated items
- Try: `swiggy-analyzer sync now --full`
- Lower threshold: `swiggy-analyzer config set analysis.min_score 30`

### "MCP server unreachable"
- Check Swiggy MCP server status
- Verify token: `swiggy-analyzer auth status`
- Check logs: `tail -f logs/swiggy_analyzer.log`

### Schedule not running
- Check: `launchctl list | grep swiggy`
- View logs: `cat logs/swiggy_analyzer.log`
- Reload: `swiggy-analyzer schedule disable && swiggy-analyzer schedule enable`

## Development

Run tests:
```bash
pytest tests/ -v --cov=swiggy_analyzer
```

Run in development mode:
```bash
python -m swiggy_analyzer.cli.main analyze run --dry-run
```

## License

MIT License

## Author

Suvrat Hiran

# Next Steps - Getting Started

## Installation (5-10 minutes)

### Option 1: Automated Installation
```bash
./install.sh
```

### Option 2: Manual Installation
```bash
# 1. Create virtual environment
python3 -m venv .venv

# 2. Activate
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install package
pip install -e .
```

## Initial Setup

### 1. Verify Installation
```bash
./verify.sh
```

### 2. Authenticate with Swiggy MCP

**Important**: You need actual Swiggy MCP credentials. The implementation assumes:
- MCP Server URL: `https://mcp.swiggy.com/im`
- OAuth endpoints for authentication
- API tools: `get_order_history`, `add_to_basket`, etc.

```bash
swiggy-analyzer auth login
```

This will:
1. Open browser for OAuth authentication
2. Handle the callback on `http://localhost:3118`
3. Store encrypted tokens in macOS Keychain

### 3. Sync Order History
```bash
# Sync last 30 days
swiggy-analyzer sync now

# Or full history
swiggy-analyzer sync now --full
```

### 4. Run Your First Analysis
```bash
# Test with dry run
swiggy-analyzer analyze run --dry-run

# Real run with confirmation
swiggy-analyzer analyze run
```

## Testing the Implementation

### Without Real MCP Access

If you don't have Swiggy MCP credentials yet, you can:

1. **Test the data layer**:
```bash
python3 -c "
from swiggy_analyzer.data.repository import SwiggyRepository
repo = SwiggyRepository('data/test.db')
print('✓ Database initialized')
print(f'Tables created: {repo._get_connection().execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()}')
"
```

2. **Test pattern detection with mock data**:
```bash
pytest tests/test_analysis/ -v
```

3. **Test scoring algorithm**:
```bash
pytest tests/test_analysis/test_scoring.py -v
```

### With Real MCP Access

1. **Authenticate**:
```bash
swiggy-analyzer auth login
```

2. **Test API connection**:
```bash
python3 -c "
from swiggy_analyzer.config.settings import Settings
from swiggy_analyzer.data.repository import SwiggyRepository
from swiggy_analyzer.auth.token_store import TokenStore
from swiggy_analyzer.auth.oauth_manager import OAuthManager
from swiggy_analyzer.mcp.client import MCPClient

settings = Settings()
repo = SwiggyRepository(settings.get_db_path())
token_store = TokenStore(repo)
auth_manager = OAuthManager(token_store)

if auth_manager.is_authenticated():
    print('✓ Authenticated')
    client = MCPClient(settings.get_mcp_base_url(), auth_manager)
    tools = client.list_tools()
    print(f'✓ Connected to MCP server')
    print(f'Available tools: {list(tools.keys())}')
else:
    print('✗ Not authenticated')
"
```

3. **Sync and analyze**:
```bash
swiggy-analyzer sync now
swiggy-analyzer analyze run --dry-run
```

## MCP API Integration Notes

The implementation expects the Swiggy MCP server to provide these tools:

### Required MCP Tools

1. **get_order_history**
   - Arguments: `limit`, `offset`, `since` (optional)
   - Returns: `{orders: [{id, order_date, total_amount, items: [...]}]}`

2. **add_to_basket**
   - Arguments: `item_id`, `quantity`
   - Returns: `{success: true/false}`

3. **get_item_details**
   - Arguments: `item_id`
   - Returns: `{item: {available, price}}`

4. **get_basket**
   - Returns: `{items: [...], total: number}`

5. **clear_basket**
   - Returns: `{success: true/false}`

### If API Structure Differs

If the actual Swiggy MCP API has different tool names or response formats, update:
- `swiggy_analyzer/mcp/endpoints.py` - API wrapper methods
- `swiggy_analyzer/data/models.py` - If data structure differs

Everything else remains unchanged due to the layered architecture.

## Configuration

### Adjust Scoring Weights

Edit `config.yaml`:
```yaml
analysis:
  weights:
    frequency: 0.40  # Purchase frequency importance
    recency: 0.40    # Timing/overdue importance
    quantity: 0.20   # Quantity consistency importance
```

### Adjust Recommendation Threshold

```bash
# Lower threshold for fewer recommendations
swiggy-analyzer config set analysis.min_score 40

# Increase max items
swiggy-analyzer config set analysis.max_items 30
```

## Setting Up Automation

### Enable Daily Analysis

```bash
# Run daily at 9:30 AM
swiggy-analyzer schedule enable --hour 9 --minute 30
```

### Verify Schedule
```bash
# Check launchd
launchctl list | grep swiggy

# Check schedule status
swiggy-analyzer schedule status

# View logs
tail -f logs/swiggy_analyzer.log
```

## Troubleshooting

### Common Issues

1. **Import errors after installation**
   - Make sure you activated the virtual environment
   - Run `pip install -e .` again

2. **OAuth callback fails**
   - Check firewall allows localhost:3118
   - Try using a different port (modify in `oauth_manager.py`)

3. **No patterns detected**
   - Need at least 2 orders with repeated items
   - Check database: `sqlite3 data/swiggy.db "SELECT COUNT(*) FROM orders"`

4. **MCP connection fails**
   - Verify MCP server URL in config.yaml
   - Check authentication: `swiggy-analyzer auth status`
   - Review logs: `tail -f logs/swiggy_analyzer.log`

### Debug Mode

Enable debug logging in `config.yaml`:
```yaml
logging:
  level: DEBUG
```

Then check logs:
```bash
tail -f logs/swiggy_analyzer.log
```

## Development Workflow

### Running Tests

```bash
# Activate venv
source .venv/bin/activate

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=swiggy_analyzer

# Run specific test
pytest tests/test_analysis/test_scoring.py -v
```

### Adding New Features

The modular architecture makes it easy to extend:

1. **New scoring factors**: Add to `analysis/scoring.py`
2. **New MCP tools**: Add to `mcp/endpoints.py`
3. **New CLI commands**: Add to `cli/commands.py`
4. **New data models**: Add to `data/models.py`

## Support

### Check Logs
```bash
tail -f logs/swiggy_analyzer.log
```

### View Database
```bash
sqlite3 data/swiggy.db

# Useful queries:
.tables
SELECT COUNT(*) FROM orders;
SELECT COUNT(DISTINCT item_id) FROM order_items;
SELECT * FROM item_patterns ORDER BY total_purchases DESC LIMIT 10;
```

### Reset Everything
```bash
# Remove all data
rm -rf data/ logs/

# Re-authenticate
swiggy-analyzer auth logout
swiggy-analyzer auth login
```

## What to Expect

### After First Sync
- Database created in `data/swiggy.db`
- Orders and items imported
- Patterns calculated

### After First Analysis
- Recommendations with scores
- Interactive selection prompt
- Items added to basket (if confirmed)
- Logs in `logs/swiggy_analyzer.log`

### With Scheduled Runs
- Daily execution at configured time
- Automatic order sync
- Recommendations logged
- Items added to basket

## Getting Help

1. Check `README.md` for comprehensive documentation
2. Review `QUICKSTART.md` for quick commands
3. Check logs: `tail -f logs/swiggy_analyzer.log`
4. Run verification: `./verify.sh`
5. Test with dry run: `swiggy-analyzer analyze run --dry-run`

## Success Checklist

- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Package installed (`swiggy-analyzer` command works)
- [ ] Authenticated with Swiggy MCP
- [ ] Orders synced successfully
- [ ] Patterns calculated
- [ ] Recommendations generated
- [ ] Items added to basket
- [ ] Schedule configured (optional)

Once all items are checked, you have a fully functional system!

---

**For immediate help**: Run `swiggy-analyzer --help`

# Swiggy Analyzer - Web UI Guide

## Overview

The web UI provides a simple, visual interface to:
- View your past order history
- See AI-powered recommendations with scores
- Add items to your basket with one click
- Manage your basket

## Quick Start

### 1. Create Test Data (Optional)
If you want to try the UI without connecting to Swiggy MCP:

```bash
.venv/bin/python create_test_data.py
```

This creates ~94 sample orders with realistic patterns.

### 2. Start the Web Server

```bash
./run_web.sh
```

Or manually:
```bash
.venv/bin/python -m swiggy_analyzer.web.app
```

### 3. Open Your Browser

Navigate to: **http://localhost:5000**

## Features

### 🎯 Recommendations Panel (Left)
- **Smart Scoring**: Items scored 0-100 based on your buying patterns
  - 🟢 **80-100**: High priority (frequent + overdue)
  - 🟡 **60-79**: Medium priority (regular + due soon)
  - ⚫ **50-59**: Low priority (occasional)
- **Min Score Slider**: Filter recommendations by score threshold
- **Reasoning**: See why each item is recommended
- **Quick Add**: Click "Add" button to add individual items
- **Add All**: Add all available items at once

### 📦 Order History Panel (Right)
- View your past orders chronologically
- See items and quantities per order
- Scrollable list of recent orders
- Auto-refreshes after sync

### 🛒 Basket Panel (Bottom)
- View current basket contents
- See quantities and prices
- Total amount calculation
- Clear basket with one click

### 🔄 Top Bar Controls
- **Status Indicator**: Shows authentication status
  - 🟢 Connected
  - 🔴 Not Authenticated
- **Sync Button**: Fetch latest orders from Swiggy MCP
  - Syncs last 30 days
  - Updates patterns automatically

## UI Components

### Recommendation Cards

Each recommendation shows:
```
┌─────────────────────────────────────┐
│ [Score] Item Name              [Add]│
│ Reasoning text...                   │
│ [Qty: 2] [₹58.00] [Available]      │
└─────────────────────────────────────┘
```

- **Score Badge**: Color-coded by priority
- **Item Name**: Product name
- **Reasoning**: Why it's recommended
- **Badges**: Quantity, price, availability
- **Add Button**: Adds to basket immediately

### Order History Cards

```
┌─────────────────────────────────────┐
│ Jan 15, 2026              [3 items] │
│ • Amul Milk 1L              ×2      │
│ • Bread Whole Wheat         ×1      │
│ • Eggs 6 Pack              ×1      │
└─────────────────────────────────────┘
```

## API Endpoints

The web UI uses these REST API endpoints:

### GET /api/status
Returns authentication and database status
```json
{
  "authenticated": true,
  "order_count": 94,
  "item_count": 8
}
```

### GET /api/orders
Returns order history
```json
{
  "success": true,
  "orders": [...]
}
```

### GET /api/recommendations
Get recommendations (supports query params)
- `min_score`: Minimum score threshold (default: 50)
- `max_items`: Maximum items to return (default: 20)

```json
{
  "success": true,
  "recommendations": [
    {
      "item_id": "milk_1l",
      "item_name": "Amul Milk 1L",
      "score": 87.3,
      "reasoning": "frequently purchased, due for reorder",
      "suggested_quantity": 2,
      "available": true,
      "current_price": 58.00
    }
  ]
}
```

### GET /api/basket
Get current basket contents

### POST /api/basket/add
Add items to basket
```json
{
  "items": [
    {
      "item_id": "milk_1l",
      "item_name": "Amul Milk 1L",
      "quantity": 2,
      "score": 87.3
    }
  ]
}
```

### POST /api/basket/clear
Clear all items from basket

### POST /api/sync
Sync order history from Swiggy MCP

## Configuration

The web UI uses the same configuration as the CLI:

```yaml
# config.yaml
analysis:
  min_score: 50.0
  max_items: 20
  weights:
    frequency: 0.40
    recency: 0.40
    quantity: 0.20
```

Changes to `config.yaml` require server restart.

## Using with Real Swiggy MCP

### 1. Authenticate
First, authenticate via CLI:
```bash
.venv/bin/swiggy-analyzer auth login
```

### 2. Start Web Server
```bash
./run_web.sh
```

### 3. Sync Orders
Click the "Sync" button in the top bar, or use CLI:
```bash
.venv/bin/swiggy-analyzer sync now
```

### 4. View Recommendations
The recommendations panel will show items based on your real order history.

### 5. Add to Basket
Click "Add" on any item to add it to your actual Swiggy basket.

## Troubleshooting

### "Not Authenticated" Warning
**Problem**: Web UI shows authentication warning

**Solution**:
```bash
.venv/bin/swiggy-analyzer auth login
```

### Empty Order History
**Problem**: No orders showing

**Solution**:
- Create test data: `.venv/bin/python create_test_data.py`
- Or sync real orders: Click "Sync" button

### No Recommendations
**Problem**: Recommendations panel is empty

**Solution**:
- Lower the min score slider
- Need at least 2 orders per item for patterns
- Sync more orders

### Port Already in Use
**Problem**: Error: Address already in use

**Solution**:
```bash
# Find process using port 5000
lsof -ti:5000 | xargs kill -9

# Or change port in app.py:
# app.run(debug=True, port=5001)
```

### Server Won't Start
**Problem**: Import errors or Flask not found

**Solution**:
```bash
# Reinstall dependencies
.venv/bin/pip install -r requirements.txt

# Verify Flask installed
.venv/bin/pip list | grep -i flask
```

## Development

### Running in Debug Mode
The server runs in debug mode by default:
- Auto-reload on code changes
- Detailed error pages
- Debug logs in terminal

### Custom Port
Edit `swiggy_analyzer/web/app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Change port here
```

### Adding New Features
The Flask app structure:
```
swiggy_analyzer/web/
├── app.py              # Flask routes and API
├── templates/          # HTML templates
│   └── index.html      # Main UI
└── static/             # Static assets
    ├── css/
    │   └── style.css   # Custom styles
    └── js/
        └── app.js      # Frontend logic
```

## Security Notes

- **Local Only**: Server binds to localhost (not accessible from network)
- **No Authentication**: UI doesn't have its own auth (uses existing Swiggy auth)
- **Development Mode**: Don't use in production (debug mode enabled)
- **Token Security**: Tokens stored securely via existing auth system

## Performance

- **Responsive**: AJAX-based, no page reloads
- **Fast**: Local SQLite database
- **Lightweight**: ~500 KB total assets
- **Real-time**: Auto-updates after actions

## Browser Support

Tested on:
- ✅ Chrome 120+
- ✅ Safari 17+
- ✅ Firefox 120+
- ✅ Edge 120+

Requires:
- JavaScript enabled
- Modern browser (ES6+ support)

## Keyboard Shortcuts

None yet, but you can add them in `static/js/app.js`

## Mobile Support

The UI is responsive and works on mobile devices:
- Touch-friendly buttons
- Responsive layout
- Readable text sizes
- Scrollable panels

## Customization

### Change Colors
Edit `static/css/style.css`:
```css
.score-high {
    background-color: #28a745 !important;
}

.score-medium {
    background-color: #ffc107 !important;
}
```

### Modify Layout
Edit `templates/index.html`:
- Bootstrap 5 grid system
- Card-based layout
- Easy to reorganize

### Add Charts
Consider adding:
- Chart.js for spending trends
- Purchase frequency graphs
- Category breakdowns

## Future Enhancements

Potential features:
- [ ] Dark mode toggle
- [ ] Budget tracking
- [ ] Price history charts
- [ ] Category filters
- [ ] Search functionality
- [ ] Export to CSV
- [ ] Shopping list mode
- [ ] Schedule configuration via UI

---

## Quick Reference

**Start Server**: `./run_web.sh`

**URL**: http://localhost:5000

**Create Test Data**: `.venv/bin/python create_test_data.py`

**View Logs**: Check terminal output where server is running

**Stop Server**: Press Ctrl+C in terminal

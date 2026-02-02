# Quick Start Guide

## Installation (5 minutes)

```bash
# Run installation script
./install.sh

# Or manually:
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## First Run (10 minutes)

### 1. Authenticate
```bash
swiggy-analyzer auth login
```
- Opens browser for Swiggy OAuth login
- Tokens stored securely in macOS Keychain

### 2. Sync Order History
```bash
swiggy-analyzer sync now
```
- Fetches last 30 days of orders
- Calculates buying patterns

### 3. Run Analysis
```bash
swiggy-analyzer analyze run
```
- Shows recommendations with scores
- Select items to add
- Items added to basket

## Daily Use

```bash
# Quick analysis
swiggy-analyzer analyze run

# With custom settings
swiggy-analyzer analyze run --min-score 70 --max-items 10

# Test without adding to basket
swiggy-analyzer analyze run --dry-run
```

## Automation

```bash
# Enable daily run at 9:30 AM
swiggy-analyzer schedule enable --hour 9 --minute 30

# Check status
swiggy-analyzer schedule status

# Disable
swiggy-analyzer schedule disable
```

## Common Commands

```bash
# Authentication
swiggy-analyzer auth status
swiggy-analyzer auth logout

# Basket
swiggy-analyzer basket view
swiggy-analyzer basket clear

# Configuration
swiggy-analyzer config show
swiggy-analyzer config set analysis.min_score 60
```

## Configuration

Edit `config.yaml`:

```yaml
analysis:
  min_score: 50.0      # Adjust threshold
  max_items: 20        # Limit recommendations

sync:
  auto_sync: true      # Sync before each analysis

basket:
  auto_add: false      # Require confirmation
```

## Understanding Scores

- **80-100**: High priority (frequent + overdue)
- **60-79**: Medium priority (regular + due soon)
- **50-59**: Low priority (occasional or not due yet)

Items score higher if:
- Purchased frequently
- Overdue based on typical interval
- Consistent quantities

## Troubleshooting

### No recommendations?
```bash
# Sync more history
swiggy-analyzer sync now --full

# Lower threshold
swiggy-analyzer config set analysis.min_score 30
```

### Auth expired?
```bash
swiggy-analyzer auth logout
swiggy-analyzer auth login
```

### Check logs
```bash
tail -f logs/swiggy_analyzer.log
```

## Tips

1. Run analysis weekly to maintain patterns
2. Lower min_score if you have fewer orders
3. Use `--dry-run` to test before adding
4. Schedule runs for consistent automation

## Example Output

```
🛒 Recommended Items
┌───┬────────────────────┬─────┬───────┬────────┬──────────────────┐
│ # │ Item               │ Qty │ Score │ Price  │ Reasoning        │
├───┼────────────────────┼─────┼───────┼────────┼──────────────────┤
│ 1 │ Amul Milk 1L       │ 2   │ 87.3  │ ₹58.00 │ frequently pur…  │
│ 2 │ Bread Whole Wheat  │ 1   │ 79.1  │ ₹45.00 │ overdue by 2 d…  │
│ 3 │ Eggs 6 Pack        │ 1   │ 68.5  │ ₹36.00 │ due for reorder  │
└───┴────────────────────┴─────┴───────┴────────┴──────────────────┘

Select items to add to basket: [✓] All selected

Adding items to basket...

Basket Update Summary
✓ Successfully added: 3 items
  • Amul Milk 1L (2x)
  • Bread Whole Wheat (1x)
  • Eggs 6 Pack (1x)

Basket Total: ₹197.00
```

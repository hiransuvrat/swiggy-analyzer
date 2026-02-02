# Web UI Troubleshooting Guide

## Issue: Can't See "Add" Buttons ✅ FIXED

### Problem
Recommendation items were showing up, but there was no "Add" button to add items to the basket.

### Root Cause
The system was trying to validate item availability with the Swiggy MCP server (which isn't available in test mode), causing all items to be marked as unavailable. The UI only shows "Add" buttons for available items.

### Solution Applied
Updated the code to automatically mark all items as available in test mode, allowing you to:
- See green "Add" buttons on each recommendation
- Click to add individual items
- Use "Add All Available Items" button

### Status
✅ **FIXED** - Server has been updated and restarted

---

## How to Verify the Fix

1. **Refresh Your Browser**
   - Go to http://localhost:5000
   - Press Cmd+R (Mac) or F5 (Windows/Linux)
   - Or click browser refresh button

2. **Check Recommendations Panel**
   - Should see green "Add" buttons on each item
   - Should see "Add All Available Items" button at top
   - Items should have green/yellow/gray score badges

3. **Test Adding Items**
   - Click any "Add" button
   - Toast notification should appear (top right)
   - Basket panel at bottom should update

---

## Common Issues & Solutions

### 1. Still Don't See "Add" Buttons

**Try:**
```bash
# Stop and restart server
lsof -ti:5000 | xargs kill -9
./run_web.sh

# Hard refresh browser
Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
```

**Check Console:**
- Open browser dev tools (F12)
- Look for JavaScript errors in Console tab
- Check Network tab for failed API calls

### 2. "Add" Button Clicks Don't Work

**Symptoms:** Buttons appear but clicking does nothing

**Try:**
- Check browser console for errors (F12)
- Verify server is running: `lsof -i :5000`
- Check logs: `tail -f logs/web.log`

**Test API directly:**
```bash
curl -X POST http://localhost:5000/api/basket/add \
  -H "Content-Type: application/json" \
  -d '{
    "items": [{
      "item_id": "milk_1l",
      "item_name": "Test Item",
      "quantity": 1,
      "score": 50
    }]
  }'
```

### 3. Items Show as "Unavailable"

**Symptoms:** Items have strikethrough text and red badge

**This should not happen in test mode anymore**, but if it does:
```bash
# Verify code fix is applied
grep -A5 "Always set to available" swiggy_analyzer/web/app.py

# Should see: rec.available = True
```

### 4. Basket Panel Shows "Test Mode" Message

**This is normal!** In test mode (without real Swiggy MCP):
- Items are added to a simulated basket
- Toast shows "Test mode - items not actually added to Swiggy basket"
- This is expected behavior

**To use real basket:**
1. Authenticate: `.venv/bin/swiggy-analyzer auth login`
2. Restart server
3. Items will now add to real Swiggy basket

### 5. Recommendations Panel is Empty

**Possible causes:**
- Min score slider set too high
- No test data loaded

**Try:**
```bash
# Lower min score slider to 30-40
# Or create more test data
.venv/bin/python create_test_data.py

# Refresh recommendations
Click "Refresh" button in UI
```

### 6. Server Won't Start

**Error: "Address already in use"**
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Start server
./run_web.sh
```

**Error: "Module not found"**
```bash
# Reinstall dependencies
.venv/bin/pip install -r requirements.txt

# Install Flask specifically
.venv/bin/pip install flask
```

### 7. Browser Shows "Connection Refused"

**Check server is running:**
```bash
lsof -i :5000
# Should show Python process

# Check logs
tail -f logs/web.log
# Should see "Running on http://127.0.0.1:5000"
```

### 8. Changes Not Appearing After Code Edit

**Clear Python cache and restart:**
```bash
# Stop server
lsof -ti:5000 | xargs kill -9

# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null

# Restart
./run_web.sh

# Hard refresh browser
Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
```

---

## Testing the Fix

### Quick Test Script

```bash
# 1. Test API returns available items
curl -s 'http://localhost:5000/api/recommendations?min_score=50' | \
  python3 -c "import sys, json; \
  data = json.load(sys.stdin); \
  recs = data['recommendations'][:3]; \
  print('Top 3 items:'); \
  [print(f'  {r[\"item_name\"]}: available={r[\"available\"]}') for r in recs]"

# Expected output:
# Top 3 items:
#   Tomatoes (500g): available=True
#   Bananas (1 kg): available=True
#   Bread Whole Wheat: available=True
```

### Manual UI Test

1. ✅ Open http://localhost:5000
2. ✅ See recommendations with scores
3. ✅ See green "Add" buttons on each item
4. ✅ See "Add All Available Items" button
5. ✅ Click "Add" - toast notification appears
6. ✅ Basket panel updates with added item
7. ✅ Click "Add All" - multiple items added
8. ✅ Toast shows success message

---

## Debug Mode

### Enable Detailed Logging

Edit `swiggy_analyzer/web/app.py`:
```python
# At the top, add:
import logging
logging.basicConfig(level=logging.DEBUG)

# Or in Flask config:
app.config['DEBUG'] = True
```

### View Real-time Logs
```bash
tail -f logs/web.log
```

### Browser Developer Tools
1. Press F12 to open dev tools
2. **Console Tab**: See JavaScript errors
3. **Network Tab**: See API requests/responses
4. **Elements Tab**: Inspect HTML structure

---

## When to Contact Support

If issue persists after trying above:

1. **Collect Information:**
   ```bash
   # Server status
   lsof -i :5000

   # Recent logs
   tail -50 logs/web.log

   # Test data status
   sqlite3 data/swiggy.db "SELECT COUNT(*) FROM orders"
   ```

2. **Browser console errors** (F12 → Console tab)

3. **Screenshot** of the issue

4. **Steps to reproduce**

---

## Related Files

- **Web App**: `swiggy_analyzer/web/app.py`
- **Frontend**: `swiggy_analyzer/web/static/js/app.js`
- **Template**: `swiggy_analyzer/web/templates/index.html`
- **Logs**: `logs/web.log`
- **Database**: `data/swiggy.db`

---

## Summary

**Issue**: No "Add" buttons visible
**Fix**: Updated server to mark items as available in test mode
**Status**: ✅ Fixed and deployed
**Action**: Refresh your browser to see the fix

---

Last Updated: Feb 2, 2026

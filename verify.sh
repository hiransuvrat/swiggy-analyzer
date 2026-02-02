#!/bin/bash
# Verification script for Swiggy Analyzer installation

echo "=========================================="
echo "Swiggy Analyzer - Installation Verification"
echo "=========================================="
echo ""

ERRORS=0

# Check Python
echo "✓ Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "  Found: $PYTHON_VERSION"
else
    echo "  ✗ Python 3 not found"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check directory structure
echo "✓ Checking project structure..."
REQUIRED_DIRS=(
    "swiggy_analyzer"
    "swiggy_analyzer/auth"
    "swiggy_analyzer/mcp"
    "swiggy_analyzer/data"
    "swiggy_analyzer/analysis"
    "swiggy_analyzer/basket"
    "swiggy_analyzer/scheduler"
    "swiggy_analyzer/config"
    "swiggy_analyzer/cli"
    "tests"
    "data"
    "logs"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "  ✓ $dir"
    else
        echo "  ✗ $dir (missing)"
        ERRORS=$((ERRORS + 1))
    fi
done
echo ""

# Check required files
echo "✓ Checking required files..."
REQUIRED_FILES=(
    "requirements.txt"
    "setup.py"
    "pyproject.toml"
    "config.yaml"
    "README.md"
    "swiggy_analyzer/data/schema.sql"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (missing)"
        ERRORS=$((ERRORS + 1))
    fi
done
echo ""

# Check Python modules
echo "✓ Checking Python modules..."
MODULES=(
    "swiggy_analyzer/__init__.py"
    "swiggy_analyzer/auth/oauth_manager.py"
    "swiggy_analyzer/auth/token_store.py"
    "swiggy_analyzer/mcp/client.py"
    "swiggy_analyzer/mcp/endpoints.py"
    "swiggy_analyzer/data/models.py"
    "swiggy_analyzer/data/repository.py"
    "swiggy_analyzer/analysis/pattern_detector.py"
    "swiggy_analyzer/analysis/scoring.py"
    "swiggy_analyzer/analysis/predictor.py"
    "swiggy_analyzer/basket/manager.py"
    "swiggy_analyzer/basket/formatter.py"
    "swiggy_analyzer/scheduler/cron_manager.py"
    "swiggy_analyzer/config/settings.py"
    "swiggy_analyzer/cli/main.py"
    "swiggy_analyzer/cli/commands.py"
)

for module in "${MODULES[@]}"; do
    if [ -f "$module" ]; then
        echo "  ✓ $module"
    else
        echo "  ✗ $module (missing)"
        ERRORS=$((ERRORS + 1))
    fi
done
echo ""

# Check if virtual environment exists
echo "✓ Checking virtual environment..."
if [ -d ".venv" ]; then
    echo "  ✓ Virtual environment exists"

    if [ -f ".venv/bin/python" ]; then
        echo "  ✓ Python executable found"
    else
        echo "  ✗ Python executable not found in venv"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "  ⚠ Virtual environment not created yet"
    echo "    Run: python3 -m venv .venv"
fi
echo ""

# Check if package is installed
echo "✓ Checking package installation..."
if [ -f ".venv/bin/swiggy-analyzer" ]; then
    echo "  ✓ swiggy-analyzer CLI installed"
else
    echo "  ⚠ Package not installed yet"
    echo "    Run: pip install -e ."
fi
echo ""

# Summary
echo "=========================================="
if [ $ERRORS -eq 0 ]; then
    echo "✓ All checks passed!"
    echo ""
    echo "Next steps:"
    echo "1. Create virtual environment: python3 -m venv .venv"
    echo "2. Activate: source .venv/bin/activate"
    echo "3. Install: pip install -e ."
    echo "4. Authenticate: swiggy-analyzer auth login"
else
    echo "✗ Found $ERRORS error(s)"
    echo "Please check the missing files/directories above"
fi
echo "=========================================="

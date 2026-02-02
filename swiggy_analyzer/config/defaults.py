"""Default configuration values."""

import os
from pathlib import Path


# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Default configuration
DEFAULT_CONFIG = {
    "analysis": {
        "min_score": 50.0,
        "max_items": 20,
        "weights": {
            "frequency": 0.40,
            "recency": 0.40,
            "quantity": 0.20,
        },
    },
    "sync": {
        "auto_sync": True,
        "incremental_days": 30,
        "full_sync_days": 365,
    },
    "basket": {
        "preview_required": True,
        "auto_add": False,
    },
    "schedule": {
        "enabled": False,
        "hour": 9,
        "minute": 0,
    },
    "storage": {
        "db_path": str(PROJECT_ROOT / "data" / "swiggy.db"),
    },
    "logging": {
        "level": "INFO",
        "file": str(PROJECT_ROOT / "logs" / "swiggy_analyzer.log"),
    },
    "mcp": {
        "base_url": "https://mcp.swiggy.com/im",
        "timeout": 30,
        "retry_attempts": 3,
        "rate_limit": 100,
    },
}

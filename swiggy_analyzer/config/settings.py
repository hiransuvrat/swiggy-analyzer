"""Configuration management."""

import yaml
from pathlib import Path
from typing import Any, Optional

from loguru import logger

from .defaults import DEFAULT_CONFIG, PROJECT_ROOT


class Settings:
    """Configuration manager."""

    def __init__(self, config_path: Optional[str] = None):
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = PROJECT_ROOT / "config.yaml"

        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from file, create with defaults if not exists."""
        if not self.config_path.exists():
            logger.info(f"Config file not found, creating with defaults: {self.config_path}")
            self._create_default_config()
            return DEFAULT_CONFIG.copy()

        try:
            with open(self.config_path, "r") as f:
                config = yaml.safe_load(f)

            # Merge with defaults (in case new keys were added)
            merged = self._deep_merge(DEFAULT_CONFIG.copy(), config)
            return merged

        except Exception as e:
            logger.error(f"Failed to load config: {e}, using defaults")
            return DEFAULT_CONFIG.copy()

    def _create_default_config(self):
        """Create default configuration file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.config_path, "w") as f:
            yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False, sort_keys=False)

        logger.info(f"Created default config at {self.config_path}")

    def _deep_merge(self, base: dict, override: dict) -> dict:
        """Deep merge two dictionaries."""
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key.

        Examples:
            settings.get("analysis.min_score")
            settings.get("mcp.base_url")
        """
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """
        Set configuration value by dot-notation key.

        Examples:
            settings.set("analysis.min_score", 60)
        """
        keys = key.split(".")
        config = self.config

        # Navigate to parent
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Set value
        config[keys[-1]] = value
        logger.info(f"Set config: {key} = {value}")

    def save(self):
        """Save configuration to file."""
        try:
            with open(self.config_path, "w") as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)

            logger.info(f"Saved config to {self.config_path}")

        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            raise

    def get_db_path(self) -> str:
        """Get database path."""
        return self.get("storage.db_path")

    def get_mcp_base_url(self) -> str:
        """Get MCP base URL."""
        return self.get("mcp.base_url")

    def get_log_file(self) -> str:
        """Get log file path."""
        return self.get("logging.file")

    def get_log_level(self) -> str:
        """Get log level."""
        return self.get("logging.level")

"""Scheduler manager for macOS launchd."""

import os
import subprocess
from pathlib import Path
from typing import Optional

from loguru import logger


class ScheduleManager:
    """Manages scheduled execution via macOS launchd."""

    PLIST_NAME = "com.swiggy.analyzer.plist"

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.plist_path = Path.home() / "Library" / "LaunchAgents" / self.PLIST_NAME
        self.venv_python = self.project_root / ".venv" / "bin" / "python"
        self.script_path = self.project_root / "swiggy_analyzer" / "cli" / "main.py"
        self.log_path = self.project_root / "logs" / "swiggy_analyzer.log"

    def _generate_plist(self, hour: int, minute: int) -> str:
        """Generate launchd plist XML."""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.swiggy.analyzer</string>

    <key>ProgramArguments</key>
    <array>
        <string>{self.venv_python}</string>
        <string>{self.script_path}</string>
        <string>analyze</string>
        <string>run</string>
    </array>

    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>{hour}</integer>
        <key>Minute</key>
        <integer>{minute}</integer>
    </dict>

    <key>StandardOutPath</key>
    <string>{self.log_path}</string>

    <key>StandardErrorPath</key>
    <string>{self.log_path}</string>

    <key>RunAtLoad</key>
    <false/>

    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
"""

    def enable_schedule(self, hour: int, minute: int) -> bool:
        """
        Enable scheduled execution.

        Args:
            hour: Hour (0-23)
            minute: Minute (0-59)

        Returns:
            bool: True if successful
        """
        if not 0 <= hour <= 23:
            raise ValueError("Hour must be between 0 and 23")
        if not 0 <= minute <= 59:
            raise ValueError("Minute must be between 0 and 59")

        try:
            # Create LaunchAgents directory if it doesn't exist
            self.plist_path.parent.mkdir(parents=True, exist_ok=True)

            # Generate and write plist
            plist_content = self._generate_plist(hour, minute)
            with open(self.plist_path, "w") as f:
                f.write(plist_content)

            logger.info(f"Created plist at {self.plist_path}")

            # Load with launchd
            subprocess.run(
                ["launchctl", "load", str(self.plist_path)],
                check=True,
                capture_output=True,
            )

            logger.info(f"Enabled schedule: daily at {hour:02d}:{minute:02d}")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to load plist: {e.stderr.decode()}")
            return False

        except Exception as e:
            logger.error(f"Failed to enable schedule: {e}")
            return False

    def disable_schedule(self) -> bool:
        """
        Disable scheduled execution.

        Returns:
            bool: True if successful
        """
        try:
            # Unload from launchd
            if self.is_enabled():
                subprocess.run(
                    ["launchctl", "unload", str(self.plist_path)],
                    check=True,
                    capture_output=True,
                )
                logger.info("Unloaded schedule from launchd")

            # Remove plist file
            if self.plist_path.exists():
                self.plist_path.unlink()
                logger.info(f"Removed plist file: {self.plist_path}")

            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to unload plist: {e.stderr.decode()}")
            return False

        except Exception as e:
            logger.error(f"Failed to disable schedule: {e}")
            return False

    def is_enabled(self) -> bool:
        """Check if schedule is currently enabled."""
        if not self.plist_path.exists():
            return False

        try:
            # Check if loaded in launchd
            result = subprocess.run(
                ["launchctl", "list"],
                check=True,
                capture_output=True,
                text=True,
            )

            return "com.swiggy.analyzer" in result.stdout

        except Exception:
            return False

    def get_schedule_info(self) -> Optional[dict]:
        """Get current schedule information."""
        if not self.plist_path.exists():
            return None

        try:
            import plistlib
            with open(self.plist_path, "rb") as f:
                plist = plistlib.load(f)

            interval = plist.get("StartCalendarInterval", {})

            return {
                "enabled": self.is_enabled(),
                "hour": interval.get("Hour"),
                "minute": interval.get("Minute"),
            }

        except Exception as e:
            logger.error(f"Failed to read schedule info: {e}")
            return None

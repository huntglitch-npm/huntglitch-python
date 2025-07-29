"""
Configuration management for HuntGlitch logger.
"""

import os
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


class Config:
    """Configuration manager for HuntGlitch logger."""

    # Environment variable names
    PROJECT_KEY_VARS = ["PROJECT_KEY", "HUNTGLITCH_PROJECT_KEY"]
    DELIVERABLE_KEY_VARS = ["DELIVERABLE_KEY", "HUNTGLITCH_DELIVERABLE_KEY"]

    def __init__(self):
        self.project_key: Optional[str] = None
        self.deliverable_key: Optional[str] = None
        self._load_config()

    def _load_config(self):
        """Load configuration from environment variables."""
        # Try multiple environment variable names
        for var_name in self.PROJECT_KEY_VARS:
            self.project_key = os.getenv(var_name)
            if self.project_key:
                break

        for var_name in self.DELIVERABLE_KEY_VARS:
            self.deliverable_key = os.getenv(var_name)
            if self.deliverable_key:
                break

    @staticmethod
    def load_env_file(env_file_path: Optional[str] = None) -> bool:
        """
        Load environment variables from .env file.

        Args:
            env_file_path: Path to .env file. If None, searches standard locations.

        Returns:
            bool: True if file was loaded successfully
        """
        if not DOTENV_AVAILABLE:
            return False

        if env_file_path:
            env_path = Path(env_file_path)
            if env_path.exists():
                load_dotenv(env_path)
                return True
            return False

        # Search standard locations
        search_paths = [
            Path.cwd() / '.env',
            Path.cwd() / '.env.local',
            Path.cwd() / '.huntglitch.env',
            Path.home() / '.huntglitch.env',
            Path(__file__).parent.parent / '.env',
        ]

        for env_path in search_paths:
            if env_path.exists():
                load_dotenv(env_path)
                return True

        return False

    def is_configured(self) -> bool:
        """Check if all required configuration is available."""
        return bool(self.project_key and self.deliverable_key)

    def get_missing_config(self) -> list:
        """Get list of missing configuration variables."""
        missing = []
        if not self.project_key:
            missing.append("PROJECT_KEY")
        if not self.deliverable_key:
            missing.append("DELIVERABLE_KEY")
        return missing


# Global config instance
config = Config()

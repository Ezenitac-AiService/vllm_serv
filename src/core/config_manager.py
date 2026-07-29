import os
import json
import tempfile
from typing import Dict, Any, Optional

class ConfigManager:
    """Manages system configuration with same-directory atomic replace, chmod 0600, and memory caching."""

    DEFAULT_CONFIG = {
        "current_model": "qwen3.5-4b",
        "current_n_ctx": 4096,
        "available_presets": ["gemma4-e2b", "gemma4-e4b", "gemma4-12b", "qwen3.5-2b", "qwen3.5-4b", "qwen3.5-9b"]
    }

    def __init__(self, config_path: str = "config/model_config.json"):
        self.config_path = config_path
        self._cache: Optional[Dict[str, Any]] = None
        self._ensure_config_exists()

    def _ensure_config_exists(self) -> None:
        dir_name = os.path.dirname(self.config_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        if not os.path.exists(self.config_path):
            self.save_config(self.DEFAULT_CONFIG)

    def get_config(self) -> dict:
        """Returns cached configuration if available, otherwise reads from file."""
        if self._cache is not None:
            return self._cache.copy()

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                self._cache = config
                return config.copy()
        except Exception:
            return self.DEFAULT_CONFIG.copy()

    def save_config(self, config: dict) -> None:
        """Saves configuration using same-directory atomic replace and chmod 0600 permissions."""
        self._write_atomic(config)
        self._cache = config.copy()

    def _write_atomic(self, config: dict) -> None:
        """FR-003 & FR-008: Writes config to temp file in SAME dir with chmod 0600 and os.replace."""
        target_dir = os.path.dirname(self.config_path) or "."
        os.makedirs(target_dir, exist_ok=True)

        # Create temporary file in the EXACT same directory to prevent EXDEV cross-device mount errors
        with tempfile.NamedTemporaryFile("w", dir=target_dir, delete=False, encoding="utf-8") as tf:
            temp_name = tf.name
            json.dump(config, tf, indent=4)
            tf.flush()
            os.fsync(tf.fileno())

        try:
            # FR-008: Enforce owner-only read/write permissions for security
            os.chmod(temp_name, 0o600)
            # POSIX atomic swap
            os.replace(temp_name, self.config_path)
        except Exception:
            if os.path.exists(temp_name):
                os.remove(temp_name)
            raise

    def update_config(self, **kwargs) -> dict:
        current = self.get_config()
        current.update(kwargs)
        self.save_config(current)
        return current.copy()

    def invalidate_cache(self) -> None:
        """Explicitly invalidates memory cache."""
        self._cache = None

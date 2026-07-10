import os
import json

class ConfigManager:
    DEFAULT_CONFIG = {
        "current_model": None,
        "current_n_ctx": 4096
    }

    def __init__(self, config_path: str = "config/model_config.json"):
        self.config_path = config_path
        self._ensure_config_exists()

    def _ensure_config_exists(self):
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        if not os.path.exists(self.config_path):
            self.save_config(self.DEFAULT_CONFIG)

    def get_config(self) -> dict:
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return self.DEFAULT_CONFIG.copy()

    def save_config(self, config: dict):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

    def update_config(self, **kwargs):
        current = self.get_config()
        current.update(kwargs)
        self.save_config(current)

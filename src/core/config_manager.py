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

    # -------------------------------------------------------------------------
    # FR-008: Model Catalog JSON 외부화 로더
    # -------------------------------------------------------------------------
    _model_catalog_cache: Optional[Dict[str, Any]] = None

    def get_model_catalog(self) -> Dict[str, Any]:
        """FR-008: config/model_catalog.json에서 모델 카탈로그를 로드하고 캐싱합니다.

        JSON 파일이 없거나 파싱 에러 발생 시 빈 딕셔너리를 반환합니다.
        """
        if self._model_catalog_cache is not None:
            return self._model_catalog_cache.copy()

        catalog_path = os.path.join(os.path.dirname(self.config_path), "model_catalog.json")
        try:
            with open(catalog_path, "r", encoding="utf-8") as f:
                catalog = json.load(f)
            self._model_catalog_cache = catalog
            return catalog.copy()
        except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
            print(f"[ConfigManager] ⚠️ model_catalog.json 로드 실패 (fallback 사용): {e}")
            self._model_catalog_cache = {}
            return {}

    # -------------------------------------------------------------------------
    # FR-009 / FR-010: Server Config JSON 외부화 로더 (환경변수 오버라이드 지원)
    # -------------------------------------------------------------------------
    _server_config_cache: Optional[Dict[str, Any]] = None

    DEFAULT_SERVER_CONFIG = {
        "port": 8081,
        "host": "127.0.0.1",
        "healthcheck_timeout_s": 120,
        "connection_pool": {
            "max_keepalive_connections": 20,
            "max_connections": 100
        },
        "vram_max_capacity_mb": 11264,
        "graceful_drain_timeout_s": 5.0
    }

    def get_server_config(self) -> Dict[str, Any]:
        """FR-009/FR-010: config/server_config.json에서 서버 설정을 로드합니다.

        환경변수 LLAMA_PORT, LLAMA_HOST가 설정되어 있으면 JSON 값을 오버라이드합니다.
        JSON 파일이 없거나 파싱 에러 발생 시 내장 기본값(DEFAULT_SERVER_CONFIG)을 반환합니다.
        """
        if self._server_config_cache is not None:
            return self._server_config_cache.copy()

        server_config_path = os.path.join(os.path.dirname(self.config_path), "server_config.json")
        try:
            with open(server_config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
            print(f"[ConfigManager] ⚠️ server_config.json 로드 실패 (기본값 사용): {e}")
            config = self.DEFAULT_SERVER_CONFIG.copy()

        # FR-009: 환경변수 오버라이드 적용
        env_port = os.environ.get("LLAMA_PORT")
        if env_port is not None:
            try:
                config["port"] = int(env_port)
            except ValueError:
                pass

        env_host = os.environ.get("LLAMA_HOST")
        if env_host is not None:
            config["host"] = env_host

        self._server_config_cache = config
        return config.copy()

    def invalidate_all_caches(self) -> None:
        """모든 설정 캐시를 무효화합니다."""
        self._cache = None
        self._model_catalog_cache = None
        self._server_config_cache = None

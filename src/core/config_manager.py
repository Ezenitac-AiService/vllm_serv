import os
import json
import tempfile
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, field_validator

class ConnectionPoolConfig(BaseModel):
    max_keepalive_connections: int = 20
    max_connections: int = 100

class ServerConfig(BaseModel):
    """FR-002 & FR-008: Pydantic v2 기반 서버 설정 규격."""
    host: str = "127.0.0.1"
    port: int = 8081
    backend_port: int = 8089
    allowed_subnets: List[str] = Field(default_factory=lambda: ["127.0.0.1", "192.168.0.0/24"])
    vram_limit_mb: int = 11264
    vram_max_capacity_mb: int = 11264
    healthcheck_timeout_s: int = 120
    graceful_drain_timeout_s: float = 5.0
    connection_pool: ConnectionPoolConfig = Field(default_factory=ConnectionPoolConfig)

    @field_validator("port", "backend_port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not (1024 <= v <= 65535):
            raise ValueError(f"Port must be between 1024 and 65535, got {v}")
        return v

class ModelCatalogEntry(BaseModel):
    """FR-001: Pydantic v2 기반 단일 모델 명세 규격."""
    name: str
    repo_id: str
    filename: str
    clip_filename: Optional[str] = None
    target_dir: str
    model_path: str
    clip_path: Optional[str] = None
    chat_template: Optional[str] = None
    default_n_ctx: int = 4096
    vram_est_mb: int
    requires_mmproj: bool = False
    quant_type: str
    size_gb: float

class ConfigManager:
    """Manages system configuration with same-directory atomic replace, chmod 0600, Pydantic v2 validation, and memory caching."""

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

        with tempfile.NamedTemporaryFile("w", dir=target_dir, delete=False, encoding="utf-8") as tf:
            temp_name = tf.name
            json.dump(config, tf, indent=4)
            tf.flush()
            os.fsync(tf.fileno())

        try:
            os.chmod(temp_name, 0o600)
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
    # FR-001: Model Catalog JSON 외부화 및 Pydantic 검증 로더
    # -------------------------------------------------------------------------
    _model_catalog_cache: Optional[Dict[str, Any]] = None

    def get_model_catalog(self) -> Dict[str, Any]:
        """FR-001: config/model_catalog.json에서 모델 카탈로그를 로드하고 캐싱합니다."""
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
    # FR-002: Server Config JSON 외부화 및 Pydantic v2 로더
    # -------------------------------------------------------------------------
    _server_config_cache: Optional[Dict[str, Any]] = None

    def get_server_config(self) -> Dict[str, Any]:
        """FR-002: config/server_config.json에서 Pydantic v2 기반 서버 설정을 로드합니다.

        환경변수 LLAMA_PORT, LLAMA_HOST가 설정되어 있으면 JSON 값을 오버라이드합니다.
        """
        if self._server_config_cache is not None:
            return self._server_config_cache.copy()

        server_config_path = os.path.join(os.path.dirname(self.config_path), "server_config.json")
        raw_config = {}
        try:
            with open(server_config_path, "r", encoding="utf-8") as f:
                raw_config = json.load(f)
        except Exception as e:
            print(f"[ConfigManager] ⚠️ server_config.json 로드 실패 (기본값 사용): {e}")

        try:
            parsed_cfg = ServerConfig(**raw_config)
            config = parsed_cfg.model_dump()
        except Exception as e:
            print(f"[ConfigManager] ⚠️ ServerConfig Pydantic 파싱 경고 (기본 설정 사용): {e}")
            config = ServerConfig().model_dump()

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

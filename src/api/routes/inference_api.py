"""
OpenAI-compatible inference routing and proxy handlers (FR-001, FR-005, FR-007, FR-009).
Provides GET /v1/models catalog listing and reverse-proxying for RAG/Agent requests.
"""

import time
from typing import Any, AsyncGenerator
import httpx
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from src.core.llama_manager import llama_manager
from src.core.config_manager import ConfigManager
from src.core.model_downloader import ModelDownloader

router = APIRouter()


def _get_llama_server_config() -> tuple[int, str]:
    """FR-009: 백엔드 LLM 엔진 포트 및 호스트를 config/server_config.json 또는 환경변수에서 동적 로드."""
    try:
        cm = ConfigManager()
        server_cfg = cm.get_server_config()
        port = server_cfg.get("backend_port", 8089)
        host = server_cfg.get("host", "127.0.0.1")
        return port, host
    except Exception:
        return 8089, "127.0.0.1"


_port, _host = _get_llama_server_config()
LLAMA_SERVER_PORT = _port
LLAMA_SERVER_URL = f"http://{_host}:{LLAMA_SERVER_PORT}"


def _build_default_client() -> httpx.AsyncClient:
    """FR-005 & FR-009: 커넥션 풀 설정을 config/server_config.json에서 동적 로드하여 싱글톤 구성."""
    try:
        cm = ConfigManager()
        server_cfg = cm.get_server_config()
        pool_cfg = server_cfg.get("connection_pool", {})
        max_keepalive = pool_cfg.get("max_keepalive_connections", 20)
        max_conn = pool_cfg.get("max_connections", 100)
    except Exception:
        max_keepalive = 20
        max_conn = 100

    return httpx.AsyncClient(
        base_url=LLAMA_SERVER_URL,
        limits=httpx.Limits(max_keepalive_connections=max_keepalive, max_connections=max_conn),
        timeout=None
    )


_default_client = _build_default_client()


async def check_llama_status() -> bool:
    """Check if the backend LLM engine is ready to accept requests."""
    return llama_manager.is_ready()


def _get_http_client(request: Request) -> httpx.AsyncClient:
    """Helper to retrieve singleton AsyncClient from app.state or fallback."""
    if hasattr(request.app.state, "http_client") and request.app.state.http_client:
        return request.app.state.http_client
    return _default_client


@router.get("/v1/models")
async def list_models(request: Request) -> dict[str, Any]:
    """FR-001 & FR-007: OpenAI API 표준 GET /v1/models 동적 모델 카탈로그 엔드포인트.
    
    ConfigManager 기반 전체 지원 모델 정보, 다운로드 상태, 현재 활성화 여부를
    OpenAI 규격 JSON ({"object": "list", "data": [...]})으로 동적 반환합니다.
    """
    cm = ConfigManager()
    catalog = cm.get_model_catalog()
    downloader = ModelDownloader(config_manager=cm)
    
    current_model = None
    try:
        cfg = llama_manager.config_manager.get_config()
        current_model = cfg.get("current_model")
    except Exception:
        pass

    created_ts = int(time.time())
    models_data = []
    for model_id, entry in catalog.items():
        is_available = downloader.is_model_available(model_id)
        is_active = (current_model == model_id and llama_manager.is_ready())
        models_data.append({
            "id": model_id,
            "object": "model",
            "created": created_ts,
            "owned_by": "llm-server",
            "permission": [],
            "is_available": is_available,
            "is_active": is_active,
        })

    return {"object": "list", "data": models_data}


@router.api_route("/v1/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
async def reverse_proxy(request: Request, path: str) -> StreamingResponse:
    """FR-009: RAG 및 Agent 마이크로서비스 요청을 비동기 싱글톤 커넥션 풀로 역방향 프록시 처리."""
    if path in ("chat/completions", "completions") and not await check_llama_status():
        raise HTTPException(
            status_code=503,
            detail="Model is currently loading or unloaded. Please try again later.",
            headers={"Retry-After": "10"}
        )

    client = _get_http_client(request)
    url = httpx.URL(path=request.url.path, query=request.url.query.encode("utf-8"))

    req = client.build_request(
        request.method,
        url,
        headers=request.headers.raw,
        content=request.stream()
    )

    try:
        r = await client.send(req, stream=True)
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="Model server is currently unreachable. Please try again later.",
            headers={"Retry-After": "10"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    async def stream_generator() -> AsyncGenerator[bytes, None]:
        """RAG 및 Agent 마이크로서비스 전용 SSE 스트리밍 제너레이터."""
        try:
            async for chunk in r.aiter_raw():
                if await request.is_disconnected():
                    break
                yield chunk
        finally:
            await r.aclose()

    return StreamingResponse(
        stream_generator(),
        status_code=r.status_code,
        headers=r.headers
    )

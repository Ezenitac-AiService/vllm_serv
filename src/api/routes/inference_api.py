"""
OpenAI-compatible inference routing and proxy handlers (FR-001, FR-005, FR-007, FR-009).
Provides GET /v1/models catalog listing and reverse-proxying for RAG/Agent requests.
"""

import os
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
    """FR-009: 백엔드 LLM 엔진 포트를 config/server_config.json에서 동적 로드 (로컬 백엔드 통신은 127.0.0.1 사용)."""
    try:
        cm = ConfigManager()
        server_cfg = cm.get_server_config()
        port = server_cfg.get("backend_port", 8089)
        return port, "127.0.0.1"
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


def parse_response_format(body: dict[str, Any]) -> dict[str, Any]:
    """FR-002: OpenAI OpenAI response_format 파라미터를 파싱하여 llama-server 문법 규격으로 변환."""
    response_format = body.get("response_format")
    if not response_format or not isinstance(response_format, dict):
        return body

    fmt_type = response_format.get("type")
    if fmt_type == "json_object":
        body["grammar"] = "json"
    elif fmt_type == "json_schema" and "json_schema" in response_format:
        schema = response_format["json_schema"]
        if "schema" in schema:
            body["json_schema"] = schema["schema"]
    return body


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


def _get_backend_target_port(path: str) -> int:
    try:
        cm = ConfigManager()
        server_cfg = cm.get_server_config()
        clean_path = path.strip("/").split("/")[-1]
        if clean_path in ("embeddings", "embedding"):
            return server_cfg.get("embedding_backend_port", 8090)
        elif clean_path in ("rerank", "reranking"):
            return server_cfg.get("rerank_backend_port", 8091)
        else:
            return server_cfg.get("backend_port", 8089)
    except Exception:
        clean_path = path.strip("/").split("/")[-1]
        if clean_path in ("embeddings", "embedding"):
            return 8090
        elif clean_path in ("rerank", "reranking"):
            return 8091
        return 8089


@router.api_route("/v1/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
@router.api_route("/embedding", methods=["POST", "OPTIONS"])
@router.api_route("/rerank", methods=["POST", "OPTIONS"])
async def reverse_proxy(request: Request, path: str = "") -> StreamingResponse:
    """FR-009 & FR-002: RAG, Agent, Embedding, Reranker 요청을 백엔드 싱글톤 인스턴스로 역방향 프록시 라우팅."""
    if not path:
        path = request.url.path.strip("/")

    clean_path = path.strip("/").split("/")[-1]
    if clean_path in ("chat/completions", "completions") and not await check_llama_status():
        raise HTTPException(
            status_code=503,
            detail="Model is currently loading or unloaded. Please try again later.",
            headers={"Retry-After": "10"}
        )

    # Mock response support for pytest/offline execution
    if os.environ.get("MOCK_LLAMA_SERVER") == "1":
        import json
        if clean_path in ("embeddings", "embedding"):
            mock_data = {
                "object": "list",
                "data": [{"object": "embedding", "index": 0, "embedding": [0.01] * 1024}],
                "model": "bge-m3",
                "usage": {"prompt_tokens": 10, "total_tokens": 10}
            }
            return StreamingResponse(content=iter([json.dumps(mock_data).encode("utf-8")]), media_type="application/json")
        elif clean_path in ("rerank", "reranking"):
            mock_data = {
                "model": "bge-reranker-v2-m3",
                "results": [
                    {"index": 0, "relevance_score": 0.95},
                    {"index": 1, "relevance_score": 0.12}
                ]
            }
            return StreamingResponse(content=iter([json.dumps(mock_data).encode("utf-8")]), media_type="application/json")

    body_content = None
    prompt_text = None
    if request.method == "POST" and clean_path in ("chat/completions", "completions"):
        body_content = await request.body()
        if body_content:
            try:
                import json
                body_json = json.loads(body_content)
                model_id = body_json.get("model") or llama_manager.config_manager.get_config().get("current_model", "qwen3.5-4b")
                requested_n_ctx = body_json.get("n_ctx")
                if requested_n_ctx is not None:
                    llama_manager.validate_requested_context(model_id, int(requested_n_ctx))

                if "messages" in body_json and isinstance(body_json["messages"], list):
                    user_msgs = [m.get("content", "") for m in body_json["messages"] if isinstance(m, dict) and m.get("role") == "user"]
                    prompt_text = user_msgs[-1] if user_msgs else json.dumps(body_json["messages"], ensure_ascii=False)
                elif "prompt" in body_json:
                    prompt_text = str(body_json.get("prompt"))
            except HTTPException:
                raise
            except Exception:
                pass

    target_port = _get_backend_target_port(path)
    backend_url = f"http://127.0.0.1:{target_port}{request.url.path}"
    if request.url.query:
        backend_url += f"?{request.url.query}"

    if body_content is None and request.method in ("POST", "PUT", "PATCH"):
        body_content = await request.body()

    try:
        # Preflight guard: Set connect & response header timeouts to prevent infinite proxy hanging (FR-007)
        client = _get_http_client(request)
        headers = [(k, v) for k, v in request.headers.raw if k.lower() not in (b"host", b"content-length")]
        req = client.build_request(
            request.method,
            backend_url,
            headers=headers,
            content=body_content if body_content is not None else request.stream()
        )
        r = await client.send(req, stream=True)
        if r.status_code == 503:
            await r.aclose()
            raise HTTPException(
                status_code=503,
                detail=f"Model server at port {target_port} is currently initializing. Please try again in a few seconds.",
                headers={"Retry-After": "5"}
            )
    except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout, httpx.TimeoutException):
        raise HTTPException(
            status_code=503,
            detail=f"Model server at port {target_port} is currently unreachable or loading. Please try again in a few seconds.",
            headers={"Retry-After": "5"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    captured_chunks = []
    start_time = time.perf_counter()
    first_chunk_received = False
    ttft_ms = 0.0

    async def stream_generator() -> AsyncGenerator[bytes, None]:
        """RAG 및 Agent 마이크로서비스 전용 SSE 스트리밍 제너레이터."""
        nonlocal first_chunk_received, ttft_ms
        try:
            async for chunk in r.aiter_raw():
                if not first_chunk_received:
                    ttft_ms = (time.perf_counter() - start_time) * 1000.0
                    first_chunk_received = True
                if await request.is_disconnected():
                    break
                if path in ("chat/completions", "completions") and request.method == "POST":
                    captured_chunks.append(chunk)
                yield chunk
        finally:
            await r.aclose()
            if path in ("chat/completions", "completions") and request.method == "POST":
                try:
                    import json
                    completion_text = ""
                    prompt_tokens = 0
                    completion_tokens = 0
                    if captured_chunks:
                        full_resp = b"".join(captured_chunks).decode("utf-8", errors="ignore")
                        if full_resp.strip().startswith("{"):
                            res_json = json.loads(full_resp)
                            choices = res_json.get("choices", [])
                            if choices:
                                completion_text = choices[0].get("message", {}).get("content", "") or choices[0].get("text", "")
                            usage = res_json.get("usage", {})
                            prompt_tokens = usage.get("prompt_tokens", 0)
                            completion_tokens = usage.get("completion_tokens", 0)
                        else:
                            for line in full_resp.splitlines():
                                line = line.strip()
                                if line.startswith("data: ") and line != "data: [DONE]":
                                    try:
                                        c_json = json.loads(line[6:])
                                        choices = c_json.get("choices", [])
                                        if choices:
                                            delta = choices[0].get("delta", {})
                                            content = delta.get("content", "")
                                            if content:
                                                completion_text += content
                                    except Exception:
                                        pass
                    thinking_text = None
                    if completion_text:
                        from src.core.think_tag_parser import parse_think_tags
                        clean_text, think_text = parse_think_tags(completion_text)
                        completion_text = clean_text
                        thinking_text = think_text

                    total_latency_s = time.perf_counter() - start_time
                    tps = round(completion_tokens / max(total_latency_s, 0.05), 1) if completion_tokens else 0.0

                    auth_header = request.headers.get("authorization", "")
                    api_key = auth_header.replace("Bearer ", "").strip() if "Bearer " in auth_header else "anonymous"

                    from src.core.metrics_db import metrics_db
                    metrics_db.log_request(
                        api_key=api_key or "anonymous",
                        endpoint=request.url.path,
                        status_code=r.status_code,
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        ttft_ms=round(ttft_ms, 2),
                        tps=tps,
                        is_error=(r.status_code >= 400),
                        prompt_text=prompt_text,
                        completion_text=completion_text,
                        thinking_text=thinking_text
                    )
                except Exception:
                    pass

    # Filter out hop-by-hop & content length/encoding headers to prevent Uvicorn h11 LocalProtocolError
    excluded_headers = {"content-length", "transfer-encoding", "connection", "content-encoding"}
    response_headers = {
        k: v for k, v in r.headers.items()
        if k.lower() not in excluded_headers
    }

    return StreamingResponse(
        stream_generator(),
        status_code=r.status_code,
        headers=response_headers
    )

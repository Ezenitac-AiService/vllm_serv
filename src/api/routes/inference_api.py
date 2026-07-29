import httpx
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask

router = APIRouter()

LLAMA_SERVER_PORT = 8081
LLAMA_SERVER_URL = f"http://127.0.0.1:{LLAMA_SERVER_PORT}"

# Fallback client for direct testing if app.state.http_client is not set
_default_client = httpx.AsyncClient(
    base_url=LLAMA_SERVER_URL,
    limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
    timeout=None
)

async def check_llama_status():
    from src.core.llama_manager import llama_manager
    return llama_manager.is_ready()

def _get_http_client(request: Request) -> httpx.AsyncClient:
    """Helper to retrieve singleton AsyncClient from app.state or fallback."""
    if hasattr(request.app.state, "http_client") and request.app.state.http_client:
        return request.app.state.http_client
    return _default_client

@router.api_route("/v1/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
async def reverse_proxy(request: Request, path: str):
    """
    Reverse proxy for /v1 requests. Forwards to the llama-server subprocess.
    Returns 503 if the server is not ready (loading, unloaded).
    """
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

    async def stream_generator():
        """FR-006 & FR-010: Streaming generator with disconnect check and try...finally aclose cleanup."""
        try:
            async for chunk in r.aiter_raw():
                if await request.is_disconnected():
                    break
                yield chunk
        finally:
            # FR-010: Prevent connection pool pollution by guaranteeing response stream closure
            await r.aclose()

    return StreamingResponse(
        stream_generator(),
        status_code=r.status_code,
        headers=r.headers
    )

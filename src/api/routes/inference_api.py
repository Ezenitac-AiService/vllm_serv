import httpx
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask
import json

router = APIRouter()

# The proxy will route to the local llama-server subprocess running on a specific port
# Default llama-server port is usually 8080, we can define it here.
LLAMA_SERVER_PORT = 8081
LLAMA_SERVER_URL = f"http://127.0.0.1:{LLAMA_SERVER_PORT}"

# Global HTTP client for proxying
client = httpx.AsyncClient(base_url=LLAMA_SERVER_URL, timeout=None)

async def check_llama_status():
    # To be implemented/imported from LlamaManager later
    # Return True if READY, False if LOADING/UNLOADED/ERROR
    from src.core.llama_manager import llama_manager
    return llama_manager.is_ready()

@router.api_route("/v1/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
async def reverse_proxy(request: Request, path: str):
    """
    Reverse proxy for /v1 requests. Forwards to the llama-server subprocess.
    Returns 503 if the server is not ready (loading, unloaded).
    """
    # Scope 503 check to inference endpoints (chat/completions, completions) per plan constraints
    if path in ("chat/completions", "completions") and not await check_llama_status():
        raise HTTPException(
            status_code=503,
            detail="Model is currently loading or unloaded. Please try again later.",
            headers={"Retry-After": "10"}
        )

    # Forward the request to llama-server
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
    
    return StreamingResponse(
        r.aiter_raw(),
        status_code=r.status_code,
        headers=r.headers,
        background=BackgroundTask(r.aclose)
    )

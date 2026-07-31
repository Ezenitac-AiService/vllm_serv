# Data Model: Inference API Reverse Proxy Content-Length Header Handling Fix (069-fix-proxy-content-length-header)

**Feature**: `069-fix-proxy-content-length-header`

## Header Filter Model Scheme

### FilteredResponseHeaders Structure
- **Inputs**: Raw `httpx.Headers` dictionary from upstream `llama-server` / `auxiliary-server` response.
- **Excluded Header Keys**:
  - `content-length`
  - `transfer-encoding`
  - `content-encoding`
  - `connection`
- **Output**: Cleaned dictionary passed directly to FastAPI `StreamingResponse(..., headers=filtered_headers)`.

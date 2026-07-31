# Implementation Plan: Inference API Reverse Proxy Content-Length Header Handling Fix (069-fix-proxy-content-length-header)

**Branch**: `069-fix-proxy-content-length-header` | **Date**: 2026-07-31 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/069-fix-proxy-content-length-header/spec.md)

**Input**: Feature specification from `specs/069-fix-proxy-content-length-header/spec.md`

## Summary

본 계획서는 `POST /v1/chat/completions` 등 역방향 프록시 요청 시 C++ 백엔드 엔진(`llama-server`)의 응답 헤더 중 `content-length`가 `StreamingResponse`로 그대로 전달되어 Uvicorn `h11` HTTP 핸들러에서 `LocalProtocolError: Too little data for declared Content-Length` 및 클라이언트 연결 조기 종료가 발생하는 결함을 해결하기 위해, `src/api/routes/inference_api.py` 내 `reverse_proxy` 반환 시 `content-length`, `transfer-encoding`, `content-encoding`, `connection` 제어 헤더를 안전하게 제외 필터링하고 검증 수트 및 회귀 테스트를 수립하는 구현 계획을 정의합니다.

## Technical Context

**Language/Version**: Python 3.11+ (FastAPI, Asyncio)

**Primary Dependencies**: FastAPI, Starlette, httpx, uvicorn, h11, pytest

**Storage**: N/A

**Testing**: Pytest (`uv run pytest tests/unit/test_inference_api_proxy_headers.py`)

**Target Platform**: Linux Server (Web Gateway & Inference Server)

**Project Type**: Async Inference Routing & API Gateway

**Performance Goals**: HTTP 200 OK 스트리밍/비스트리밍 응답 100% 정상 수신 및 프로토콜 에러 0%

**Constraints**: `uv run` 표준 준수 및 하위 호환성 유지

**Scale/Scope**: `src/api/routes/inference_api.py`, `tests/unit/test_inference_api_proxy_headers.py`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙)
- [x] 목업은 유료/제한 API로 엄격히 제한하고 실물 시스템/소켓/OS 인자 및 실제 호출 플래그(REAL_API_CALL=1) 기반 실측 검증 계획이 포함되어 있는가? (실체적 테스트 및 수렴 검증 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (비파괴적 문서 수정 원칙)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (uv 패키지 및 환경 관리 원칙)
- [x] 전체 회귀 테스트 수트 검증 계획이 포함되어 있는가? (의무적 회귀 테스트 원칙)

## Project Structure

### Documentation (this feature)

```text
specs/069-fix-proxy-content-length-header/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (/speckit-plan command output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── proxy-header-filter-contract.json
└── checklists/
    └── requirements.md  # Specification quality checklist
```

### Source Code (repository root)

```text
src/
└── api/
    └── routes/
        └── inference_api.py # Exclude hop-by-hop & content-length headers in reverse_proxy

tests/
└── unit/
    └── test_inference_api_proxy_headers.py # Unit test for proxy header filtering
```

**Structure Decision**: Standard repository layout modifying inference API route handlers and creating dedicated unit test.

## Complexity Tracking

*No violations.*

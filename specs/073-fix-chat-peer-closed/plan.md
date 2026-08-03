# Implementation Plan: Chat Completions API 커넥션 두절(peer closed connection) 오류 수정 및 파이프라인 안정화

**Branch**: `073-fix-chat-peer-closed` | **Date**: 2026-08-03 | **Spec**: [specs/073-fix-chat-peer-closed/spec.md](file:///home/dev/storage/vllm_serv/specs/073-fix-chat-peer-closed/spec.md)

**Input**: Feature specification from `/specs/073-fix-chat-peer-closed/spec.md`

## Summary

본 구현 계획서는 `vllm_serv` 플랫폼의 Chat Completions API (`/v1/chat/completions`, port 8081) 호출 시 Uvicorn ASGI 프로토콜 핸들러에서 발생하던 `h11.LocalProtocolError: Too little data for declared Content-Length` 예외를 차단하기 위한 구조적 해법을 담고 있습니다. FastAPI/Starlette 전송 레이어의 UTF-8 바이트 단위 Content-Length 계산 동기화 및 `StreamingResponse` Chunked Transfer 세이프가드를 적용하여 클라이언트 커넥션 두절 현상을 근본적으로 해결하고, 8091 포트 BGE Reranker v2 M3 데몬 구동 동기화를 완성합니다.

## Technical Context

**Language/Version**: Python 3.12 (managed via `uv`)

**Primary Dependencies**: FastAPI, Starlette, Uvicorn, h11, httpx, pydantic, llama-cpp-python

**Storage**: SQLite (`data/metrics.db` - API 사용량 및 키 메트릭 보관)

**Testing**: `uv run pytest` (pytest-asyncio, httpx test client)

**Target Platform**: Linux x86_64 (NVIDIA GeForce GTX 1070 8GB VRAM)

**Project Type**: High-performance Multi-model LLM/Embedding/Reranking Serving Web Service

**Performance Goals**: 첫 번째 토큰 응답 시간(TTFT) 지연 5% 이내 유지, 커넥션 에러율 0%

**Constraints**: Zero-Mock 준수, `uv run` 환경 격리, 헌법 II/III조 준수 (실체적 소켓 파이프라인 연동)

**Scale/Scope**: 서빙 포트 3개 (8081 Chat, 8090 Embedding, 8091 Reranker)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책 준수)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙 준수)
- [x] 목업은 유료/제한 API로 엄격히 제한하고 실물 시스템/소켓/OS 인자 및 실제 호출 플래그(REAL_API_CALL=1) 기반 실측 검증 계획이 포함되어 있는가? (실체적 테스트 및 수렴 검증 원칙 - Zero Mock 준수)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙 준수)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (비파괴적 문서 수정 원칙 준수)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (uv 패키지 및 환경 관리 원칙 준수)
- [x] 전체 회귀 테스트 수트 및 Playwright 기반 E2E 브라우저 실측 검증 계획이 포함되어 있는가? (의무적 회귀 테스트 및 브라우저 E2E 검증 원칙 준수)

## Project Structure

### Documentation (this feature)

```text
specs/073-fix-chat-peer-closed/
├── plan.md              # 이 계획서
├── research.md          # Phase 0 연구 결과 문서
├── data-model.md        # Phase 1 도메인 엔티티 모델 문서
├── quickstart.md        # Phase 1 실측 검증 가이드
├── contracts/           # Phase 1 API 계약 스키마 (chat-completion-contract.json)
└── tasks.md             # Phase 2 과제 목록 (/speckit-tasks 명령어로 수립 예정)
```

### Source Code (repository root)

```text
src/
├── api/                 # FastAPI 엔드포인트 및 라우터 (/v1/chat/completions)
├── services/            # LlamaManager, AuxiliaryManager (8081, 8090, 8091 서빙)
├── core/                # ASGI 미들웨어, 스트리밍 파이프라인 및 Content-Length 세이프가드
└── models/              # Pydantic 스키마 및 DTO

samples/                 # 실측 예제 스크립트 (sample_01 ~ sample_05)
tests/                   # 실체적 회귀 및 통합 테스트 수트 (uv run pytest)
```

**Structure Decision**: 기존 `vllm_serv` 단일 레포지토리 구조(`src/`, `samples/`, `tests/`)를 활용하여 핵심 프록시 및 API 응답 파이프라인 버그를 수정하고 통합 수렴 검증합니다.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*(위반 사항 없음 - 헌법 7대 원칙 100% 준수)*

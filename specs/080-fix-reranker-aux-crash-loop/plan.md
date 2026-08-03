# Implementation Plan: 보조 모델 크래시 루프 방지 및 프록시 503 게이트 (`080-fix-reranker-aux-crash-loop`)

**Branch**: `080-fix-reranker-aux-crash-loop` | **Date**: 2026-08-03 | **Spec**: [`spec.md`](file:///home/dev/storage/vllm_serv/specs/080-fix-reranker-aux-crash-loop/spec.md)

**Input**: Feature specification from `/specs/080-fix-reranker-aux-crash-loop/spec.md`

## Summary

`vllm_serv` 서버 구동 시 GTX 1070 (8GB VRAM) 등 VRAM 제약 플랫폼에서 보조 모델(Embedding `bge-m3`, Reranker `bge-reranker-v2-m3`)이 구동 직후 OOM으로 반복 크래시하여 무한 재시작 루프에 빠지고, 역방향 프록시가 READY 미도달 포트로 요청을 전달하여 404 Not Found가 발생하는 근본 원인을 해결합니다.

**기술적 해결 방안**:
1. `_crash_recovery_loop` 서킷 브레이커: 연속 크래시 카운터(최대 3회) 도입 및 초과 시 `ProcessStatusEnum.DISABLED` 상태 전이
2. 보조 모델 순차 초기화: `start_auto_startup_and_recovery()`에서 Embedding 완료 후 Reranker를 순차 시작하여 동시 피크 VRAM 방지
3. 역방향 프록시 READY 게이트: `reverse_proxy`에서 `ensure_*_resident` 결과가 `READY`일 때만 백엔드로 포워딩하고, `DISABLED` 또는 미READY 상태 시 즉시 `HTTP 503 Service Unavailable` 반환 (404 원천 차단)

## Technical Context

**Language/Version**: Python 3.10+ (uv managed)

**Primary Dependencies**: FastAPI, Uvicorn, httpx, asyncio

**Storage**: SQLite (`data/metrics.db`), Local JSON Config (`config/server_config.json`, `config/model_catalog.json`)

**Testing**: pytest (`uv run pytest`), pytest-asyncio

**Target Platform**: Linux (x86_64, NVIDIA GPU: GTX 1070 8GB, GTX 1080 Ti 11GB, RTX 3060 12GB)

**Project Type**: Python Web Service (FastAPI Proxy + Subprocess Manager)

**Performance Goals**: 프록시 게이트 오버헤드 < 1ms, DISABLED 상태 시 즉시 503 반환 (< 2ms)

**Constraints**: Zero Mock 프로덕션 코드, 100% Real Verification, VRAM 8GB 플랫폼에서 보조 모델 크래시 루프 0건

**Scale/Scope**: 3개 플랫폼 프로필 support (`legacy-i7-930-gtx1070`, `pascal-avx2-gtx1080ti`, `dev-rtx3060`)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙)
- [x] 목업은 유료/제한 API로 엄격히 제한하고 실물 시스템/소켓/OS 인자 및 실제 호출 플래그(REAL_API_CALL=1) 기반 실측 검증 계획이 포함되어 있는가? (실체적 테스트 및 수렴 검증 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (비파괴적 문서 수정 원칙)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (uv 패키지 및 환경 관리 원칙)
- [x] 전체 회귀 테스트 수트 및 Playwright 기반 E2E 브라우저 실측 검증 계획이 포함되어 있는가? (의무적 회귀 테스트 및 브라우저 E2E 검증 원칙)

## Project Structure

### Documentation (this feature)

```text
specs/080-fix-reranker-aux-crash-loop/
├── spec.md              # Feature Specification
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 research artifact
├── data-model.md        # Phase 1 data model & state transition artifact
├── quickstart.md        # Phase 1 validation guide
├── contracts/           # Phase 1 API contract artifact
│   └── auxiliary-response-contract.json
└── checklists/
    └── requirements.md  # Spec quality checklist
```

### Source Code (repository root)

```text
src/
├── core/
│   ├── process_manager.py     # ProcessStatusEnum.DISABLED 추가
│   └── auxiliary_manager.py   # 연속 크래시 카운터, 순차 초기화, 서킷 브레이커
└── api/
    └── routes/
        └── inference_api.py   # reverse_proxy READY 게이트 및 DISABLED 503 반환

tests/
├── unit/
│   ├── test_auxiliary_circuit_breaker.py   # 서킷 브레이커 단위 테스트
│   └── test_auxiliary_sequential_init.py   # 순차 초기화 단위 테스트
└── integration/
    └── test_auxiliary_503_gate.py          # 역방향 프록시 503 게이트 통합 테스트
```

**Structure Decision**: 기존 Python 단일 서비스 구조(`src/core/`, `src/api/routes/`, `tests/`)를 그대로 활용하며, 보조 모델 관리자(`auxiliary_manager.py`)와 프록시 엔드포인트(`inference_api.py`)에 안전 로직을 추가합니다.

## Complexity Tracking

> **Violations**: 없음 (모든 헌법 원칙 준수)

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| 없음 | N/A | N/A |

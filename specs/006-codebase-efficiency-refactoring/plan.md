# Implementation Plan: 코드베이스 구조 개선 및 효율화 리팩토링 (Codebase Efficiency Refactoring)

**Feature Branch**: `006-codebase-efficiency-refactoring`  
**Date**: 2026-07-29

## Technical Context

- **Core Technologies**: Python 3.10+, FastAPI 0.110+, Pydantic v2, `httpx` (AsyncClient), `asyncio`, `pytest`
- **Primary Modules**:
  - `src/core/llama_manager.py`: 리팩토링 대상 (책임 분리 ➔ `ProcessManager`, `EventBroadcaster`, `LlamaManager` 코디네이터)
  - `src/core/process_manager.py`: 서브프로세스 런치/킬 및 `SIGKILL` 후 `await process.wait()` 좀비 수거 전담 (`FR-009`)
  - `src/core/event_broadcaster.py`: SSE 리스너, Bounded Queue(`maxsize=100`), 15s ping 및 오버플로우 시 풀 스냅샷 전담 (`FR-007`, `FR-011`)
  - `src/core/config_manager.py`: 원자적 파일 I/O (`tempfile` 동일 디렉토리 + `chmod 0600` + `os.replace`) & 캐싱 고도화 (`FR-003`, `FR-008`)
  - `src/api/routes/inference_api.py`: `httpx.AsyncClient` lifespan 커넥션 풀 활용, 클라이언트 이탈(`request.is_disconnected()`) 감지 및 `try...finally` 내 `response.aclose()` 정리 (`FR-004`, `FR-006`, `FR-010`)
  - `src/api/main.py`: FastAPI `lifespan` 관리자 구현 및 커넥션 풀 해제(`aclose()`)
- **Key Constraints**:
  - 외부 API 엔드포인트 URL, JSON 스키마, SSE 포맷, 503 Maintenance Mode 헤더 규격 100% 하위 호환성 유지
  - 기존 10개 전체 pytest 테스트 100% 통과

---

## Constitution Check

- **Principle I: 언어 정책 (한국어 출력 및 영어 추론)**: ✅ 통과 (모든 문서 및 주석/가이드 한국어 작성)
- **Principle II: 테스트 주도 개발 및 품질 보증**: ✅ 통과 (모듈별 단위 테스트 및 10개 레그레션 통합 테스트 100% 통과 조건)
- **Principle III: 작업 종료 조건 명확화 (DoD)**: ✅ 통과 (DoD-001 ~ DoD-003 정립)
- **Principle IV: 비파괴적 문서 수정 원칙**: ✅ 통과 (기존 기능 및 명세 항목 요약/생략 없이 100% 보존 및 비파괴적 고도화)

---

## Project Structure & Architecture Touch-Points

```text
src/
├── core/
│   ├── llama_manager.py       # [REFACTOR] LlamaManager 코디네이터 및 하위 컴포넌트 조합
│   ├── process_manager.py     # [NEW] 서브프로세스 런치/킬/VRAM 감지 전담
│   ├── event_broadcaster.py   # [NEW] SSE 리스너 관리, Bounded Queue, 15s ping 하트비트 전담
│   └── config_manager.py      # [REFACTOR] 동일 디렉토리 Atomic Replace & 캐싱
├── api/
│   ├── main.py                # [REFACTOR] lifespan 컨텍스트 매니저 바인딩 (AsyncClient)
│   ├── routes/
│   │   ├── inference_api.py   # [REFACTOR] lifespan 커넥션 풀 사용 & Disconnect Cancellation
│   │   └── dashboard_api.py   # [REFACTOR] Pydantic 모델 타입 힌팅 강화
tests/
├── unit/
│   ├── test_llama_manager.py  # [UPDATE] ProcessManager 및 EventBroadcaster 단위 테스트 추가
│   └── test_config_manager.py # [UPDATE] Atomic Replace 동일 디렉토리 테스트 추가
└── integration/
    ├── test_dashboard.py      # [VERIFY] 100% 레그레션 통과
    └── test_dashboard_api.py  # [VERIFY] 100% 레그레션 통과
```

---

## Phases & Execution Plan

### Phase 0: Research & Foundation
- `research.md` 작성 및 기술 검증 완료:
  - `ProcessManager`와 `EventBroadcaster` 책임 분리 전략
  - 동일 디렉토리 원자적 I/O(`tempfile` + `os.replace`)로 EXDEV 에러 차단
  - FastAPI `lifespan` 내 `httpx.AsyncClient` 커넥션 풀링
  - `request.is_disconnected()` 비동기 프록시 캔슬레이션

### Phase 1: Core Modularization & Design Artifacts
- `data-model.md`, `quickstart.md` 작성 완료
- `ProcessState` Pydantic v2 불변 모델(`frozen=True`) 정의

### Phase 2: Implementation & Verification Strategy
- **Step 1**: `config_manager.py` 동일 디렉토리 원자적 I/O 및 캐시 구현 ➔ `test_config_manager.py` 단위 테스트 검증
- **Step 2**: `process_manager.py` & `event_broadcaster.py` 추출 구현 ➔ `test_llama_manager.py` 단위 테스트 검증
- **Step 3**: `src/api/main.py` lifespan 바인딩 및 `inference_api.py` 커넥션 풀 / Disconnect 감지 구현
- **Step 4**: 전체 10개 레그레션 테스트(`uv run pytest`) 구동 및 100% 통과 확인

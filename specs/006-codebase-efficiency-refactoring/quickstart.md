# Quickstart & Validation Guide: Codebase Efficiency Refactoring

**Feature**: `006-codebase-efficiency-refactoring`  
**Date**: 2026-07-29

본 가이드는 리팩토링된 모듈의 개별 단위 테스트 및 통합 테스트를 통한 완전한 검증 수순을 제시합니다.

## Prerequisites

- Python 3.10+ (uv 환경)
- 기존 pytest 테스트 환경 구동 가능

---

## Validation Scenarios

### Scenario 1: 책임 분리 모듈 단위 테스트 검증 (`ProcessManager` & `EventBroadcaster`)

1. 단위 테스트 실행:
   ```bash
   uv run pytest tests/unit/test_llama_manager.py
   ```
2. **검증 사항**:
   - `ProcessManager`가 서브프로세스 런치 및 킬 모킹 상태에서 상태 객체를 불변(`ProcessState`)으로 리턴하는지 확인.
   - `EventBroadcaster`가 Bounded Queue(`maxsize=100`) 환경에서 구독자 수용 및 15초 하트비트 주입 패킷(`: ping\n\n`)을 올바르게 디스패치하는지 확인.

---

### Scenario 2: 원자적 파일 쓰기(Atomic Replace) 검증 (`ConfigManager`)

1. 원자적 설정 파일 저장 단위 테스트 구동:
   ```bash
   uv run pytest tests/unit/test_config_manager.py
   ```
2. **검증 사항**:
   - 동일 디렉토리 내 임시 파일 생성을 통해 동시 파일 쓰기 및 `os.replace` 시 데이터 오염이 발생하지 않는지 확인.
   - `get_config()` 메모리 캐시 조회가 불필요한 디스크 읽기 없이 신속하게 반환되는지 확인.

---

### Scenario 3: 비동기 역방향 프록시 및 전체 10개 레그레션 테스트 통합 검증

1. 전체 pytest 수트 구동:
   ```bash
   uv run pytest
   ```
2. **검증 사항**:
   - 기존 10개 전체 단위 및 통합 테스트 성공률 100% 달성.
   - `httpx.AsyncClient` 커넥션 풀이 FastAPI `lifespan` 내에서 정상 생성되고 소켓 누수 없이 정리되는지 검증.

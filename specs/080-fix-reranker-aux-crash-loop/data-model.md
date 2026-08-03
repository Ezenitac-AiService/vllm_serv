# Phase 1 Data Model: 보조 모델 크래시 루프 방지 및 프록시 게이트 (`080-fix-reranker-aux-crash-loop`)

## Entities & Enums

### 1. ProcessStatusEnum (상태 열거형 확장)

`src/core/process_manager.py`에 정의된 백엔드 프로세스 생주기 상태:

- `UNLOADED`: 프로세스 미구동
- `LOADING`: 프로세스 생성 및 모델 메모리 적재 중
- `READY`: 헬스체크 통과 및 서비스 가능 상태
- `ERROR`: 실행 실패 또는 비정상 종료 (재시도 대상)
- `DISABLED` *(기능 080 핵심)*: 최대 연속 크래시 횟수(3회) 초과로 인한 서킷 브레이커 작동 상태 (자동 재시작 시도 중단, on-demand 재시작 차단)

### 2. AuxiliaryModelManager State (엔티티 확장)

`src/core/auxiliary_manager.py` 클래스 내부 관리 데이터 구조:

| 필드명 | 타입 | 기본값 | 설명 |
|-------|------|-------|------|
| `embedding_pm` | `ProcessManager` | `ProcessManager(port=8090)` | Embedding 백엔드 프로세스 관리자 |
| `rerank_pm` | `ProcessManager` | `ProcessManager(port=8091)` | Reranker 백엔드 프로세스 관리자 |
| `embedding_consecutive_crashes` | `int` | `0` | Embedding 연속 크래시 카운터 |
| `rerank_consecutive_crashes` | `int` | `0` | Reranker 연속 크래시 카운터 |
| `max_consecutive_crashes` | `int` | `3` | 서킷 브레이커 작동 최대 허용 크래시 횟수 (`server_config.json`에서 설정 가능) |

### 3. State Transition Matrix (상태 전이 표)

```
[UNLOADED] --(spawn)--> [LOADING] --(healthcheck pass)--> [READY] (crashes = 0)
   ^                       |                                 |
   |                (healthcheck fail/crash)          (crash detected in loop)
   |                       v                                 v
   +<--- (crashes < 3) --- [ERROR] <-------------------------+
                           |
                     (crashes >= 3)
                           v
                      [DISABLED] (no auto-restart, return 503 on request)
```

## Configuration Data Model (`config/server_config.json`)

```json
{
  "embedding_backend_port": 8090,
  "rerank_backend_port": 8091,
  "embedding_enabled": true,
  "rerank_enabled": true,
  "auxiliary_max_crashes": 3
}
```

# Phase 1 Data Model: Process Lifecycle & Test Reliability Entities

**Feature**: Codebase Structural Audit & Real-world Test Reliability Verification (`012-audit-test-reliability`)

## Entities & Data Contracts

### 1. ProcessLifecycleState (프로세스 생명주기 엔티티)

`ProcessManager` 및 `LlamaManager`가 프로세스의 상태 변화를 추적하고 보장하는 핵심 데이터 모델.

| Field Name | Type | Description | Validation Rules |
|------------|------|-------------|------------------|
| `status` | `ProcessStatusEnum` | 프로세스 현재 상태 (`UNLOADED`, `LOADING`, `READY`, `ERROR`, `DOWNLOADING`) | 필수 Enum |
| `model_id` | `Optional[str]` | 현재 할당된 모델 식별자 (예: `qwen3.5-4b`) | `model_presets`에 등록된 식별자 |
| `port` | `int` | 서빙 추론 HTTP 포트 | 기본 `8081` |
| `pid` | `Optional[int]` | 실행 중인 서브프로세스 PID | `status == READY` 일 때 비어있지 않음 |
| `vram_offloaded_100pct` | `bool` | GPU VRAM 100% 오프로드 완성 여부 | `True` 일 때만 READY 전환 허용 |
| `error_message` | `Optional[str]` | 에러 발생 시 세부 메시지 | `status == ERROR` 일 때 필수 |
| `exit_code` | `Optional[int]` | 서브프로세스 종료 코드 | 정상 종료 시 `0` 또는 `None` |

---

### 2. PortCollisionPolicy (포트 충돌 복구 정책 엔티티)

포트 8081 점유 시 자율 복구 및 예외 처리를 규정하는 정책 구조체.

```json
{
  "target_port": 8081,
  "max_cleanup_retries": 10,
  "retry_interval_sec": 0.5,
  "recovery_strategy": "AUTONOMOUS_DRAIN_THEN_KILL",
  "raise_exception_on_unresolvable": true,
  "exception_class": "PortCollisionError"
}
```

---

### 3. TestReliabilityContract (테스트 정합성 계약 엔티티)

단위/통합 테스트 수트가 실측 런타임 시스템 동작을 모사하고 자원 누수를 차단하기 위해 준수해야 하는 계약.

- **Teardown Rule**: 모든 Async Fixture는 실행 후 `await pm.stop_process()`를 통해 프로세스를 멸실시켜야 함.
- **Port Release Verification**: 테스트 간 포트 8081 소켓이 완전히 해제되었음을 `SO_REUSEADDR` 소켓 연결로 동기식 확인.
- **CUDA Runtime Rule**: CPU 전용 바이너리 사용 금지, CUDA 100% 파이프라인 검증.

---

### 4. GoldenDatasetRecord (골든 데이터셋 합성 엔티티)

Antigravity Gemini 3.6 Flash 모델을 통해 합성/생성되는 벤치마크 평가 정답지 레퍼런스 엔티티.

| Field Name | Type | Description |
|------------|------|-------------|
| `eval_id` | `str` | 골든 데이터셋 항목 고유 식별자 (예: `GOLDEN-FINANCE-01`) |
| `prompt` | `str` | 품질 평가용 입력 질의 프롬프트 |
| `ground_truth_answer` | `str` | Antigravity Gemini 3.6 Flash가 생성한 레퍼런스 정답 |
| `eval_rubric` | `Dict[str, float]` | 키워드 매칭, 문맥 일치성, 간결성 가중치 루브릭 |
| `generator_model` | `str` | 생성 AI 모델명 (`antigravity-gemini-3.6-flash`) |

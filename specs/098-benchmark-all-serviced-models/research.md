# Research & Technical Decisions: 서비스 대상 전체 LLM 모델 기반 컨텍스트 윈도우 스케일링 벤치마크 확장

**Feature**: `098-benchmark-all-serviced-models`
**Created**: 2026-08-05

## Research Topics & Decision Log

### 1. 다중 LLM 후보 모델 실측 GPU 벤치마킹 통합 구조 설계 (Multi-Model Real GPU Benchmark Architecture)

* **Decision**: `scripts/benchmark_context_window.py`의 `evaluate_all_catalog_models` 함수를 기존 고정 수식(TPS=45.0) 비교 방식에서 **카탈로그의 각 후보 LLM 모델에 대해 실제 GPU 프로세스를 스폰하고 2단계 이진 탐색 스케일링을 수행하는 실측 파이프라인**으로 전면 개편합니다.
* **Rationale**:
  * 기존 구조는 모델별 무결성 검사만 수행한 뒤 디폴트 45.0 TPS 수식을 적용하여 상위 TPS 모델(`gemma4-e2b`)을 자의적으로 선정한 후, 단 1개 모델에 대해서만 실측 이진 탐색을 구동했습니다.
  * vllm_serv 헌법 II조(Real Verification 원칙)에 따라 모든 candidate LLM 모델(gemma4-e2b, gemma4-e4b, gemma4-12b, qwen3.5-2b, qwen3.5-4b, qwen3.5-9b 등)에 대해 실제 `ProcessManager.spawn_process(model_name, n_ctx)`를 스폰하여 실측 웜업 인퍼런스를 투입하고, 실측 TPS와 VRAM 점유량을 수집해야 실체적인 최적 서빙 모델 선정이 가능합니다.
* **Alternatives Considered**:
  * *대안 A (경량 수식 추정 유지)*: 스캔 속도는 빠르나 타 모델 서빙 시 VRAM OOM 발생 여부를 사전에 검증하지 못해 프로덕션 롤백 에러 유발 ➔ **기각**
  * *대안 B (선택적 2개 모델만 실측)*: 사용자 지정 모델만 벤치마크 ➔ **기각 (전체 모델 대상 지원 요구사항 불충족)**

---

### 2. 개별 모델 실측 타임아웃 (120초) 및 비동기 프로세스 안전 정리 (Per-Model Timeout & Safe Process Cleanup)

* **Decision**: 개별 모델의 GPU 스폰, 웜업 및 이진 탐색 수행 시간을 **최대 120초**로 제한하며, `asyncio.wait_for(..., timeout=120)`로 래핑합니다. 타임아웃 초과 또는 OOM 발생 시 하위 `llama-server` 프로세스에 대해 `ProcessManager.stop_process()` 및 `kill -9`를 수행하여 GPU VRAM을 완전히 해제하고, 해당 모델의 프로파일을 `is_supported=False`, `recommended_context_length=2048`로 안전 마킹한 후 다음 모델 벤치마크를 계속 진행합니다.
* **Rationale**:
  * 12B 이상 대형 모델 또는 특정 GPU 호환성 문제 발생 시 벤치마크 프로세스가 무한 멈춤(Hang) 상태에 빠지는 위험을 차단합니다.
  * 헌법 IV조(Definition of Done 및 파이프라인 연속성)에 따라 에러가 발생해도 setup.sh 전체가 exit status != 0으로 비정상 종료되는 것을 방지합니다.
* **Alternatives Considered**:
  * *대안 A (타임아웃 미설정 및 예외 시 setup.sh 중단)*: 멈춤 현상 발생 시 사용자가 수동 중단해야 함 ➔ **기각**

---

### 3. 부분 캐시 미스 (Partial Cache Miss) 핀포인트 벤치마크 및 캐시 스킵 알고리즘 (Pinpoint Cache Sync & Bypass)

* **Decision**: setup.sh 구동 시 아래 3단계 조건 판정 알고리즘을 적용합니다:
  1. **`--force-benchmark` 플래그 감지 시**: 기존 캐시 무시 ➔ 카탈로그 내 모든 LLM 후보 모델 전체 강제 실측 벤치마크 및 `model_context_profiles.json` 덮어쓰기.
  2. **일반 구동 (`--force-benchmark` 없음) & 부분 캐시 미스 감지 시**: `config/model_catalog.json` 내 LLM 모델 목록 `C`와 `config/model_context_profiles.json` 내 프로필 모델 목록 `P` 비교. `Missing = C - P`가 1개 이상 존재 시, 전체 벤치마크를 재수행하지 않고 **`Missing`에 포함된 신규 모델에 대해서만 실측 벤치마크를 수행하여 캐시 병합(Merge) 저장**.
  3. **일반 구동 & 완전 캐시 정합 시 (`C - P == ∅`)**: 벤치마크 실행 스킵 ➔ 5초 이내 고속 통과 및 기존 프로파일/서버 설정 보존.
* **Rationale**:
  * 신규 모델이 카탈로그에 추가될 때마다 수 분이 소요되는 전체 벤치마크를 재수행하는 낭비를 방지하고, 필요한 신규 모델만 핀포인트로 측정하여 빠른 셋업 속도(SC-003, SC-004)를 보장합니다.
* **Alternatives Considered**:
  * *대안 A (부분 캐시 미스 시 전체 벤치마크 재수행)*: 재벤치마킹 오버헤드가 과도함 ➔ **기각**

---

### 4. 원자적 파일 저장 및 스키마 정합성 (Atomic File Write & Schema Parity)

* **Decision**: 프로필 업데이트 시 `config/model_context_profiles.json.tmp` 파일에 먼저 `json.dump`를 기록한 후 `os.replace`로 원자적으로 치환합니다. 프로필 schema에 `is_supported: bool` 필드를 추가하여 벤치마크 성공/실패 여부를 정량 명시합니다.
* **Rationale**:
  * 벤치마크 실행 중 전원 차단이나 프로세스 kill 발생 시 기존 유효한 캐시 파일이 0바이트로 손상되는 현상을 완벽히 방지합니다.

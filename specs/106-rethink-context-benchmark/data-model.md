# Phase 1 Data Model: 컨텍스트 윈도우 벤치마킹 데이터 모델

**Feature Branch**: `106-rethink-context-benchmark`
**Date**: 2026-08-07
**Spec**: [spec.md](./spec.md)

## 1. Entities & Data Schemas

### GpuResourceSnapshot
실시간 GPU 자원 상태 스냅샷을 나타내는 불변 데이터 구조.

| Field Name | Type | Description | Constraints |
|------------|------|-------------|-------------|
| `gpu_name` | `str` | GPU 제품명 (예: "NVIDIA GeForce GTX 1080 Ti") | non-empty |
| `total_vram_mb` | `int` | 전체 물리 GPU VRAM (MB) | > 0 |
| `used_vram_mb` | `int` | 현재 타 프로세스 및 시스템 점유 VRAM (MB) | >= 0 |
| `free_vram_mb` | `int` | 현재 실제 할당 가능한 가용 VRAM (MB) | >= 0 |
| `is_cuda_available` | `bool` | CUDA 가속 엔진 사용 가능 여부 | True |

#### Dynamic Usable VRAM Calculation
$$\text{usable\_vram\_mb} = \max(0, \text{free\_vram\_mb} - \text{SAFETY\_MARGIN\_MB})$$
- `SAFETY_MARGIN_MB` 기본값: `500` MB

---

### ModelContextProfile
각 LLM 후보 모델별 벤치마크 실측 결과 프로파일 불변 엔티티.

| Field Name | Type | Description | Constraints |
|------------|------|-------------|-------------|
| `max_context_length` | `int` | 실측 검증된 최대 성공 컨텍스트 크기 | >= 2048, 512의 배수 |
| `recommended_context_length` | `int` | VRAM 안정성을 고려한 최종 권장 컨텍스트 크기 | <= `max_context_length` |
| `binary_search_steps` | `List[BinarySearchStep]` | 이진 탐색 단계별 실측 히스토리 | |
| `peak_vram_mb` | `int` | 최고점 VRAM 점유량 (MB) | >= 0 |
| `tpot_tok_per_sec` | `float` | 추론 속도 (Token Per Second) | >= 0.0 |
| `scaling_tested` | `bool` | GPU 실측 이진 탐색 완료 여부 | |
| `is_supported` | `bool` | 현재 시스템 자원 상 서빙 가능 여부 | |
| `failure_reason` | `str` | 실패 시 명확한 원인 사유 메시지 | "SUCCESS" or Error Detail |
| `last_tested_at` | `str` | ISO 8601 UTC 타임스탬프 | `%Y-%m-%dT%H:%M:%SZ` |

---

### BinarySearchStep
이진 탐색 벤치마킹 개별 단계를 기록하는 객체.

| Field Name | Type | Description | Constraints |
|------------|------|-------------|-------------|
| `step` | `int` | 탐색 회차 (1 ~ 5) | 1 ~ 5 |
| `tested_n_ctx` | `int` | 해당 회차에서 테스트한 컨텍스트 크기 | 512 블록 얼라인먼트 |
| `real_vram_mb` | `int` | 실측된 VRAM 점유량 (MB) | >= 0 |
| `status` | `str` | 단계 통과 여부 | "PASS" \| "OOM/FAIL" |
| `reason` | `str` | 상세 이유 또는 에러 코드 | "SUCCESS" \| "HEALTH_CHECK_TIMEOUT" \| "CUDA_OOM_KILLED" |

---

## 2. Validation & State Preservation Rules

1. **Non-Destructive Overwrite Rule**:
   - `existing_profile.is_supported == True` 이고 `new_result.is_supported == False` 이면서 CLI에 `--force-overwrite-profiles` 옵션이 지정되지 않은 경우:
   - `existing_profile`을 그대로 보존하고 `failure_reason` 경고만 로그에 기록한다.
2. **Atomic Write Rule**:
   - `config/model_context_profiles.json` 저장 시 임시 파일(`model_context_profiles.json.tmp`)로 이중 쓰기 후 `os.replace`로 원자적 교체하여 파일 손상을 방지한다.

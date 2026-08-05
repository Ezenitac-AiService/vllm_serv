# Feature Specification: 서비스 대상 전체 LLM 모델 기반 컨텍스트 윈도우 스케일링 벤치마크 확장 (Step 4.5 Multi-Model Context Benchmark)

**Feature Branch**: `098-benchmark-all-serviced-models`

**Created**: 2026-08-05

**Status**: Draft

**Input**: User description: "4.5단계는 왜 서비스 하는 모든 모델을 대상으로 하지 않는거야?"

## Clarifications

### Session 2026-08-05

- Q: Step 2.8과 Step 4.5의 전체 후보 모델 실측 벤치마크 범위 통일 및 스킵 조건 → A: Option A (강제 벤치마크 옵션 `--force-benchmark` 부여 시 Step 2.8과 Step 4.5 모두 카탈로그 내 전체 후보 모델에 대해 실제 GPU 인퍼런스 실측 벤치마크 및 이진 탐색 스케일링을 수행하여 서비스 가능 모델 검증, 최적 모델 선정 및 전체 컨텍스트 프로필 갱신. 강제 옵션 미부여 시 저장된 설정 파일이 존재하면 실측 벤치마크를 스킵하고 기존 설정을 유지)
- Q: 부분 캐시 미스 처리, 벤치마크 타임아웃 및 하드웨어 VRAM 로딩 한계 정책 → A: Option A (기존 `model_context_profiles.json` 캐시에 미등록된 신규 모델 감지 시 해당 모델만 선택적 핀포인트 벤치마크(Partial Sync) 수행. 개별 모델 실측 타임아웃 120초 적용 및 VRAM 초과로 로딩 불가능한 대형 모델은 `unsupported` 상태(recommended_context_length=2048, is_supported=False)로 안전 마킹하여 setup.sh 지연 및 OOM 롤백 에러 방지)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 카탈로그 내 서비스 대상 전체 LLM 모델의 컨텍스트 윈도우 스케일링 프로파일링 (Priority: P1)

시스템 관리자가 `./setup.sh --force-benchmark` 또는 `benchmark_context_window.py --force-benchmark` 실행 시, 기존 단일 기본 모델(`qwen3.5-4b`)에 국한되지 않고 `config/model_catalog.json`에 등록된 모든 서비스 대상 LLM 후보 모델(gemma4-e2b, gemma4-e4b, gemma4-12b, qwen3.5-2b, qwen3.5-4b, qwen3.5-9b 등)에 대해 실제로 GPU 프로세스를 스폰하여 2단계 이진 탐색 컨텍스트 윈도우 스케일링 벤치마크를 순차적으로 수행하고 각 모델별 추천 컨텍스트 크기를 `config/model_context_profiles.json`에 원자적으로 저장 및 갱신합니다.

**Why this priority**: 현재 Step 4.5는 기본 파라미터 미지정 시 단일 특정 모델만 벤치마킹하여 다른 후보 모델들에 대한 최적 컨텍스트 프로필 정보가 누락됩니다. 서비스 가능한 모든 모델의 GPU 메모리 한계(Limit) 및 최대/추천 컨텍스트 윈도우를 사전에 실측하여 종합 측정해야 다중 모델 전환 시 VRAM OOM 없는 안정적 서비스가 가능합니다.

**Independent Test**: `uv run python scripts/benchmark_context_window.py --force-benchmark` 명령 실행 후 `config/model_context_profiles.json`의 `profiles` 객체 내에 카탈로그의 모든 LLM 후보 모델 키와 각 모델별 `max_context_length`, `recommended_context_length` 실측 결과가 100% 정상 수록되었는지 단정하여 측정합니다.

**Acceptance Scenarios**:

1. **Given** `config/model_catalog.json`에 N개의 LLM 후보 모델이 등록되어 있고 `--force-benchmark` 옵션이 부여된 상태에서, **When** Step 2.8 및 Step 4.5 벤치마크가 가동되면, **Then** N개 모델 전체에 대해 순차적으로 실측 GPU 인퍼런스 및 이진 탐색 부하 투입이 실행되어 최적 모델이 선정되고 모든 모델의 스케일링 프로필이 `config/model_context_profiles.json`에 저장되어야 합니다.
2. **Given** 기존 `config/model_context_profiles.json`에 M개의 모델이 수록되어 있고 `config/model_catalog.json`에 1개의 신규 모델이 추가되어 부분 캐시 미스(Partial Cache Miss)가 발생한 상태에서, **When** `--force-benchmark` 옵션 없이 `./setup.sh`가 구동되면, **Then** 전체 벤치마크를 재수행하지 않고 미측정된 신규 모델에 대해서만 선택적 핀포인트 벤치마크를 수행하여 캐시를 보완 갱신해야 합니다.
3. **Given** 기존 `config/model_context_profiles.json` 및 `config/server_config.json` 캐시 파일이 완전 정합(100% Match)인 상태에서, **When** `--force-benchmark` 옵션 없이 `./setup.sh`가 실행되면, **Then** 실측 GPU 벤치마크가 스킵되고 기존 저장된 프로필과 설정값이 보존되어야 합니다.
4. **Given** 특정 대형 모델이 VRAM 용량 초과로 인해 최소 컨텍스트 로딩조차 불가능하거나 120초 타임아웃이 발생한 경우, **When** 실측 벤치마크가 진행되면, **Then** 프로세스가 즉시 SIGKILL 안전 종료되고 해당 모델은 `is_supported=False` 및 `unsupported` 상태로 마킹되어 setup.sh 전체의 멈춤(Hang)을 방지하고 다음 모델 벤치마크로 정상 이행되어야 합니다.

---

### User Story 2 - setup.sh 2.8/4.5단계 및 CLI 파라미터와의 일관된 모듈 연동 (Priority: P2)

관리자가 `./setup.sh --force-benchmark` 옵션으로 전체 설정을 수행할 때 Step 2.8(최적 서빙 모델 선정)과 Step 4.5(컨텍스트 윈도우 스케일링 프로파일링) 모두 카탈로그 전체 모델을 대상으로 실제 GPU 인퍼런스 실측 기반으로 통합 동작하도록 구성합니다.

**Why this priority**: setup.sh 내 Step 2.8과 Step 4.5의 모델 대상 범위 및 실측 방식 불일치로 인한 혼선을 방지하고 원스톱 환경 구축 스크립트의 결정론적 완성도를 보장합니다.

**Independent Test**: `./setup.sh --force-benchmark` 실행 후 Step 2.8 및 Step 4.5 출력 로그에서 카탈로그 전체 모델 대상 실측 벤치마크 수행 로그가 정상 출력되고 exit status 0으로 완료되는지 검증합니다.

**Acceptance Scenarios**:

1. **Given** `--force-benchmark` 플래그가 부여된 `./setup.sh` 실행 시, **When** Step 2.8 및 Step 4.5에 도달하면, **Then** 카탈로그 내 서비스 대상 모든 LLM 모델에 대해 실제 GPU 프로세스 기반 실측 벤치마크가 수행되고 캐시 파일이 업데이트되어야 합니다.

---

### Edge Cases

- **로컬 가중치 미존재 모델 수반**: 일부 LLM 후보 모델 가중치가 로컬 `models/` 디렉토리에 존재하지 않을 경우, 가중치가 존재하는 모델은 GPU 프로세스를 스폰하여 실측하고 미존재 모델은 하드웨어 VRAM 기반 추정 프로필을 적용하여 전체 프로세스 중단을 방지합니다.
- **임베딩/리랭커 전용 모델 탐지**: `config/model_catalog.json` 내 `task_type`이 `embedding` 또는 `rerank`인 모델은 LLM 컨텍스트 윈도우 생성 인퍼런스 벤치마크 대상에서 자동으로 제외 처리합니다.
- **실측 프로세스 타임아웃 초과**: 개별 모델당 실측 GPU 스폰 대기 또는 웜업 실행 시간이 120초를 초과하는 경우, 하위 프로세스를 원자적으로 kill하고 안전 프로필을 할당합니다.
- **VRAM 물리 용량 완전 초과 모델**: VRAM 부족으로 하위 `llama-server` 프로세스가 스폰 직후 즉시 OOM 에러로 종료되는 경우, `is_supported=False` 및 `unsupported` 상태를 할당하고 파이프라인을 계속 진행합니다.

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `scripts/benchmark_context_window.py`에 카탈로그 전체 LLM 모델을 순차적으로 실제 GPU 인퍼런스 스폰을 통해 실측 벤치마크하고 프로필을 병합 저장하는 파이프라인 구현 통과
- **DoD-002**: 개별 모델 실측 120초 타임아웃 제어 및 VRAM 완전 초과 모델에 대한 `unsupported` 상태 처리 및 부분 캐시 미스(Partial Cache Miss) 핀포인트 벤치마크 기능 통과
- **DoD-003**: `scripts/setup.sh` Step 2.8 및 Step 4.5 모듈이 `--force-benchmark` 옵션 시 서비스 대상 전체 모델에 대한 실측 벤치마크 및 스케일링을 호출하도록 연동 완료, 미부여 시 저장된 캐시 설정으로 스킵 처리 및 `./setup.sh --force-benchmark` 정상 동작 검증
- **DoD-004**: `pytest` 단위/통합 테스트 및 전체 회귀 테스트 수트(`uv run pytest`) 통과

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 시스템은 `config/model_catalog.json`에서 `task_type`이 LLM 서빙 대상(임베딩/리랭커 제외)인 모든 후보 모델 목록을 자동으로 추출해야 합니다.
- **FR-002**: `--force-benchmark` 옵션 부여 시 Step 2.8 최적 모델 선정과 Step 4.5 컨텍스트 윈도우 스케일링 벤치마크 실행 시, 추출된 모든 서비스 대상 LLM 모델에 대해 실제 GPU 프로세스를 스폰하여 실측 벤치마크 및 512/1024 토큰 얼라인먼트 이진 탐색을 수행해야 합니다.
- **FR-003**: 시스템은 벤치마크 결과를 `config/model_context_profiles.json`의 `profiles` dictionary에 모델명을 키로 하여 원자적(atomic write)으로 병합 및 저장해야 합니다.
- **FR-004**: 로컬 GGUF 파일이 존재하지 않거나 GPU 스폰 실패 시, 해당 모델에 대해서는 VRAM 기반 안전 기본값 프로필을 기록하고 전체 파이프라인을 비파괴적으로 계속 진행해야 합니다.
- **FR-005**: `./setup.sh --force-benchmark` 구동 시 Step 2.8 및 Step 4.5에서 서비스 대상 전체 모델 실측 벤치마크 및 스케일링이 자동 호출되어야 합니다.
- **FR-006**: `--force-benchmark` 옵션이 미부여된 setup.sh 구동 시 기존 저장된 `config/model_context_profiles.json`에 카탈로그 모든 모델의 프로필이 완벽 수록되어 있는 경우 실측 벤치마크를 스킵하고 기존 설정값을 보존해야 합니다.
- **FR-007**: 캐시에 미등록된 신규 모델이 감지된 부분 캐시 미스(Partial Cache Miss) 시, 전체 벤치마크 대신 미등록 모델만 핀포인트로 추가 벤치마크하여 캐시를 보완 업데이트해야 합니다.
- **FR-008**: 개별 모델 실측 GPU 벤치마크 및 이진 탐색 타임아웃을 120초로 제한하고, 타임아웃 또는 VRAM 100% 로딩 불가 시 프로세스를 안전 정리하고 `is_supported=False` 및 `unsupported` 프로필을 기록해야 합니다.

### Key Entities

- **ModelCatalog**: `config/model_catalog.json`에 정의된 모델 식별자, `task_type`, `model_path`, `vram_est_mb` 등의 모델 메타데이터 객체.
- **ModelContextProfiles**: `config/model_context_profiles.json`에 저장되는 각 모델별 `max_context_length`, `recommended_context_length`, `binary_search_steps`, `peak_vram_mb`, `is_supported` 프로파일 데이터 엔티티.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `--force-benchmark` 수행 시 `config/model_context_profiles.json`에 등록된 LLM 후보 모델 전체(최소 6종 이상)의 실측 프로필 항목이 누락 없이 100% 수록되어야 합니다.
- **SC-002**: 로컬 모델 가중치 부재, OOM 실패 또는 120초 타임아웃 초과 시에도 setup.sh 전체 스크립트 실행이 에러(exit status != 0) 없이 완료율 100%를 달성해야 합니다.
- **SC-003**: 기존 프로파일 캐시 완전 존재 시 `--force-benchmark` 미지정 `./setup.sh` 실행 시간이 5초 이내로 스킵 완료되어 고속 재사용을 달성해야 합니다.
- **SC-004**: 부분 캐시 미스 발생 시 미등록 신규 모델만 선택 벤치마킹하여 무필요한 재벤치마킹 오버헤드를 0%로 제거해야 합니다.

## Assumptions

- **카탈로그 기반 대상 정의**: "서비스 하는 모든 모델"은 `config/model_catalog.json`에 등록된 LLM task_type 모델 전체를 의미합니다.
- **VRAM 안전 하한선**: GPU 이진 탐색 중 VRAM 점유율이 92%를 초과하거나 프로세스 스폰 에러 시 해당 구간을 Fail로 처리하여 안전 한계 내 context size를 측정합니다.
- **기존 캐시 하위 호환성**: `model_context_profiles.json` 업데이트 시 기존에 측정된 다른 모델의 프로필 데이터를 지우지 않고 인메모리 로드 후 덮어쓰기/병합(Merge) 방식으로 저장하며, 강제 옵션 미부여 시 캐시 파일을 재사용합니다.

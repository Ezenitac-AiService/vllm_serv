# Feature Specification: 시드 팩(Seed Pack) 생성 스크립트 최신 명세(GQA/GGUF/프로필) 반영 고도화

**Feature Branch**: `109-seed-pack-script-enhancement`  
**Created**: 2026-08-07  
**Status**: Draft  
**Input**: User description: "/speckit-specify 시드 팩 만드는 스크립트를 현재 스펙을 반영하여 고도화"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - GQA 파서 및 최신 아키텍처 수록 검증 🎯 MVP (Priority: P1)

> **As a** LLM 서빙 시스템 관리자  
> **I want to** `./make_seed_pack.sh` 실행 시 Feature 108에서 추가된 GQA VRAM 연산 모듈(`src/core/gpu_detector.py`), GGUF 바이너리 파서, 및 갱신된 `config/model_catalog.json` 명세가 압축 아카이브에 100% 빠짐없이 패키징되길 원한다.  
> **So that** 신규 GPU 서버 이관 후 `./setup.sh` 구동 시 경량 GQA 모델(Gemma 4, Qwen 3.5 등)의 KV 캐시 역산 및 동적 상한선 확장 탐색이 오작동 없이 즉시 수행되도록 보장한다.

**Why this priority**: 이관 대상 타겟 서버에서 Feature 108의 GQA 파싱 및 동적 캡핑 기능이 온전히 작동하려면 관련 핵심 모듈과 명세 파일이 시드 팩에 누락 없이 수록되어야 함.

**Independent Test**: `./make_seed_pack.sh` 실행 후 아카이브 검증 루틴에서 `src/core/gpu_detector.py` 내 `read_gguf_metadata_architecture` 및 `config/model_catalog.json` 수록 여부를 실측 확인.

**Acceptance Scenarios**:
1. **Given** 프로젝트 루트에서, **When** `./make_seed_pack.sh`를 구동하면, **Then** 생성된 `dist/vllm_serv_seed.tar.gz` 내에 `src/core/gpu_detector.py`와 `config/model_catalog.json`의 최신 명세가 검증 통과한다.
2. **Given** 압축 아카이브 해제 시, **When** `read_gguf_metadata_architecture` 함수를 호출하면, **Then** 예외 없이 GGUF 바이너리 헤더 파싱 및 GQA $n_{\text{head\_kv}}$ 연산이 정상 동작한다.

---

### User Story 2 - 컨텍스트 프로필 동기화 및 선택적 포함 옵션 제공 (Priority: P2)

> **As a** DevOps 엔지니어  
> **I want to** 타겟 서버 이관 시 벤치마크 결과를 재활용하거나 새 환경에서 재측정할 수 있도록 `--include-profiles` 옵션을 제공받기를 원한다.  
> **So that** 기존 탐색된 컨텍스트 프로필(`config/model_context_profiles.json`)을 타겟 서버로 온전히 복사하여 재탐색 시간을 단축할 수 있다.

**Why this priority**: 이관 시 프로필 재사용 옵션을 통해 타겟 서버 초기 셋업 시간을 대폭 절감.

**Independent Test**: `./make_seed_pack.sh --include-profiles` 옵션 부여 시 `config/model_context_profiles.json`이 아카이브에 포함되는지 검증.

**Acceptance Scenarios**:
1. **Given** `--include-profiles` 옵션을 주어 `./make_seed_pack.sh --include-profiles`를 실행할 때, **Then** `config/model_context_profiles.json` 파일이 아카이브에 포함되고 검증 로그가 출력된다.

---

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `./make_seed_pack.sh` 구동 시 Feature 108 최신 모듈(`gpu_detector.py` GQA 파서) 및 `model_catalog.json` 수록 검증 100% 통과.
- **DoD-002**: `--include-profiles` CLI 옵션 지원 및 아카이브 검증 단위 테스트 수트 작성 및 통과.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `scripts/make_seed_pack.sh`가 Feature 108에서 개정된 `src/core/gpu_detector.py` (GQA 파서, pure-python GGUF 헤더 파서 `read_gguf_metadata_architecture`) 및 아키텍처 명세가 수록된 `config/model_catalog.json`을 아카이브 필수 수록 검증 대상에 수록해야 한다.
- **FR-002**: CLI 옵션 `--include-profiles`를 추가하여 지정 시 `config/model_context_profiles.json`을 제외 목록에서 해제하고 아카이브에 함께 번들링하도록 개선해야 한다.
- **FR-003**: 생성된 아카이브 내 필수 핵심 파일 수록 검증 항목에 `gpu_detector.py` GQA 함수 검증 및 `model_catalog.json` 수록 검증 단계를 추가해야 한다.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `./make_seed_pack.sh` 실행 시 10초 이내에 시드 팩 아카이브가 생성되고 필수 검증 항목 7개 이상이 모두 통과(PASS)해야 한다.
- **SC-002**: 생성된 시드 팩 용량이 모델/가상환경 제외 기준 15MB 이하를 유지해야 한다.
- **SC-003**: 단위 테스트 수트 `tests/unit/test_shell_scripts.py` 또는 `test_seed_pack.py` 실행 시 100% Green 통과해야 한다.

---

## Assumptions

- 기본 동작 시 대용량 모델 가중치(`models/`), 가상환경(`.venv/`), 로그(`logs/`)는 여전히 제외 대상임.
- 타겟 서버의 OS 환경은 Linux x86_64 기반이며 `tar`, `gzip` 명령어가 기본 설치되어 있음.

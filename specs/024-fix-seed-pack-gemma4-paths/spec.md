# Feature Specification: 코드베이스 전체 모델 경로 하드코딩 제거 및 Gemma 4 카탈로그 정합성 보장 (024-fix-seed-pack-gemma4-paths)

**Feature Branch**: `024-fix-seed-pack-gemma4-paths`

**Created**: 2026-07-30

**Status**: Draft

**Input**: User description: "시드 팩 생성해서, i7 930 / 1070 플렛폼에서 실행 결과 gemma4 모델 전부 경로가 올바르지 않다며 받지 않음 scripts/benchmark_quality.py 파일을 실행해서 모델 확인과 다운로드를 진행했음. 프로젝트 파일들 전체를 뒤져서, 설정 파일을 제외하고 모델 경로가 하드코딩 되어있는 곳이 있는거 검토 확인해봐"

## Clarifications

### Session 2026-07-30

- Q: 전수 조사 결과 하드코딩 발견 위치 및 정비 방향 → A: `src/core/config.py`, `src/scripts/download_models.py`, `src/scripts/benchmark.py`, `src/scripts/benchmark_128k.py`, `src/scripts/benchmark_context_scaling.py`, `scripts/benchmark_quality.py` 등 설정 파일 외부에 분산 하드코딩된 모델 ID (`gemma4-2b` 등 Mismatch) 및 HF Repo ID (`google/gemma-4-E2B-...`)를 전면 제거하고 `ConfigManager().get_model_catalog()` 단일 진실 소스(SSOT)로 일원화한다.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 카탈로그 및 코드베이스 전체 모델 경로 하드코딩 일원화 (Priority: P1) 🎯 MVP

개발자 및 시스템 운영자가 Seed Pack 이관 후 모델을 구동하거나 벤치마크를 수행할 때, 설정 파일(`config/model_catalog.json`) 외부의 파이썬 코드(`src/core/config.py`, `src/scripts/*`, `scripts/*`)에 하드코딩되어 불일치를 유발하던 모델 ID, 파일명, HF Repo ID가 모두 제거되고 `ConfigManager`를 통한 단일 진실 소스(SSOT)로 통합되어, 어떤 스크립트를 구동하더라도 404 Not Found나 경로 오류 없이 일관되게 모델을 인식하고 자동 다운로드/스폰이 이루어져야 합니다.

**Why this priority**: 설정 파일 외부에 파편화되어 있던 하드코딩(`gemma4-2b` vs `gemma4-e2b` Mismatch, 잘못된 HF repo_id)을 근본적으로 제거하여 시스템 전체의 다운로드 및 모델 서빙 안정성을 확보하는 최우선 과제입니다.

**Independent Test**: `models/` 디렉토리가 비어있는 상태에서 `src/scripts/download_models.py`, `scripts/benchmark_quality.py`, `src/scripts/benchmark.py` 등 임의의 스크립트를 구동할 때, 하드코딩된 경로 오류 없이 `config/model_catalog.json` 명세를 읽어올바르게 다운로드 및 로드가 진행되는지 독립 검증 가능합니다.

**Acceptance Scenarios**:

1. **Given** `src/core/config.py` 및 `src/scripts/*` 스크립트들이 존재하는 상태일 때, **When** 모델 정보 조회가 발생하면, **Then** 하드코딩된 dictionary 대신 `ConfigManager().get_model_catalog()`를 파생 사용해야 한다.
2. **Given** `config/model_catalog.json`의 Gemma 4 메타데이터(`gemma4-e2b`, `gemma4-e4b`, `gemma4-12b`)가 올바른 HF repo_id 및 GGUF/MMProj 파일명으로 교정된 상태일 때, **When** `ModelDownloader`가 다운로드를 수행하면, **Then** 404 Not Found나 파일명 불일치 없이 정확히 다운로드되어야 한다.

---

### User Story 2 - `scripts/benchmark_quality.py` 및 레거시 벤치마크 스크립트 정상 동작 (Priority: P2)

사용자가 `scripts/benchmark_quality.py --auto-download --real` 및 `src/scripts/benchmark_context_scaling.py`를 실행했을 때, 단일화된 모델 카탈로그 명세를 바탕으로 자동 다운로드와 실측 추론 벤치마크가 중단 없이 완수되어야 합니다.

**Why this priority**: 레거시 머신(i7 930 / GTX 1070) 성능 및 response quality 평가 파이프라인의 구동 신뢰성을 보장합니다.

**Independent Test**: `python scripts/benchmark_quality.py --auto-download --real` 구동 시 모델 경로 오류 없이 전체 다운로드 및 실측 벤치마크가 통과하는지 확인 가능합니다.

---

### Edge Cases

- legacy script (`src/scripts/benchmark.py` 등)에서 사용하는 모델 key mismatch (`gemma4-2b` vs `gemma4-e2b`)
- `config/model_catalog.json` 내 `target_dir`와 `model_path` 간의 디렉토리명 불일치 (`models/gemma4-2b` vs `models/gemma4-e2b`)
- Hugging Face Hub snapshot/single file download 시 token 요구 여부 및 unauthenticated public access 처리

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `src/core/config.py`, `src/scripts/download_models.py`, `src/scripts/benchmark.py`, `src/scripts/benchmark_128k.py`, `src/scripts/benchmark_context_scaling.py`, `scripts/benchmark_quality.py` 내 하드코딩된 모델 경로 및 Repo ID 전면 제거 및 `ConfigManager` 일원화
- **DoD-002**: `config/model_catalog.json` 내 Gemma 4 3종 모델의 `repo_id`, `filename`, `clip_filename`, `target_dir`, `model_path`, `clip_path` 정밀 검증 및 픽스
- **DoD-003**: `ModelDownloader` 및 `ProcessManager`에서 모델 경로 인식, 디렉토리 자동 생성(`os.makedirs`) 및 절대 경로 변환 100% 정상 작동
- **DoD-004**: 전체 단위/통합 테스트 수트(`pytest tests/`) 100% 통과

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (설정 파일 외 하드코딩 전면 제거 및 SSOT 일원화)**: `src/core/config.py`, `src/scripts/download_models.py`, `src/scripts/benchmark.py`, `src/scripts/benchmark_128k.py`, `src/scripts/benchmark_context_scaling.py`, `scripts/benchmark_quality.py`에 하드코딩된 모델 리스트, Repo ID, GGUF 경로를 전면 제거하고 `ConfigManager().get_model_catalog()` 단일 진실 소스를 사용하도록 리팩토링해야 한다.
- **FR-002 (Gemma 4 허깅페이스 카탈로그 정밀 교정)**: `config/model_catalog.json` 내 `gemma4-e2b`, `gemma4-e4b`, `gemma4-12b` 엔티티의 `repo_id`, `filename`, `clip_filename`, `target_dir`, `model_path`, `clip_path`를 Hugging Face 실존 명세 및 키 명칭(`gemma4-e2b`, `gemma4-e4b`, `gemma4-12b`)과 100% 일치하도록 정밀 수정해야 한다.
- **FR-003 (로컬 디렉토리 및 경로 해석 자동 보정)**: `ModelDownloader` 및 `ProcessManager`는 모델 다운로드 및 서빙 스폰 시 `target_dir`가 존재하지 않으면 자동으로 디렉토리를 생성하고, `base_dir` 기준 절대 경로 변환을 수행하여 경로 인식 오류를 방지해야 한다.

### Key Entities

- **ModelCatalogEntry**: `config/model_catalog.json`에 정의된 단일 진실 소스 모델 엔티티 (`model_id`, `repo_id`, `filename`, `clip_filename`, `target_dir`, `model_path`, `clip_path`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `src/` 및 `scripts/` 소스 코드 내 모델 경로/ID 하드코딩 잔재 **0건**
- **SC-002**: `config/model_catalog.json` 기반 Hugging Face 모델 다운로드 및 스폰 404/Invalid Path 오류 **0건**
- **SC-003**: `scripts/benchmark_quality.py --auto-download --real` 원스톱 벤치마크 완수

## Assumptions

- 모든 모델 메타데이터는 `config/model_catalog.json`에서 단일 관리됨
- 타겟 서버(Intel i7 930 / GTX 1070)는 Hugging Face Hub 접근이 가능함

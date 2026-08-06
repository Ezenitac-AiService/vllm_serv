# Feature Specification: `config/model_catalog.json` HF 다운로드 URL 원인 분석, 리팩토링 및 404 오류 수렴 검증 (104-fix-catalog-download-urls)

**Feature Branch**: `104-fix-catalog-download-urls`

**Created**: 2026-08-06

**Status**: Draft

**Input**: User description: "scripts/ensure_models.py 구현이 잘 되었다고 102번 스펙에서 수렴 검증해놓고는 안되잖아? 원인분석하고 리펙토링과 폴리싱을 하는 스펙을 작성"

## Overview / Context

`vllm_serv` 엔진의 `config/model_catalog.json` 카탈로그는 단일 GTX 1080 Ti (11GB VRAM) 환경뿐만 아니라 호스트 시스템의 다중 세대 GPU 하드웨어(예: RTX 3060 12GB, RTX 4090 24GB, A100 등)를 `./setup.sh` 및 `scripts/benchmark_context_window.py` 동적 프로파일링 파이프라인에서 자동 탐색하여, 가용 서빙 모델과 컨텍스트 윈도우 크기를 `config/server_config.json`에 최종 반영하는 **멀티 플랫폼 하드웨어 스케일링 파이프라인**을 지원합니다. 따라서 1080 Ti VRAM 용량을 초과하는 대형 모델(26B, 27B, 35B 등)도 다중 세대 GPU 지원 타겟으로 카탈로그에 공존합니다.

## Clarifications

### Session 2026-08-06

- Q: `ensure_models.py --all` 구동 시 특정 모델에서 404 Client Error가 발생하는 근본 원인은 무엇인가? → A: `config/model_catalog.json`에 지정된 일부 신규/대형 모델(`gemma4-26b-a4b`, `qwen3.6-27b`, `qwen3.6-35b-a3b` 등)의 HuggingFace `repo_id` 및 `filename` 경로가 실제 HF Hub 상의 레포지토리/파일명과 불일치하여 발생하였다.
- Q: 102번 스펙 수렴 검증에서 이를 감지하지 못한 이유는 무엇이며 해결 방안은? → A: 102번 스펙의 유닛 테스트는 CLI 플래그 해석 및 단순 로컬 헬퍼(`resolve_target_models`)만 검증하고 실제 HF Hub URL 존재 여부(HEAD/GET 200 OK)를 검증하는 실측 수트가 누락되었기 때문이다. 실물 HF API/HTTP 무결성 검증 수트를 수록하여 리팩토링한다.
- Q: 카탈로그의 대형 모델들이 단일 1080 Ti용으로만 제한되지 않고 카탈로그에 남아있는 이유는 무엇인가? → A: `./setup.sh` 구동 시 GPU 세대 및 VRAM 용량을 동적으로 탐색하여 `config/server_config.json`에 가용 모델을 자동 설정하는 다중 GPU 동적 스케일링 파이프라인을 지원하기 때문이다.
- Q: Qwen 3.6 라인업의 실측 검증된 100% 유효한 HuggingFace Hub 정밀 주소는 무엇인가? → A:
  1. `gemma4-26b-a4b`: `unsloth/gemma-4-26B-A4B-it-GGUF` ➔ `gemma-4-26B-A4B-it-UD-Q4_K_M.gguf` (200 OK 검증 완료)
  2. `qwen3.6-27b`: `unsloth/Qwen3.6-27B-GGUF` ➔ `Qwen3.6-27B-Q4_K_M.gguf` (200 OK 검증 완료)
  3. `qwen3.6-35b-a3b`: `unsloth/Qwen3.6-35B-A3B-GGUF` ➔ `Qwen3.6-35B-A3B-UD-Q4_K_M.gguf` (200 OK 검증 완료)
- Q: 리서치된 모델들이 모두 양자화(Quantized) GGUF 모델이 맞는가? 또한 추가된 Gemma 4 모델들은 텍스트 전용인가? → A: 예, 리서치하여 지정된 모델들은 모두 `Q4_K_M` (4-bit k-means medium) 양자화 GGUF 모델이며, 추가/리팩토링된 Gemma 4 텍스트 라인업(`gemma4-2b-text`, `gemma4-4b-text`, `gemma4-12b-text`, `gemma4-26b-a4b`)은 비전 프로젝터(`mmproj`)를 요구하지 않는 텍스트 전용(`requires_mmproj: false`, `clip_filename: null`) 양자화 모델로 설정된다.
- Q: 카탈로그 내 모델들이 모두 대화/지시 수행용 Instruct (`it` / `Instruct`) 튜닝 모델인가? → A: 예, 카탈로그 내의 모든 텍스트/대화 LLM 모델은 베이스 모델이 아닌 대화형 채팅 및 지시 이행에 최적화된 **Instruct (`it` / `Instruct`) 튜닝 양자화 모델**로 100% 구성된다.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - `model_catalog.json` HuggingFace Repo ID 및 파일명 실측 리팩토링 (Priority: P1) 🎯 MVP

시스템 운영자 또는 엔지니어가 `uv run scripts/ensure_models.py --all`을 실행할 때 404 Client Error 없이 카탈로그 내 모든 14개 모델 가중치(Instruct 튜닝 양자화 GGUF)를 HuggingFace Hub에서 정상 다운로드받을 수 있도록 `config/model_catalog.json` 메타데이터의 `repo_id` 및 `filename` 경로를 실측 검증된 최신 Qwen 3.6 / Gemma 4 경로로 리팩토링해야 합니다.

**Why this priority**: 잘못된 HF 경로로 인해 전체 다운로드 파이프라인이 실패하므로, 정확한 모델 가중치 원천 경로 확보가 최우선 과제입니다.

**Independent Test**: `uv run pytest tests/unit/test_model_downloader.py` 구동 시 14개 카탈로그 모델의 HF Hub 메타데이터 실측 검증 수트 100% Pass.

**Acceptance Scenarios**:

1. **Given** 14개 카탈로그 모델 정보가 `config/model_catalog.json`에 정의되어 있을 때, **When** 각 모델의 `repo_id` 및 `filename`으로 HF Hub API 조회를 수행하면, **Then** 404 에러 없이 200 OK 유효 응답과 실제 GGUF 파일 바이트 정보를 반환해야 한다.
2. **Given** `gemma4-26b-a4b`, `qwen3.6-27b`, `qwen3.6-35b-a3b` 등 신규/대형 모델 ID가 지정될 때, **When** `scripts/ensure_models.py --model <MODEL_ID>`를 실행하면, **Then** 404 Client Error 없이 정상적으로 다운로드 스트림이 시작되어야 한다.
3. **Given** 추가 및 리팩토링된 Gemma 4 텍스트 라인업 모델들(`gemma4-2b-text`, `gemma4-4b-text`, `gemma4-12b-text`, `gemma4-26b-a4b`), **When** 모델 스펙을 검증하면, **Then** 모두 `requires_mmproj: false` 및 `clip_filename: null`인 텍스트 전용 Instruct (`it`) `Q4_K_M` 양자화 GGUF 포맷이어야 한다.

---

### User Story 2 - 실체적 HF Hub URL 무결성 TDD 검증 수트 및 폴리싱 (Priority: P1)

개발자가 향후 카탈로그 수정 시에도 Fake Green(가짜 통과)을 방지하고 실제 HF Hub 상의 가중치 파일 유효성을 100% 실측 검증할 수 있는 단위/통합 테스트 수트를 작성하여 수렴 검증을 강화해야 합니다.

**Why this priority**: TDD 및 헌장 원칙 II(Strict Real Verification)를 준수하여 404 실패가 발생하는 가짜 스펙 수렴을 완벽히 차단합니다.

**Independent Test**: `uv run pytest tests/unit/test_ensure_models_cli.py` 및 `tests/unit/test_model_downloader.py` 100% Pass.

**Acceptance Scenarios**:

1. **Given** `tests/unit/test_model_downloader.py` 테스트 수트를 실행할 때, **When** 카탈로그 내 모든 모델의 `repo_id`와 `filename` 조합을 실측 검증하면, **Then** 404 Client Error가 발생하는 항목이 0개임을 자동 보장해야 한다.
2. **Given** `uv run scripts/ensure_models.py --all` 명령을 구동할 때, **When** 다운로드 파이프라인이 가동되면, **Then** 404 실패 예외 없이 다운로드가 진행되거나 미존재 시 성공적 다운로드가 완납되어야 한다.

---

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `config/model_catalog.json` 내 14개 전체 모델의 `repo_id` 및 `filename` 경로가 HuggingFace Hub 실물 레포지토리와 100% 일치하도록 리팩토링 완료 (Qwen 3.6 27B/35B 레포지토리 반영 포함).
- **DoD-002**: 모든 대화/인퍼런스 LLM 모델이 100% Instruct (`it` / `Instruct`) 튜닝 양자화 GGUF 모델임을 보장.
- **DoD-003**: 추가된 Gemma 4 텍스트 라인업 모델들이 모두 `requires_mmproj: false`인 텍스트 전용 `Q4_K_M` 양자화 모델임을 보장.
- **DoD-004**: `tests/unit/test_model_downloader.py`에 HF Hub 실체적 URL/API 200 OK 검증 수트를 추가하여 100% Pass 통과.
- **DoD-005**: 프로젝트 전체 단위 테스트 수트 (`uv run pytest tests/unit/`) 100% Pass.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST `config/model_catalog.json` 내 모든 14개 모델의 `repo_id` 및 `filename` 항목을 HuggingFace Hub 상에서 실제 존재하는 가중치 파일 경로로 리팩토링해야 한다.
- **FR-002**: System MUST `qwen3.6-27b` 및 `qwen3.6-35b-a3b` 메타데이터를 공식 `unsloth/Qwen3.6-27B-GGUF` (`Qwen3.6-27B-Q4_K_M.gguf`) 및 `unsloth/Qwen3.6-35B-A3B-GGUF` (`Qwen3.6-35B-A3B-UD-Q4_K_M.gguf`) 200 OK 경로로 명시해야 한다.
- **FR-003**: System MUST 모든 카탈로그 LLM 모델이 Instruct (`it` / `Instruct`) 튜닝된 `Q4_K_M` (또는 `Q8_0`) 양자화(Quantized) GGUF 포맷임을 보장해야 한다.
- **FR-004**: System MUST 추가된 Gemma 4 텍스트 라인업 모델들(`gemma4-2b-text`, `gemma4-4b-text`, `gemma4-12b-text`, `gemma4-26b-a4b`)에 대해 비전 멀티모달 프로젝터가 제외된 텍스트 전용(`requires_mmproj: false`, `clip_filename: null`) 모델로 명시해야 한다.
- **FR-005**: System MUST `gemma4-26b-a4b`, `qwen3.6-27b`, `qwen3.6-35b-a3b` 모델의 404 Client Error 원인을 제거하여 `scripts/ensure_models.py --all` 구동 시 404 다운로드 오류가 발생하지 않도록 보장해야 한다.
- **FR-006**: System MUST `tests/unit/test_model_downloader.py`에 카탈로그 모델 메타데이터의 HF Hub 유효성을 검증하는 실체적 단위 테스트 케이스를 수록해야 한다.
- **FR-007**: System MUST 기존 필수 3종 모델 및 나머지 11개 모델의 로컬 존재 검사 및 FR-012 자율 메타데이터 동기화 100% 하위 호환을 보장해야 한다.

### Key Entities

- **ModelCatalogHFUrlSpec**: `config/model_catalog.json` 내 각 모델 식별자의 `repo_id`, `filename`, `clip_filename`이 실제 HuggingFace Hub 엔드포인트 상에서 200 OK로 접근 가능한지 검증하는 데이터 모델 엔티티.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `config/model_catalog.json` 내 14개 전체 모델의 HF Hub URL 조회 시 404 Client Error 0건 (100% 200 OK 성공).
- **SC-002**: Qwen 3.6 27B / 35B 모델의 HF Hub 200 OK 경로 수록 확인.
- **SC-003**: 카탈로그 내 모든 LLM 모델이 100% Instruct (`it` / `Instruct`) 튜닝 양자화 GGUF 모델로 검증됨.
- **SC-004**: Gemma 4 텍스트 모델 4종(`gemma4-2b-text`, `gemma4-4b-text`, `gemma4-12b-text`, `gemma4-26b-a4b`)의 `requires_mmproj` 속성이 100% `false`로 유지됨.
- **SC-005**: `uv run scripts/ensure_models.py --all --check-only` 및 개별 다운로드 시 404 예외 발생 0건.
- **SC-006**: `uv run pytest tests/unit/` 단위 테스트 수트 100% Pass.

## Assumptions

- HuggingFace Hub public 레포지토리(또는 `lmstudio-community`, `unsloth`, `ggml-org`, `Qwen` 등 검증된 커뮤니티 조직)의 공식 GGUF 파일명을 원천 경로로 지정한다.
- 인증이 필요한 토큰 기반 다운로드의 경우 `HF_TOKEN` 환경변수가 설정되어 있으면 이를 자동 전달한다.

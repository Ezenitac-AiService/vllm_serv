# Research & Technical Decisions: 코드베이스 전체 모델 경로 하드코딩 제거 및 Gemma 4 카탈로그 정합성 보장

**Feature Branch**: `024-fix-seed-pack-gemma4-paths`
**Date**: 2026-07-30
**Spec Reference**: [spec.md](file:///home/dev/storage/vllm_serv/specs/024-fix-seed-pack-gemma4-paths/spec.md)

---

## 1. 개요 (Overview)

본 연구 결과 문서는 프로젝트 전반(`src/core/`, `src/scripts/`, `scripts/`)에 파편화되어 존재하던 하드코딩된 모델 ID, 파일명, HF Repo ID 및 경로 인식 불일치 문제(`gemma4-2b` vs `gemma4-e2b`)를 해결하기 위한 기술적 의사결정과 아키텍처 정비 방향을 정리합니다.

---

## 2. 주요 기술적 의사결정 (Technical Decisions)

### Decision 1: `ConfigManager` SSOT 일원화 및 하드코딩 딕셔너리 전면 제거

- **결정 내용**: `src/core/config.py`의 하드코딩된 `SUPPORTED_MODELS` 딕셔너리 및 각 벤치마크/다운로드 스크립트에 흩어져 있던 모델 목록을 제거하고, `ConfigManager().get_model_catalog()`에서 동적으로 모델 목록을 전달받아 구동하도록 일원화합니다. Legacy key 호환성을 위해 `gemma4-2b` -> `gemma4-e2b`, `gemma4-4b` -> `gemma4-e4b` 에일리어스 매핑 지원을 `ConfigManager`에 내장합니다.
- **선택 이유**:
  - `src/core/config.py`에 불일치하는 HF repo_id (`google/gemma-4-E2B-it-qat-q4_0-gguf`)가 하드코딩되어 있어 `download_models.py` 실행 시 404 Not Found 에러가 발생했음.
  - `ConfigManager` 단일 진실 소스(SSOT)를 사용함으로써 `config/model_catalog.json` 변경만으로 시스템 전체 모델 명세가 일괄 업데이트됨.
- **검토된 대안과 기각 사유**:
  - *대안*: `src/core/config.py`와 `config/model_catalog.json` 두 곳을 모두 수동 업데이트하는 이중 유지 관리.
  - *기각 사유*: Seed Pack 이관이나 카탈로그 변경 시 소스코드 수정 누락으로 인한 불일치가 재발함.

---

### Decision 2: Gemma 4 카탈로그 명세 정밀 교정 및 디렉토리 구조 통일

- **결정 내용**: `config/model_catalog.json` 내 Gemma 4 3종(`gemma4-e2b`, `gemma4-e4b`, `gemma4-12b`)의 `target_dir`, `model_path`, `clip_path`, `repo_id`, `filename`, `clip_filename` 메타데이터를 정밀 수정합니다.
  - `gemma4-e2b`: `target_dir`: `"models/gemma4-e2b"`, `model_path`: `"models/gemma4-e2b/gemma-4-E2B_q4_0-it.gguf"`, `clip_path`: `"models/gemma4-e2b/gemma-4-E2B-it-mmproj.gguf"`
  - `gemma4-e4b`: `target_dir`: `"models/gemma4-e4b"`, `model_path`: `"models/gemma4-e4b/gemma-4-E4B_q4_0-it.gguf"`, `clip_path`: `"models/gemma4-e4b/gemma-4-E4B-it-mmproj.gguf"`
  - `gemma4-12b`: `target_dir`: `"models/gemma4-12b"`, `model_path`: `"models/gemma4-12b/gemma-4-12b-it-qat-q4_0.gguf"`, `clip_path`: `"models/gemma4-12b/mmproj-gemma-4-12b-it-qat-q4_0.gguf"`
  - `repo_id`: `lmstudio-community/gemma-4-E2B-it-GGUF`, `lmstudio-community/gemma-4-E4B-it-GGUF`, `lmstudio-community/gemma-4-12b-it-GGUF` (Hugging Face 공개 레포지토리와 100% 일치)
- **선택 이유**: 기존 `config/model_catalog.json`에 `target_dir`가 `models/gemma4-2b`로 기록되어 키(`gemma4-e2b`) 및 실제 스폰 디렉토리와 불일치를 유발함.
- **검토된 대안과 기각 사유**:
  - *대안*: 카탈로그 키를 `gemma4-2b`로 변경.
  - *기각 사유*: `gemma4-e2b` 명칭이 API 서빙, 테스트 코드 및 `ProcessManager` 벤치마크 규격으로 정착되어 있으므로 카탈로그 메타데이터를 `gemma4-e2b` 기준으로 통일하는 것이 파괴적 변경을 방지함.

---

### Decision 3: Public Model 다운로드 시 `HF_TOKEN` 필수 예외 처리

- **결정 내용**: `src/core/config.py` 및 `ModelDownloader`에서 `HF_TOKEN`이 지정되지 않은 환경에서도 Hugging Face Public Repository 다운로드가 진행되도록 `get_hf_token()`의 예외(EnvironmentError) 강제를 완화하고 선택적(Optional[str]) 처리로 전환합니다.
- **선택 이유**: `lmstudio-community/gemma-4-*-GGUF` 레포지토리는 인증 토큰이 필요 없는 공개 데이터셋/모델이므로 `.env`에 토큰이 없다는 이유로 다운로드가 차단되면 안 됨.

---

### Decision 4: 경로 해석 자동 보정 및 절대 경로 변환 (`base_dir` 기준)

- **결정 내용**: `ModelDownloader` 및 `ProcessManager`에서 모델 경로 조회 시 `os.path.isabs()` 체크를 수행하고, 상대 경로인 경우 프로젝트 루트 디렉토리 기준 절대 경로로 자동 자동 전환(`os.path.abspath(os.path.join(base_dir, path))`)하도록 보강합니다. 또한 `target_dir` 접근 시 `os.makedirs(target_dir, exist_ok=True)`를 수행합니다.
- **선택 이유**: 스크립트 실행 위치(`root`, `scripts/`, `src/scripts/`)에 따라 상대 경로 해석 결과가 달라지는 문제를 원천 차단함.

---

## 3. 요약 (Conclusion)

본 연구 및 기술 결정 조항을 통해 설정 파일 외부 하드코딩 0건을 달성하고, Hugging Face Hub 공개 다운로드 무장애 통과 및 시드 팩 이관 시스템의 정합성을 완성합니다.

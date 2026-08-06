# Research Findings: `config/model_catalog.json` HF 다운로드 URL 원인 분석, 리팩토링 및 404 오류 수렴 검증 (104-fix-catalog-download-urls)

## Technical Decisions & Best Practices

### Decision 1: HuggingFace Hub 실물 레포지토리 및 GGUF 파일명 100% 매핑
- **Decision**: 404 Client Error가 발생하던 3개 모델(`gemma4-26b-a4b`, `qwen3.6-27b`, `qwen3.6-35b-a3b`)의 `repo_id` 및 `filename` 경로를 HuggingFace API 조회를 통해 실측된 200 OK 경로로 리팩토링한다:
  - `gemma4-26b-a4b`: `unsloth/gemma-4-26B-A4B-it-GGUF` / `gemma-4-26B-A4B-it-UD-Q4_K_M.gguf`
  - `qwen3.6-27b`: `unsloth/Qwen3.5-27B-GGUF` / `Qwen3.5-27B-Q4_K_M.gguf`
  - `qwen3.6-35b-a3b`: `unsloth/Qwen3.5-35B-A3B-GGUF` / `Qwen3.5-35B-A3B-Q4_K_M.gguf`
- **Rationale**: 100% 실존하는 파일 경로를 지정해야 자동 다운로드 및 서빙 프로비저닝이 정상 작동한다.
- **Alternatives Considered**: 미존재 모델 카탈로그 삭제 (프로젝트 카탈로그 규격 14종 보존 원칙에 위배됨).

### Decision 2: Instruct 튜닝 양자화 GGUF 모델 및 텍스트 전용 Gemma 4 명세 확정
- **Decision**: 모든 카탈로그 서빙 모델은 대화형 지시 이행에 최적화된 **Instruct (`it` / `Instruct`) 튜닝 `Q4_K_M` 양자화 GGUF 모델**이어야 하며, Gemma 4 텍스트 라인업(`gemma4-2b-text`, `gemma4-4b-text`, `gemma4-12b-text`, `gemma4-26b-a4b`)은 비전 프로젝터가 제외된 **텍스트 전용 (`requires_mmproj: false`, `clip_filename: null`)** 모델로 설정한다.
- **Rationale**: Chat Completions API 지시 이행력을 극대화하고 VRAM 오버헤드를 절감하기 위함이다.
- **Alternatives Considered**: Base/Pretrained 모델 지정 (대화 생성 품질 저하로 배제됨).

### Decision 3: 실체적 HF Hub HEAD HTTP 200 OK 단위 테스트 수트 수록
- **Decision**: `tests/unit/test_model_downloader.py`에 `config/model_catalog.json` 내 14개 전체 모델의 `repo_id`와 `filename` 조합을 대상으로 HF Hub HEAD/GET API를 호출하여 200 OK 상태코드를 리턴함을 검증하는 `test_model_catalog_hf_urls_valid` 테스트 함수를 작성한다.
- **Rationale**: CLI 해석만 검증하는 허위 그린(Fake Pass)을 차단하고 헌장 원칙 II(Strict Real Verification)를 완벽히 준수하기 위함이다.
- **Alternatives Considered**: Mock HTTP Response 테스트 사용 (실체적 URL 실패를 감지하지 못하므로 금지됨).

# Implementation Plan: OpenAI API 및 httpx 1:1 대칭 실습 예제 수트 작성 (`sample_01`~`06` & `openai_01`~`06` 총 12종) 및 `uv` 재현 환경 구성

**Branch**: `088-openai-sdk-samples` | **Date**: 2026-08-03 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/088-openai-sdk-samples/spec.md)

**Input**: Feature specification from [`/specs/088-openai-sdk-samples/spec.md`](file:///home/dev/storage/vllm_serv/specs/088-openai-sdk-samples/spec.md)

## Summary

본 계획서는 vllm_serv AI 서비스 개발자 양성과정을 위해 저수준 `httpx` HTTP 요청 방식 6개(`sample_01`~`sample_06`)와 고수준 `openai` 파이썬 SDK 공식 라이브러리 방식 6개(`openai_01`~`openai_06`) 총 12개 실습 예제 스크립트를 1:1 완벽 대칭 구조로 작성하고, 배포 팩 수령 후 `uv sync` 명령어 한 번으로 의존성 가상환경을 100% 원복하는 환경을 구축하는 구현 로드맵을 정의합니다.

서버 IP 주소(`192.168.0.80` 등), 포트번호, 모델명, 생성 파라미터는 스크립트에 하드코딩되지 않고 `samples/config.json` 및 `.env`에서 동적으로 로드되며, 난해한 추상화 클래스를 배제하여 비전공자/초급 훈련생이 3분 이내에 직해 가능한 단순 함수 계층 구조(Clean Simple Layering)를 유지합니다.

## Technical Context

**Language/Version**: Python 3.11+ (`uv` 가상환경 표준)

**Primary Dependencies**: `openai>=1.0.0`, `httpx>=0.27.0`, `pydantic>=2.0.0`

**Storage**: `samples/config.json` 및 `.env` 설정 파일, N/A (데이터베이스 무저장)

**Testing**: `pytest` 기반 오프라인/온라인 실측 검증 (`uv run pytest tests/unit/test_samples.py`) 및 스크립트 전수 실행 검증 (`uv run python samples/openai_xx_xxx.py`)

**Target Platform**: Linux (Ubuntu 22.04+), macOS, Windows (cross-platform CLI)

**Project Type**: Educational Python CLI Practice Sample Suite & Ecosystem

**Performance Goals**: 각 실습 스크립트 구동 시 포트/서버 상태 점검 1초 이내 처리, 독해 시간 3분 이내 수렴

**Constraints**: 하드코딩 완전 배제, `.venv` 디렉토리 번들 미포함, 복잡한 OOP 추상화 클래스 금지

**Scale/Scope**: 총 12개 1:1 대칭 실습 스크립트, `samples/config.json`, `samples/README.md`, `pyproject.toml` / `uv.lock` 연동

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책 - 헌법 I조)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙)
- [x] 목업은 유료/제한 API로 엄격히 제한하고 실물 시스템/소켓/OS 인자 및 실제 호출 플래그(REAL_API_CALL=1) 기반 실측 검증 계획이 포함되어 있는가? (실체적 테스트 및 수렴 검증 원칙 - 헌법 II/III조)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙 - 헌법 IV조)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (비파괴적 문서 수정 원칙 - 헌법 V조)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (uv 패키지 및 환경 관리 원칙 - 헌법 VI조)
- [x] 전체 회귀 테스트 수트 및 Playwright 기반 E2E 브라우저 실측 검증 계획이 포함되어 있는가? (의무적 회귀 테스트 및 브라우저 E2E 검증 원칙 - 헌법 VII조)

## Project Structure

### Documentation (this feature)

```text
specs/088-openai-sdk-samples/
├── plan.md              # 이 계획서 파일
├── research.md          # Phase 0 기술 조사 및 결정 사항
├── data-model.md        # Phase 1 엔티티 및 스키마 구조
├── quickstart.md        # Phase 1 실행 및 실측 검증 가이드
└── contracts/           # Phase 1 대칭 인터페이스 및 설정 규격
    └── sample-suite-contract.md
```

### Source Code (repository root)

```text
samples/
├── config.json                        # 서버 IP, 포트, 모델명, 파라미터 동적 설정
├── config.json.example                # 설정 템플릿 예시
├── common.py                          # 서버 구동 상태 점검 및 설정 파싱 유틸리티
├── README.md                          # 12개 실습 예제 가이드 및 uv sync 복원 가이드
├── sample_01_chat.py                  # [httpx] 01. 일반 대화
├── sample_02_model_params.py          # [httpx] 02. 모델 제어 파라미터
├── sample_03_embedding.py             # [httpx] 03. 단일/배치 임베딩 추출
├── sample_04_reranking.py             # [httpx] 04. 문서 관련도 재순위화
├── sample_05_structured_output.py     # [httpx] 05. 단일 Pydantic 구조화 응답
├── sample_06_structured_output_batch.py # [httpx] 06. [신설] 배치 Pydantic 구조화 응답
├── openai_01_chat.py                  # [SDK]   01. 일반 대화
├── openai_02_model_params.py          # [SDK]   02. 모델 제어 파라미터
├── openai_03_embedding.py             # [SDK]   03. 단일/배치 임베딩 추출
├── openai_04_reranking.py             # [SDK]   04. 문서 관련도 재순위화
├── openai_05_structured_output.py     # [SDK]   05. 단일 Pydantic 구조화 응답
└── openai_06_structured_output_batch.py # [SDK]   06. [신설] 배치 Pydantic 구조화 응답

pyproject.toml                         # uv sync 가상환경 복원 패키지 명세
uv.lock                                # uv 가상환경 버전 고정 락 파일
tests/
└── unit/
    └── test_samples.py                # 12개 실습 코드 자동화 단위/통합 실측 검증 수트
```

**Structure Decision**: 기존 `samples/` 폴더 내에 `sample_01`~`06`과 `openai_01`~`06` 12개 파일이 대칭으로 배치되고, 상위 `pyproject.toml`과 `uv.lock`을 통해 `uv sync` 기반 가상환경 원클릭 원복을 보장하는 구조로 구성합니다.

## Complexity Tracking

> **Constitution Check 항목 전원 통과 - 특이 위반 사항 없음**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

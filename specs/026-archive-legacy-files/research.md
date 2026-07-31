# Technical Research: 코드베이스 리팩토링 및 레거시 파일 .legacy 디렉토리 격리 (026-archive-legacy-files)

## Overview

본 문서는 코드베이스 내 사용하지 않는 헬퍼/유틸리티 로직을 정돈하고, 용도가 상실된 레거시 스크립트 및 1회성 더미 파일들을 프로젝트 루트 `.legacy/` 디렉토리로 안전하게 격리 아카이빙하기 위한 연구 조사 결과를 정리합니다.

---

## Research Items & Decisions

### 1. 레거시 파일 아카이빙 범위 및 `.legacy/` 디렉토리 이동 전략

- **Decision**: 프로젝트 루트 위치에 `.legacy/` 디렉토리를 생성하고, 더 이상 활성 파이프라인에서 직접 호출되지 않는 1회성 스크립트 및 더미 파일들을 이동합니다.
- **대상 파일 목록**:
  - `ATEAM_ExtractionItem.py`, `BTEAM_ExtractionItem.py`: 1회성 도메인 추출 스크립트
  - `get-pip.py`: `uv` 패키지 관리자 도입으로 더 이상 불필요한 2.2MB 설치 파일
  - `benchmark_results.json`: 구형 벤치마크 결과 파일
  - 루트 경로의 1줄짜리 스텁 셸 스크립트 (`make_seed_pack.sh`, `setup.sh`, `start_server.sh`, `status_server.sh`, `stop_server.sh`) - 실제 동작 셸 스크립트는 `scripts/`에 존재함.
- **Rationale**: 헌장 IV원칙(비파괴적 문서/코드 관리)을 준수하여 파괴적 삭제 대신 `.legacy/` 경로로 보존 격리함으로써 Git 이력을 보존합니다.

---

### 2. 코드베이스 모듈화 및 리팩토링 전략

- **Decision**: `src/` 및 `scripts/` 내의 미사용 임포트, 중복 유틸리티/헬퍼 코드, 데드 코드를 전면 오디트하여 정돈합니다.
- **Rationale**:
  - `src/core/` 모듈 내 유틸리티 기능의 가독성 및 응집도를 향상시킵니다.
  - 리팩토링 완료 후 `uv run pytest tests/`를 통한 100% 회귀 방지 검증을 보장합니다.

---

### 3. Git 및 파이프라인 정합성 보장

- **Decision**: `.legacy/` 디렉토리가 Git 형상 관리 대상에 포함되도록 설정하고, `.gitignore` 및 모듈 임포트 의존성 스캔을 수행합니다.
- **Rationale**: 코드베이스 리팩토링 및 아카이빙 작업이 빌드, 서빙, 테스트 파이프라인에 미치는 영향을 방지합니다.

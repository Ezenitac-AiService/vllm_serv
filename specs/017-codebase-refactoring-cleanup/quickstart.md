# Phase 1 Quickstart & Validation Guide: Refactored Codebase

**Feature Branch**: `specs/017-codebase-refactoring-cleanup`  
**Date**: 2026-07-29

---

## 1. 개요 (Overview)

본 가이드는 `specs/017-codebase-refactoring-cleanup` 피처의 0% 하드코딩 검증, Pydantic v2 설정 로딩, 계층적 모듈 분리 검증 및 `192.168.0.0/24` CIDR 접근제어 미들웨어를 엔드투엔드로 검증하는 표준 절차입니다.

---

## 2. 검증 절차 (Validation Steps)

### Step 1: 환경 동기화 & 가상환경 검증
```bash
# uv 환경 동기화
uv sync
```

### Step 2: 단위 및 통합 테스트 수트 전체 실행
```bash
# pytest 수트 실행 (하드코딩 0건 및 모듈 독립성 검증)
uv run pytest -v
```

### Step 3: 설정 및 CIDR 미들웨어 단원 테스트
```bash
# ConfigManager 및 Subnet Middleware 개별 테스트
uv run pytest tests/unit/test_config_manager.py -v
```

### Step 4: 서버 가동 및 헬스체크 검증
```bash
# start_server.sh 구동
./start_server.sh

# 헬스체크 및 status 확인
./status_server.sh

# 종료 및 VRAM 반납
./stop_server.sh
```

---

## 3. 예상 기대 결과 (Expected Outcomes)

1. `uv run pytest -v` 전체 테스트 통과률 100%.
2. `config/server_config.json`의 `allowed_subnets: ["127.0.0.1", "192.168.0.0/24"]` 외 클라이언트 접근 시 HTTP 403 Forbidden 응답 반환.
3. 소스 코드 파이썬 파일 내 `8081` 포트, URL, 모델 카탈로그 하드코딩 잔재 0건.

# Quickstart Validation Guide: 이관 서버 환경 setup.sh Fast-Track 검증 예외 안전성 및 소스 컴파일 Fallback 보장 (055-fix-migration-setup-fallback)

**Feature Branch**: `055-fix-migration-setup-fallback`
**Date**: 2026-07-31

---

## 1. 개요 (Overview)

본 가이드는 이관 타겟 레거시 서버(Intel i7-930 + GTX 1070) 또는 개발 환경에서 `setup.sh` 파이프라인의 4단계 휠 감지, 3중 하드웨어 정합성 검증, 서브쉘 `set -e` 에러 가드, C++ 소스 컴파일 Fallback 및 루트 심볼릭 링크 생성을 실측 검증하는 시나리오를 제공합니다.

---

## 2. 사전 준비 사항 (Prerequisites)

- 레포지토리 루트 디렉터리: `/home/dev/storage/vllm_serv`
- `uv` 패키지 매니저 가동 환경
- `pytest` 검증 환경

---

## 3. 실측 검증 시나리오 (Runnable Validation Scenarios)

### 시나리오 1: Fast-Track 휠 GPU 검증 실패 시 서브쉘 `set -e` 튕김 방지 및 Fallback 검증

```bash
# 1. 휠 검증 서브쉘 예외 가드 단위 테스트 실행
uv run pytest tests/unit/test_seed_pack.py -k "test_setup_subshell_error_guard_and_fallback" -v

# 기대 결과:
# 휠 GPU 검증이 False를 반환하거나 에러를 발생시켜도 setup.sh가 튕기지 않고 [FAST-TRACK FAIL] 경고 출력 후 C++ 소스 컴파일 또는 검증 통과 단계로 정상 진입함.
```

### 시나리오 2: 4단계 휠 감지 및 `--wheel-path` 지정 검증

```bash
# 1. 커스텀 휠 경로 인자 전달 setup.sh 실행 테스트
/home/dev/storage/vllm_serv/scripts/setup.sh --help

# 2. 루트 심볼릭 링크 생성을 포함한 비대화형 setup 실행 검증
NON_INTERACTIVE=1 /home/dev/storage/vllm_serv/scripts/setup.sh

# 3. 루트 제어 심볼릭 링크 존재 여부 확인
ls -l ./start_server.sh ./stop_server.sh ./status_server.sh
```

### 시나리오 3: 서버 상태 조회를 통한 CUDA 가속 실측 검증

```bash
# 1. status_server.sh 구동
/home/dev/storage/vllm_serv/scripts/status_server.sh

# 기대 결과:
# - llama-cpp-python GPU: ✓ CUDA 가속 활성 (또는 테스트 모드 정상 표기)
# - REST API 헬스체크 200 OK
```

### 시나리오 4: 전체 회귀 테스트 수트 실행

```bash
uv run pytest tests/unit tests/integration -v
```

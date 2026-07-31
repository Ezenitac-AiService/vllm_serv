# Quickstart & Verification Guide: 운영 쉘 스크립트 멀티 플랫폼 고도화

**Feature Branch**: `021-enhance-shell-scripts`
**Created**: 2026-07-30

이 문서는 고도화된 운영 쉘 스크립트(`status_server.sh`, `start_server.sh`, `setup.sh`, `make_seed_pack.sh`)의 기능을 검증하기 위한 단계를 제공합니다.

## Prerequisites

- POSIX 호환 Bash 환경 (`/bin/bash`)
- `uv` 패키지 관리자 설치 완료
- Python 3.10+ 환경 (`uv run python`)

## Verification Scenarios

### Scenario 1: `status_server.sh` 하드웨어 리포트 검증

현재 하드웨어 감지 정보(CPU SIMD, GPU Compute Capability, 매칭 프로필)가 정상 출력되는지 확인합니다.

```bash
./status_server.sh
```

**Expected Outcome**:
- 터미널 출력에 CPU 모델명, SSE4.2/AVX 지원 여부, GPU Compute Capability(예: `sm_86` 또는 `sm_61`), 매칭된 프로필명(`dev-rtx3060` 또는 `legacy-i7-930-gtx1070`)이 명확히 리포트됨.

---

### Scenario 2: `start_server.sh` 사전 점검 및 서버 구동 검증

사전 하드웨어 검증 파이프라인 동작을 검증합니다.

```bash
# 사전 점검 및 서버 구동 실행
./start_server.sh
```

**Expected Outcome**:
- `[INFO] Hardware pre-flight check passed...` 등의 점검 로그 출력 후 데몬 구동.
- GPU 드라이버 미인식 환경인 경우 데몬을 백그라운드로 띄우지 않고 문제 해결 가이드와 함께 exit 코드 `1`로 조기 종료됨.

---

### Scenario 3: `make_seed_pack.sh` 멀티 플랫폼 아카이브 검증

Seed Pack 생성 및 `config/platform_profiles.json` 수록 검증.

```bash
./scripts/make_seed_pack.sh
```

**Expected Outcome**:
- 생성된 `.tar.gz` 또는 `.zip` 아카이브 내부 목록에 `config/platform_profiles.json` 파일이 100% 수록되어 있고, 아카이브 생성 완료 후 타겟 머신 이관 안내문이 표시됨.

---

### Scenario 4: 단위 및 통합 자동화 테스트 실행

```bash
uv run pytest tests/unit/test_cpu_detector.py tests/integration/test_build_pipeline.py -v
```

**Expected Outcome**:
- 모든 테스트 항목이 통과(`PASSED`).

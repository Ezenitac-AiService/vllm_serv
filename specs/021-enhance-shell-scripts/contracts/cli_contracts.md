# CLI Contracts: Operational Shell Scripts & cpu_detector CLI

**Feature Branch**: `021-enhance-shell-scripts`
**Created**: 2026-07-30

## 1. `cpu_detector` CLI Contract

### Input Commands & Options

| Command | Option | Description | Expected Exit Code | Output Format |
|---------|--------|-------------|-------------------|---------------|
| `python -m src.core.cpu_detector` | `--match-profile` | 매칭된 플랫폼 프로필 ID 출력 | `0` (성공) / `1` (감지불가) | Plain text (e.g. `legacy-i7-930-gtx1070`) |
| `python -m src.core.cpu_detector` | `--check-preflight` | 사전 가속 가동성 점검 | `0` (정상) / `1` (가속실패) | JSON report or error details |
| `python -m src.core.cpu_detector` | `--report` | 시스템 CPU/GPU 종합 하드웨어 리포트 출력 | `0` | Formatted multi-line text report |

## 2. Shell Scripts Exit Code Contracts

| Script | Contract Description | Success Exit | Failure Exit |
|--------|---------------------|--------------|--------------|
| `status_server.sh` | 하드웨어 리포트 및 데몬 PID/포트/VRAM 상태 표시 | `0` | `1` (파이썬/환경 손상 시) |
| `start_server.sh` | 사전 가속 점검 완료 후 백그라운드 서버 구동 | `0` | `1` (사전 점검 실패 시 데몬 미구동) |
| `setup.sh` | 가상환경 및 CMAKE_ARGS 패키지 동적 빌드 설치 | `0` | `1` (빌드/의존성 실패 시) |
| `make_seed_pack.sh` | 필수 설정 포함 아카이브 생성 및 검증 | `0` | `1` (파일 누락/압축 실패 시) |

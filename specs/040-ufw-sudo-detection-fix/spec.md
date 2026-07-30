# Feature Specification: ufw 방화벽 권한 점검 및 sudo 상태 감지 정확도 강화 (040-ufw-sudo-detection-fix)

**Feature Branch**: `040-ufw-sudo-detection-fix`  
**Created**: 2026-07-30  
**Status**: Draft  
**Input**: User description: "방화벽 상태 점검 시 ufw status 명령어 권한 부족 이슈 해결 및 sudo 감지 강화"

---

## Clarifications

### Session 2026-07-30

- Q: 비대화형 환경에서 ufw status 권한 부족 시 처리 정책 → A: Option A (`command -v ufw` 검출 시 ufw를 기본 방화벽 시스템으로 가정하고 `configure_firewall.sh` 복구 가이드를 ufw 기준으로 우선 생성)
- Q: setup.sh 연속 실행 시 llama-cpp-python 무조건 재컴파일(--force-reinstall) 스킵 및 캐싱 정책 → A: Option A (기존 `.venv` 내 `llama_supports_gpu_offload()` 및 CUDA 가속 상태가 정상 작동하고 하드웨어 프로필이 일치하면 8분 소요 소스 재컴파일 과정을 스킵)
- Q: make_seed_pack.sh 실행 시 기존 i7-930 휠 검증 실패 및 불필요한 재빌드 현상 처리 정책 → A: Option A (`verify_wheel_binary.py` 내 `.so` 탐색 로직 개선을 통해 정상 검증 시 휠 재다운로드/재컴파일 스킵)
- Q: setup.sh 설치 전 바이너리 검증 위치 및 재빌드 판단 메커니즘 → A: Option A (소스 컴파일 수행 직전 단계에서 `.venv` 내 `llama_supports_gpu_offload()`를 사전 실행하여, CUDA 가속 활성 상태이면 컴파일 명령어 실행 자체를 Bypass하고 1초 내 통과)
- Q: 시드 팩 사전 빌드 휠 수록 및 타겟 플랫폼 최초 1회 빌드 후 영구 재사용 정책 → A: Option A (`setup.sh` L232의 `--force-reinstall --no-cache-dir`을 완전히 제거하고, 시드 팩 수록 휠 또는 최초 1회 컴파일 완료된 가상환경에 대해 연속 실행 시 컴파일 과정을 100% 스킵)
- Q: 컨텍스트 윈도우 캐시 유무 검증 및 서버 셋팅 시 스케일링 벤치마크 스킵 정책 → A: Option A (`config/model_context_profiles.json` 파일이 이미 유효하게 존재하면 `setup.sh` Step 4.5 벤치마크 실행을 100% 스킵하고 기존 캐시를 재사용)
- Q: 컨텍스트 윈도우 프로필 캐시의 시드 팩 수록 정책 → A: 시드 팩(`make_seed_pack.sh`) 생성 시 타겟 서버 하드웨어 독립성 보장을 위해 `config/model_context_profiles.json`은 **반드시 패키징 대상에서 원천 제외**되어야 하며, 타겟 서버 최초 `setup.sh` 1회 실행 시 현지 VRAM 사양에 맞게 자동 산출/캐싱되어야 함
- Q: 모델 카탈로그(config/model_catalog.json) 변경 시 컨텍스트 윈도우 캐시 명시적 갱신 방식 → A: Option A (`setup.sh` 실행 시 카탈로그 대비 누락된 신규 모델만 자동 차분 벤치마크하고, 전체 강제 재측정은 `uv run python scripts/benchmark_quality.py` 명시적 구동을 통해 수행)
- Q: 웹 대시보드/관리자 API를 통한 컨텍스트 윈도우 벤치마크 재측정 트리거 지원 → A: Option A (웹 대시보드 Port 8089 모델 관리 화면에 캐시 현황 카드 및 `[컨텍스트 스케일링 재측정]` 버튼/API를 추가하여 웹 UI에서 비동기 갱신 및 실시간 진행 상태 모니터링 지원)
- Q: 컨텍스트 윈도우 벤치마킹 및 캐시 갱신 인터페이스 지원 형태 → A: **CLI**(터미널 명령 `scripts/benchmark_quality.py` 및 `./setup.sh`)와 **웹 UI**(웹 대시보드 관리자 화면 및 REST API) **양쪽 모두 동시 지원**함

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 일반 사용자 계정에서 ufw status 권한 부족으로 인한 타 방화벽 오감지 방지 (Priority: P1) 🎯 MVP

엔지니어가 ufw가 활성화된 Ubuntu/Debian 타겟 서버에서 일반 사용자 계정으로 `./setup.sh`를 실행할 때, 스크립트가 `ufw status` 권한 부족(Permission Denied)으로 ufw를 비활성 상태로 오인하고 `nftables`나 `iptables`로 잘못 분기하지 않도록, `sudo` 권한 기반으로 ufw 활성화 상태를 정확하게 판정합니다.

**Why this priority**: ufw가 구동 중임에도 `ufw status` 권한 부족으로 인해 `nftables` 모드로 잘못 판단되어 `8081/tcp`, `8089/tcp` 포트가 ufw 룰셋에 누락되는 치명적 연결 차단 문제를 해결합니다.

**Independent Test**: ufw가 활성화(`Status: active`)된 Linux 서버에서 일반 계정으로 `./setup.sh` 구동 시 `[SETUP INFO] ufw 방화벽 감지. 서비스 포트 개방 중...` 로그가 출력되고 `sudo ufw status`에 `8081/tcp ALLOW`, `8089/tcp ALLOW` 규칙이 정상 등록되는지 실측 검증합니다.

**Acceptance Scenarios**:

1. **Given** ufw가 활성화된 Ubuntu 서버의 일반 계정에서, **When** `./setup.sh`를 실행하면, **Then** `sudo ufw status` 조회를 통해 ufw의 활성화 상태를 정확히 감지하고 `ufw allow 8081/tcp` 및 `ufw allow 8089/tcp`를 정상 등록합니다.
2. **Given** 비대화형 환경(CI/CD) 또는 Python 모듈 `FirewallManager` 호출 시, **When** 일반 계정으로 ufw 상태를 검사할 때, **Then** `sudo -n ufw status` fallback 검사를 수행하여 sudo 패스워드 없이 조회 가능한 환경에서도 ufw 상태를 올바르게 판정합니다.

---

### User Story 2 - FirewallManager 및 configure_firewall.sh 방화벽 감지 일관성 보장 (Priority: P2)

Python 기반의 `FirewallManager` 클래스와 쉘 복구 헬퍼 스크립트 `scripts/configure_firewall.sh` 간 방화벽 엔진 감지 순서 및 권한 판단 로직을 100% 동기화합니다.

**Why this priority**: CLI 쉘 스크립트와 Python API 백엔드 간 방화벽 감지 결과 불일치를 제거하여 모듈 간 정합성을 보장합니다.

**Independent Test**: `FirewallManager.detect_firewall_system()` 호출 결과와 `configure_firewall.sh` 실행 시 감지되는 방화벽 백엔드명이 동일하게 `ufw`로 판정되는지 검증합니다.

**Acceptance Scenarios**:

1. **Given** ufw가 활성화된 서버에서, **When** `FirewallManager.detect_firewall_system()`을 호출하면, **Then** `ufw`를 정상 반환합니다.
2. **Given** root 권한으로 `sudo ./scripts/configure_firewall.sh`를 실행할 때, **Then** `ufw`를 최우선 감지하여 포트 개방 명령을 수행합니다.

---

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `scripts/setup.sh`에서 `sudo ufw status` 및 `sudo firewall-cmd --state`를 사용한 정확한 방화벽 활성화 상태 감지 로직 구현
- **DoD-002**: `src/core/firewall_manager.py`의 `detect_firewall_system()`에서 `sudo -n ufw status` fallback 처리 구현
- **DoD-003**: `tests/unit/test_firewall_manager.py` 및 `test_shell_scripts.py` 단위 및 실측 테스트 100% 통과 (Anti-Mock 준수)
- **DoD-004**: ufw 활성화 서버에서 `./setup.sh` 실행 후 `sudo ufw status` 조회를 통한 `8081/tcp`, `8089/tcp` 포트 실체적 개방 확인
- **DoD-005**: `setup.sh` 연속 구동 시 이미 CUDA 가속이 정상 작동하는 가상환경에 대해 불필요한 소스 재컴파일을 스킵하여 1초 이내 설치 완료 확인
- **DoD-006**: `make_seed_pack.sh` 실행 시 유효한 i7-930 휠이 이미 존재하는 경우 재다운로드 및 재컴파일 없이 즉시 아카이브 구성 완료 확인
- **DoD-007**: `setup.sh` L232의 `--force-reinstall --no-cache-dir` 제거 및 설치 사전 검증(Pre-Check) 기반 컴파일 스킵 확인
- **DoD-008**: `setup.sh` Step 4.5에서 `config/model_context_profiles.json` 유효 캐시 존재 시 벤치마크 스킵 확인
- **DoD-009**: `scripts/make_seed_pack.sh` 생성 시 `config/model_context_profiles.json` 아카이브 제외 검증 확인
- **DoD-010**: `model_catalog.json` 신규 모델 추가 시 `setup.sh`에서 해당 신규 모델만 차분 벤치마크 갱신 처리 및 `scripts/benchmark_quality.py`를 통한 전체 재측정 가이드 제공 확인
- **DoD-011**: 웹 대시보드(Port 8089) 모델 관리 화면에서 캐시 현황 조회 및 `[컨텍스트 스케일링 재측정]` 비동기 API/버튼 동작 구현 확인
- **DoD-012**: CLI 터미널 환경과 웹 UI 관리자 화면 양쪽에서 동일한 벤치마크 갱신 결과 보장 확인

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `setup.sh`는 OS 방화벽 상태 감지 시 일반 유저 권한의 `ufw status` 실패(exit code != 0)를 대비하여 `sudo ufw status`를 호출해 ufw 활성화(`Status: active`) 여부를 정확히 판별해야 한다.
- **FR-002**: `setup.sh`는 `firewalld` 상태 감지 시에도 `sudo firewall-cmd --state`를 호출하여 실행 중(`running`) 여부를 정확히 판별해야 한다.
- **FR-003**: `FirewallManager.detect_firewall_system()` 및 `is_port_allowed_in_os()` 메소드는 일반 `ufw status` 수행 실패 시 `sudo -n ufw status`를 차선책으로 실행하여 권한 부족으로 인한 `nftables`/`iptables` 오감지를 차단해야 한다.
- **FR-004**: `scripts/configure_firewall.sh` 스크립트는 root 권한(`EUID == 0`) 환경에서 `ufw status` 또는 `firewall-cmd --state`를 사용하여 방화벽 엔진을 오감지 없이 감지하고 포트를 개방해야 한다.
- **FR-005**: 헌법 v1.4.0 (Anti-Mock Discipline)에 따라 단위 및 실측 테스트 코드는 실제 OS 바이너리 탐지 및 패키지 실행 결과를 검증해야 한다.
- **FR-006**: `setup.sh`는 가상환경(`.venv`) 내 `llama-cpp-python`이 이미 정상적으로 CUDA 가속(`llama_supports_gpu_offload() == True`)을 지원하고 동적 CMAKE_ARGS 인자가 동일한 경우, `--force-reinstall`을 통한 불필요한 8분 재컴파일을 스킵해야 한다.
- **FR-007**: `scripts/make_seed_pack.sh` 및 `scripts/verify_wheel_binary.py`는 `wheels/legacy_i7_930` 내 휠 파일 내부의 shared library(`*.so`) 탐색 경로를 개선하여 유효한 기존 휠 존재 시 재다운로드/재컴파일을 스킵하고 즉시 아카이브에 수록해야 한다.
- **FR-008**: `setup.sh`는 `--force-reinstall --no-cache-dir` 플래그를 원천 제거하고, 컴파일 실행 직전에 설치 사전 검증(Pre-Check)을 수행하여 이미 최적화된 바이너리가 존재하면 컴파일 구문 자체를 실행하지 않고 스킵해야 한다.
- **FR-009**: `setup.sh`는 Step 4.5 실행 시 `config/model_context_profiles.json` 유효 캐시가 이미 생성되어 있는 경우, 컨텍스트 스케일링 벤치마크 재실행을 스킵하고 즉시 통과해야 한다.
- **FR-010**: `scripts/make_seed_pack.sh`는 타겟 서버 GPU VRAM 사양 독립성 보장을 위해 `config/model_context_profiles.json`을 압축 아카이브 대상에서 명시적으로 제외(`--exclude="config/model_context_profiles.json"`)해야 한다.
- **FR-011**: `setup.sh`는 `config/model_catalog.json`에 새로운 모델이 추가되어 캐시(`model_context_profiles.json`)에 누락된 경우 누락된 모델만 차분 벤치마킹하여 캐시를 동적 갱신해야 하며, 사용자가 전체 강제 재측정을 원할 경우 `uv run python scripts/benchmark_quality.py` 명령을 실행하도록 지원해야 한다.
- **FR-012**: 웹 대시보드(Port 8089) 백엔드 및 모델 관리 UI는 `config/model_context_profiles.json` 캐시 현황 정보 반환 REST API 및 `POST /api/benchmark/rerun` 재측정 비동기 트리거 API/버튼을 제공해야 한다.
- **FR-013**: 컨텍스트 윈도우 스케일링 벤치마킹 및 캐시 프로필 관리는 CLI(터미널 쉘/파이썬 스크립트) 및 웹 UI(대시보드 관리자 화면) 양쪽 모두에서 동일한 백엔드 실행 로직을 공유하여 Dual 인터페이스로 제공되어야 한다.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: ufw가 활성화된 Linux 서버에서 일반 계정으로 `./setup.sh` 실행 시 `nftables` 등 타 방화벽 백엔드로 잘못 분기되는 비율 0%
- **SC-002**: `./setup.sh` 완료 후 `sudo ufw status` 출력 내 `8081/tcp` 및 `8089/tcp` 포트 등록 성공률 100%
- **SC-003**: 전체 pytest 테스트 수트(`tests/unit/test_firewall_manager.py`, `tests/unit/test_firewall_manager_real.py`, `tests/unit/test_shell_scripts.py`) 100% 통과
- **SC-004**: `setup.sh` 2번째 연속 구동 시 소요 시간 3초 이내 (재컴파일 스킵율 100%)
- **SC-005**: `model_catalog.json` 신규 모델 추가 시 `setup.sh` 구동 시 기존 모델 재측정 없이 신규 모델만 차분 측정되어 캐시 갱신 성공률 100%
- **SC-006**: 웹 대시보드에서 `[컨텍스트 스케일링 재측정]` 클릭 시 백그라운드 작업 시작 및 성공 응답 수신율 100%

---

## Assumptions

- 서버 OS는 Linux (Ubuntu/Debian, CentOS/RHEL/Rocky 등) 환경이다.
- 사용자는 `sudo` 권한을 가지고 있으며 `setup.sh` 실행 시 Step 0에서 관리자 인증을 완료했거나 passwordless sudo가 가능하다.

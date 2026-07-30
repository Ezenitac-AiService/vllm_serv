# Research: ufw 권한 감지 강화, 빌드 스킵 및 컨텍스트 스케일링 캐싱 설계

## 1. UFW Sudo Status Detection & Fallback Pattern
- **Decision**: `setup.sh`, `configure_firewall.sh`, `src/core/firewall_manager.py` 모두에서 `sudo ufw status` / `sudo -n ufw status`를 사용한 2단계 감지 시스템 채택.
- **Rationale**:
  - 일반 유저 권한으로 `ufw status`를 직접 구동하면 stdout 대신 stderr에 `ERROR: You must be root to run this script`를 출력하고 exit code 1을 반환함.
  - `setup.sh` 및 `configure_firewall.sh`에서는 sudo 티켓 증발 방지 및 root 권한 확인 후 `sudo ufw status`를 사용하고, Python API(`FirewallManager`)에서는 비대화형 환경 지원을 위해 `sudo -n ufw status 2>/dev/null`을 시도 후 실패 시 `command -v ufw` 존재 유무로 ufw를 우선 감지함.
- **Alternatives Considered**:
  - `/etc/ufw/ufw.conf` 파일 직접 읽기 (`ENABLED=yes` 여부): root 읽기 권한 제한이나 systemd 서비스 상태와 불일치할 수 있어 `sudo ufw status` 호출보다 신뢰성이 낮음.

## 2. Pre-Check Based Rebuild Bypass in setup.sh
- **Decision**: `setup.sh` L232의 `uv pip install ... --force-reinstall --no-cache-dir` 플래그를 완전 제거하고, 소스 컴파일 실행 **직전(Pre-Check)** 단계에서 `.venv` 내 `llama-cpp-python` 가속 지원 함수(`llama_supports_gpu_offload()`)를 실행하여 `True` 반환 시 소스 컴파일 명령어 수수 자체를 100% 스킵.
- **Rationale**:
  - 기존 `setup.sh`는 소스 컴파일(8분 소요)을 완납한 **후**에 검증 코드를 실행하고 있었음.
  - 사전 검증(Pre-Check)을 컴파일 구문 전으로 전진 배치(Shift-Left)함으로써, 시드 팩 수록 휠 설치 상태나 연속 실행 시 3초 이내에 `setup.sh`가 완납되도록 보장함.
- **Alternatives Considered**:
  - `.venv` 디렉토리 내 특정 빌드 플래그 파일(`build.lock`) 생성: 파이썬 가상환경 모듈 실제 실행 상태(`llama_supports_gpu_offload()`) 직접 검증보다 부정확함.

## 3. Wheel Library Inspection & Seed Pack Exclusion Policy
- **Decision**:
  1. `scripts/verify_wheel_binary.py` 내 `.so` 검사 로직을 update하여 zip file entry 내 경로 상관없이 `.so` 파이썬 패키지 라이브러리를 검출하도록 개선.
  2. `scripts/make_seed_pack.sh`에서 `tar -czf` 실행 시 `--exclude="config/model_context_profiles.json"` 플래그를 추가.
- **Rationale**:
  - `wheels/legacy_i7_930/*.whl` 검증 시 내부 zip 스펙상의 서브디렉토리 경로 패턴 차이로 인해 유효한 `.so` 바이너리가 있음에도 "No shared libraries found" 오류가 발생했던 버그를 정밀 해결.
  - 컨텍스트 윈도우 프로필 캐시는 타겟 서버의 하드웨어 VRAM/RAM 성능에 고유한 캐시이므로 개발 머신의 파일이 시드 팩에 포함되는 것을 원천 차단함.
- **Alternatives Considered**:
  - 휠 검증 무조건 통과: 손상되거나 타겟 아키텍처 미지원 휠 검증 역할을 상실하므로 거부.

## 4. Dual Interface (CLI & Web UI) for Context Window Benchmark Management
- **Decision**:
  1. **CLI**: `setup.sh` Step 4.5에서 `config/model_context_profiles.json` 유효 캐시 존재 시 벤치마크 스킵하며, `model_catalog.json` 대비 누락된 모델 발생 시 해당 모델만 차분 측정(Incremental Benchmark) 수행. 전체 강제 재측정은 `uv run python scripts/benchmark_quality.py` 명령으로 제공.
  2. **Web UI**: 웹 대시보드(Port 8089) 백엔드 API (`GET /api/benchmark/profiles`, `POST /api/benchmark/rerun`) 및 모델 관리 화면 UI를 추가하여 클릭 한 번으로 비동기 재측정 및 상태 모니터링 제공.
- **Rationale**:
  - CLI 터미널 환경과 웹 관리자 UI 양쪽에서 동일한 파이썬 스크립트 실행 로직(`scripts/benchmark_quality.py`)을 공유함으로써 코드 중복 없이 Dual 인터페이스 완성.
- **Alternatives Considered**:
  - 웹 대시보드 전용 독립 측정 엔진 구현: 중복 및 벤치마크 결과 불일치 위험으로 거부.

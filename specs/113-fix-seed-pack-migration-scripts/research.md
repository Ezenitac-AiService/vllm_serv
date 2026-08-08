# Research: 시드 팩 마이그레이션 파이프라인 및 ProcessManager 호환성 전수 검증 (Fix Seed Pack Migration Pipeline & ProcessManager Compatibility)

## 1. ProcessManager 클래스 및 인스턴스 메서드 이중 하위 호환성 설계 (Double Safety Net for ProcessManager)

- **Decision**: `src/core/process_manager.py` 클래스 내부의 `calculate_base_vram_mb` 및 `force_kill_zombie_llama_servers` 메서드를 `@staticmethod`로 장식하여 클래스(`ProcessManager.method()`) 및 인스턴스(`pm.method()`) 양쪽 호출 방식을 완벽히 지원하며, `scripts/benchmark_context_window.py` 및 `scripts/benchmark_quality.py` 호출부에도 `getattr()` 및 `try-except` 폴백 방어 구문을 적용하여 이중 하위 호환 구조를 수립합니다.
- **Rationale**:
  - `ProcessManager`는 시스템 전반(`llama_manager.py`, `benchmark_quality.py`, `benchmark_context_window.py`, `auxiliary_manager.py`)에서 공통 프로세스 라이프사이클을 관장합니다.
  - 마이그레이션된 타겟 서버 환경에서 레거시 스크립트 또는 부분 동기화된 모듈이 혼용될 때 발생할 수 있는 `AttributeError: type object 'ProcessManager' has no attribute ...` 또는 `AttributeError: 'ProcessManager' object has no attribute ...` 예외를 근본 차단합니다.
- **Alternatives Considered**:
  - `ProcessManager` 클래스 내부 장식자만 보강하고 호출부는 수정하지 않는 방안: 호출부 스크립트가 파생되거나 이전 버전 스크립트와 조합될 경우 방어력이 떨어지므로 이중 방어 안(Double Safety Net)을 선택하여 기각.

---

## 2. 시드 팩 파이프라인 무결성 검증 항목 동기화 (`make_seed_pack.sh` & `unpack_seed.sh`)

- **Decision**: `scripts/make_seed_pack.sh`의 수록 검증 함수(`verify_archive_entry`)와 `scripts/unpack_seed.sh`의 필수 복원 목록(`REQUIRED_ENTRIES`)에 마이그레이션 핵심 제어 및 벤치마크 스크립트를 명시적으로 수록/검증하도록 확장합니다.
  - 추가 검증 항목: `process_manager.py`, `model_downloader.py`, `benchmark_quality.py`, `benchmark_context_window.py`, `setup.sh`, `unpack_seed.sh`, `make_seed_pack.sh`
- **Rationale**:
  - 이전 시드 팩 검증은 `platform_profiles.json`, `gpu_detector.py`, `model_catalog.json` 등 일부분에 국한되어 주요 벤치마크 및 인퍼런스 엔진 스크립트의 누락을 감지하지 못했습니다.
  - 아카이브 생성 시점 및 언팩 직후/직전에 100% 전수 필수 스크립트 수록 여부를 자동 단정하여 타 플랫폼 이관 실패를 원천 차단합니다.
- **Alternatives Considered**:
  - 단순히 디렉토리 디바이스 존재 여부(`-d scripts/`)만 확인하는 방안: `scripts/` 디렉터리는 존재하지만 특정 `benchmark_context_window.py` 등이 누락되었을 때 감지할 수 없어 기각.

---

## 3. `setup.sh` Step 1 필수 검증 및 루트 심볼릭 링크 원자적 갱신

- **Decision**: `scripts/setup.sh` Step 1의 `REQUIRED_FILES` 목록에 `src/core/model_downloader.py`, `scripts/benchmark_context_window.py`, `scripts/unpack_seed.sh`를 추가하고, Step 4에서 `start_server.sh`, `stop_server.sh`, `status_server.sh` 심볼릭 링크를 생성할 때 기존 낡거나 깨진 링크를 강제 덮어쓰기(`ln -sf`)하여 안정성을 보장합니다.
- **Rationale**:
  - 타 시스템으로 시드 팩을 해제하고 `./setup.sh`를 구동할 때 환경 수립 전 필수 파일 누락 여부를 조기에 감지(Fail-Fast)하여 불필요한 빌드 시간 낭비를 막습니다.
  - 루트 경로 심볼릭 링크가 타겟 서버에서 잘못 인지되는 현상을 방지합니다.
- **Alternatives Considered**:
  - 심볼릭 링크 생성을 스킵하고 사용자가 직접 `scripts/start_server.sh`를 호출하도록 가이드만 제시하는 방안: 기존 가이드 `./start_server.sh` 직관성을 해치므로 기각.

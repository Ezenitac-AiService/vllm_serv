# Research & Technical Decisions: 학습 플랫폼 이관 코드 정밀 검토, 종합 테스트 및 구조적 리팩토링 (`090-audit-test-refactor`)

## Phase 0: Research & Decision Log

### Decision 1: 이관 및 혼재 자산의 전수 조사(Audit) 분류 및 `.legacy/` 아카이빙 처리 방침

- **Decision**: 학습 플랫폼에서 이관되어 기존 개발 플랫폼 파일들과 혼재된 자산들 중, 중복되거나 대치된 레거시 스크립트/모듈을 `.legacy/archive_088_sync/` 디렉토리로 이동하여 격리 관리한다.
- **Rationale**:
  - 프로젝트 헌장(Constitution V: 비파괴적 수정 원칙)에 따라 파일과 역사를 하드 삭제(rm)하지 않고 보존한다.
  - `scripts/`, `src/`, `samples/`, `wheels/` 디렉토리의 자산 유통 구조를 명확히 정돈하여 런타임 수신/빌드 오류를 예방한다.
- **Alternatives Considered**:
  - *Option B (즉시 영구 삭제)*: Git 커밋 이력에는 남으나 파일 손실 시 복구가 번잡하고 헌장 위반 우려가 있음.
  - *Option C (현 위치 `.bak` 확장자 지정)*: 동일 디렉토리 내 임시 파일 누적으로 소스 경로 오염 문제 발생.

---

### Decision 2: CUDA GPU 전용 실행 단정 및 `pytest` 테스트 수트 구축 방침

- **Decision**: `uv run pytest`로 실행되는 테스트 수트는 NVIDIA CUDA GPU 가용성(`torch.cuda.is_available()` 또는 `nvcc` / `nvidia-smi` 정상 응답)을 필수 단정하며, 미장착 시 즉시 Fail-Fast 오류를 발생시킨다.
- **Rationale**:
  - 프로젝트 헌장(Constitution II: 실체적 테스트 결합 원칙 & VII: 의무적 회귀 테스트) 준수.
  - 명세 명확화(Clarification Q2) 단계에서 사용자가 단정한 "CUDA GPU가 없는 플랫폼 전면 배제" 요구사항 100% 이행.
- **Alternatives Considered**:
  - *Option A (CPU Fallback 동적 스킵)*: 사용자가 CPU-only 플랫폼 배제를 명시적 요청했으므로 부적합.
  - *Option C (Fake Mock 테스트)*: 헌장 II (Fake Green 전면 금지) 규정에 따라 엄격히 배제.

---

### Decision 3: 유틸리티 함수 이중 모듈화 구조 설계 (`src/utils/cuda_env.py` & `scripts/common.sh`)

- **Decision**: 파이썬 모듈과 쉘 스크립트에 분산된 CUDA/드라이버/cuDNN 버전을 정밀 파싱하고 llama.cpp 휠 호환성을 검증하는 로직을 이중 공통 모듈화하여 단일화한다.
  - 파이썬 공통 모듈: `src/utils/cuda_env.py`
  - 쉘 공통 믹스인: `scripts/common.sh`
- **Rationale**:
  - 파이썬 영역(`src/`, `tests/`)과 쉘 영역(`scripts/setup.sh` 등)의 실행 런타임 언어가 달라 개별 공통 진입점이 필요함.
  - 각 언어 환경 내에서 중복 구현을 제거하고 공통 검증 로직을 단일 출처(Single Source of Truth)로 관리함.
- **Alternatives Considered**:
  - *Option B (단일 파이썬 전용 패키지화)*: 쉘 스크립트에서 파이썬 래퍼를 계속 호출할 경우 쉘 구동 오버헤드 증가.
  - *Option C (기존 파일 위치 유지 및 개별 중복)*: 유지보수성이 낮고 차후 드라이버 기준 변경 시 누락 발생 위험.

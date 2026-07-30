# Feature Specification: 대시보드 및 플레이그라운드 동적 서비스 모델 드롭다운 노출 버그 및 VRAM 호환성 필터링 (051-fix-model-select-display)

**Feature Branch**: `051-fix-model-select-display`  
**Created**: 2026-07-30  
**Status**: Draft  
**Input**: User directive: "특정 모델 개수(6종 등)를 하드코딩하지 말 것. 카탈로그 모델은 고정이 아니며 GPU VRAM 및 하드웨어 구동 가능성에 따라 동적으로 결정됨."

---

## Clarifications

### Session 2026-07-30

- Q: 모델 목록 표출 시 특정 개수 하드코딩 여부 및 VRAM 호환성 처리 → A: 모델 수 하드코딩 금지. `ConfigManager` 캐시 고착 버그를 해결하고 `model_catalog.json` 카탈로그와 VRAM/하드웨어 호환성에 기반하여 실행 가능한 동적 모델 목록을 프론트엔드 드롭다운에 노출함.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 동적 모델 카탈로그 로드 및 드롭다운 연동 근본 수리 (Priority: P1) 🎯 MVP

대시보드 메인 접속 및 탭 전환 시 `ConfigManager`의 캐시 고착 결함을 수리하여, `config/model_catalog.json`에 등록된 동적 모델 카탈로그 및 현재 시스템 하드웨어에서 실행 가능한 모델 목록이 대시보드 수동 설정 탭(`#model-select`)과 AI Playground 탭(`#pg-model-select`) 드롭다운에 올바르게 노출되고 바인딩됩니다.

- **ConfigManager 캐시 고착 결함 수리**: `src/core/config_manager.py`에서 로드 실패 시 `_model_catalog_cache`가 빈 딕셔너리(`{}`)로 메모리에 고착되는 결함을 수정하여 정합한 동적 카탈로그 데이터를 실시간으로 로드합니다.
- **동적 모델 목록 전달**: 모델 수(개수)를 하드코딩하지 않고, 카탈로그 데이터 기반으로 현재 하드웨어에서 지원되는 모든 유효 모델 키를 `GET /dashboard/api/capabilities`의 `available_models`로 프론트엔드에 전달합니다.
- **프론트엔드 드롭다운 완벽 바인딩**: `src/api/static/app.js`에서 수신된 `available_models` 배열 크기에 맞추어 `#model-select` 및 `#pg-model-select`에 `<option>` 요소들을 동적으로 생성하고, 현재 서비스 중인 활성 모델(`current_model`)을 기본 선택(`selected = true`) 상태로 정밀 바인딩합니다.

**Why this priority**: 하드코딩된 개수를 없애고 동적 카탈로그 지원 모델이 정확하게 선택 가능하도록 모델 선택 기능을 정상화합니다.

**Independent Test**:
1. 대시보드 접속 후 수동 설정 탭(`#model-select`) 및 플레이그라운드 탭(`#pg-model-select`) 드롭다운을 열어 카탈로그 기반의 실행 가능한 지원 모델 목록이 동적으로 정상 표시되는지 확인.
2. `ConfigManager` 인스턴스 반복 생성 시에도 `available_models`에 동적 카탈로그 모델들이 정상 반환되는지 백엔드 테스트 수트로 검증.

---

## Functional Requirements *(mandatory)*

- **FR-001**: `src/core/config_manager.py`의 `get_model_catalog()` 함수에서 `_model_catalog_cache` 캐시가 빈 딕셔너리(`{}`) 상태로 고착되지 않도록 예외 처리 및 로더 로직을 수리하여 `config/model_catalog.json`의 카탈로그 데이터를 동적으로 항상 정확히 로드해야 한다.
- **FR-002**: `src/api/routes/dashboard_api.py`의 `get_capabilities` 함수는 `ConfigManager`에서 조회한 동적 카탈로그 모델 키 목록을 `available_models` 필드로 프론트엔드에 정확히 반환해야 한다. (특정 개수 하드코딩 금지)
- **FR-003**: `src/api/static/app.js`의 `loadCapabilities()` 함수는 전달받은 `available_models`의 동적 크기에 맞추어 대시보드 수동 설정(`#model-select`), AI Playground 드롭다운(`#pg-model-select`), 프리셋 그리드 뷰에 모델 옵션을 빠짐없이 바인딩하고 `current_model`을 기본 선택 처리해야 한다.
- **FR-004**: 헌법 v1.5.2 규정에 따라 백엔드 `ConfigManager` 로더 수리 및 동적 카탈로그 모델 바인딩 연동을 검증하는 단위 테스트 수트(`tests/unit/test_model_select_display_fix.py`)를 작성해야 한다.

---

## Success Criteria *(mandatory)*

- **SC-001**: `ConfigManager.get_model_catalog()`의 동적 카탈로그 반환 성공률 **100%**.
- **SC-002**: 대시보드 및 플레이그라운드 드롭다운의 동적 서비스 모델 목록 노출 및 바인딩 성공률 **100%**.

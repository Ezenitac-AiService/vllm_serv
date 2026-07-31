# Feature Specification: 멀티 플랫폼 하드웨어 사양(16GB RAM) 및 서브넷 네트워크 토폴로지(10.0.0.x vs 192.168.0.x) 보정 명세 (028-update-platform-network-profiles)

**Feature Branch**: `028-update-platform-network-profiles`

**Created**: 2026-07-30

**Status**: Draft

**Input**: User description: "플렛폼 정보가 틀렸어 훈련생 팀 프로젝트 훈련용은 램이 16gb임 훈련생용 서버와, llm 서비스 서버는 같은 192.168.0.x에 있음 개발 플렛폼은 10.0.0.x 임 별도의 네트워크에 있음"

## Clarifications

### Session 2026-07-30

- Q: 하드웨어 프로필 및 네트워크 토폴로지 보정 세부 사항 → A:
  1) 훈련생 팀 프로젝트 서버(Platform B: i7-4770 / RTX 3060) 시스템 RAM 사양을 32GB에서 **16GB**로 정정.
  2) 훈련생 팀 프로젝트 서버(Platform B)와 LLM 서비스 제공 서버(Platform C: i7-930 / GTX 1070)는 동일 사설 서브넷 대역(`192.168.0.0/16`)에 위치하도록 구성.
  3) 개발 개발 플랫폼(Platform A: Xeon E3-1231v3 / GTX 1080 Ti)은 별도의 서브넷 대역(`10.0.0.0/8`)에 위치하도록 바인딩 허용 대역 보정.
- Q: server_config.json 내 VRAM 하드코딩(11264MB) 제거 및 플랫폼별/NVML 동적 인지 처리 여부 → A: server_config.json 내 static 11264MB 하드코딩을 제거하고 감지된 GPU 프로필(NVML / platform_profiles.json)의 VRAM 용량(RTX 3060: 12GB, GTX 1080Ti: 11GB, GTX 1070: 8GB)을 동적으로 반영함.
- Q: 대시보드 API 키 발급용 관리자 정보(admin_secret) 명시화 여부 → A: config/server_config.json에 admin_secret ("aiservice"), api_key_enabled, api_keys 설정 항목을 명시적으로 노출하여 사용자가 손쉽게 비밀번호를 확인하고 변경할 수 있도록 함.
- Q: 대시보드 웹 UI 접속 주소 안내 및 로그 로깅 명시화 → A: 대시보드 접속 URL (`http://127.0.0.1:8081/dashboard/` 또는 LAN IP `http://<active_ip>:8081/dashboard/`) 및 로그인 암호(`"aiservice"`) 안내를 서버 상태 출력 및 테스트 가이드에 명시함.
- Q: 모델별 컨텍스트 윈도우 크기(n_ctx) 설정 위치 및 모델 스위치 시 상한 제어 위치 → A: `config/model_catalog.json` 내 각 모델 항목별 `default_n_ctx` (기본 4096)를 정의하고, 컨텍스트 스케일링 전용 벤치마크 스크립트(`src/scripts/benchmark_context_scaling.py`)의 실측 VRAM 측정 결과 및 KV Cache VRAM 동적 계산기 (`estimate_kv_cache_vram()`)를 활용하여 소형 모델(2B/4B)은 8K~16K 이상 확장을 허용하되 대형 모델(9B/12B)은 4K=4096 상한을 동적으로 제어함.
- Q: 컨텍스트 윈도우 스케일링 벤치마크 실행 시점 및 파이프라인 연동 방식 → A: 1) 원스톱 서버 구축 파이프라인 스크립트(`scripts/setup.sh`) 실행 마지막 단계에서 컨텍스트 벤치마크(`src/scripts/benchmark_context_scaling.py`)를 1회 백그라운드 측정하여 결과를 `config/model_context_profiles.json`에 캐싱. 2) 서버 런타임 시작 시 캐시 파일 존재 시 즉시 로드(0ms), 미존재 시 `estimate_kv_cache_vram()`으로 안전 계산. 3) 관리자 온디맨드 API (`POST /v1/admin/benchmark/run`)를 통해 언제든 수동 재측정 지원.
- Q: 다중 페르소나 비판 분석 반영 (보안, API 에러 핸들링, 파이프라인 예외 처리) → A:
  1) `admin_secret` 보안: `config/server_config.json` 표기 외에 환경변수 `VLLM_ADMIN_SECRET` 오버라이드 지원 (12-Factor App 원칙 준수).
  2) `max_n_ctx` 초과 처리: 클라이언트가 허용 상한을 초과하는 컨텍스트 요청 시 OpenAI 규격 `400 Bad Request` 에러 응답 및 최대 허용 용량 안내.
  3) `setup.sh` 파이프라인 안가성: 벤치마크 실행 실패 시 파이프라인 중단 없이 Non-blocking 예외 트랩 후 `estimate_kv_cache_vram()` 자동 fallback 전환.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 플랫폼 하드웨어 프로필(RAM 16GB) 및 서브넷 네트워크 토폴로지 정밀 반영 (Priority: P1) 🎯 MVP

시스템 운영자 및 엔지니어가 `config/platform_profiles.json` 및 `src/core/config_manager.py`를 통해 하드웨어 정보와 허용 서브넷 대역을 조회할 때, 실제 머신 환경(Platform B RAM 16GB, Platform A `10.0.0.x` 분리 망, Platform B/C `192.168.0.x` 동일 망)과 100% 일치하도록 보정합니다.

**Why this priority**: 잘못된 RAM 용량 인식 및 네트워크 서브넷 대역 설정으로 인한 서비스 차단 및 모니터링 왜곡을 방지하기 위함입니다.

**Independent Test**: `uv run pytest tests/unit/test_config_manager_profiles.py tests/unit/test_network_detector.py` 실행 시 16GB RAM 및 서브넷 허용 정책 정상 통과 검증.

**Acceptance Scenarios**:

1. **Given** 훈련생 팀 프로젝트 서버(Platform B: `dev-rtx3060`) 프로필이 조회될 때, **When** 시스템 사양을 확인하면, **Then** RAM 용량이 16GB로 정확히 표시되어야 한다.
2. **Given** 개발 플랫폼(Platform A: `pascal-avx2-gtx1080ti`) 프로필이 조회될 때, **When** 네트워크 서브넷 정책을 확인하면, **Then** `10.0.0.0/8` 망 접근이 허용되어야 한다.
3. **Given** LLM 서비스 제공 서버(Platform C: `legacy-i7-930-gtx1070`) 및 훈련생 서버(Platform B)가 구동될 때, **When** 동일 `192.168.0.x` 네트워크 대역 상에서 상호 통신을 수행하면, **Then** IP 허용 필터링을 무사히 통과해야 한다.

---

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `config/platform_profiles.json` 및 관련 프로필 설정 코드 내 Platform B RAM 사양 16GB 수정 완료
- **DoD-002**: Platform A 개발 망(`10.0.0.0/8`) 및 Platform B/C 훈련망(`192.168.0.0/16`) 서브넷 대역 명시적 반영
- **DoD-003**: `server_config.json` VRAM 하드코딩 제거 및 NVML/플랫폼 프로필 기반 동적 바인딩 보정 완료
- **DoD-004**: `server_config.json` 내 `admin_secret` 관리자 인증 정보 명시적 노출 반영 완료 (`"aiservice"`) 및 `VLLM_ADMIN_SECRET` 환경변수 오버라이드 지원
- **DoD-005**: `src/scripts/benchmark_context_scaling.py` 실측 VRAM 연동 기반 소형 모델(2B/4B) 컨텍스트 확장(8K~16K) 허용, 대형 모델 상한 제어, 초과 시 `400 Bad Request` 에러 처리 및 `setup.sh` Non-blocking fallback 검증
- **DoD-006**: 100% Pytest 테스트 수트 통과 보장

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (Platform B 시스템 RAM 16GB 정정)**: `dev-rtx3060` 프로필의 `ram_gb` 수치를 32GB에서 16GB로 보정하고 관련된 검증 로직을 업데이트해야 한다.
- **FR-002 (Platform A 개발망 서브넷 대역 10.0.0.x 분리 반영)**: `pascal-avx2-gtx1080ti` 프로필의 허용 서브넷 목록에 `10.0.0.0/8`을 반영해야 한다.
- **FR-003 (Platform B/C 훈련생 동계망 192.168.0.x 통합 반영)**: `dev-rtx3060` 및 `legacy-i7-930-gtx1070` 프로필의 허용 서브넷 목록에 `192.168.0.0/16`을 반영해야 한다.
- **FR-004 (server_config.json VRAM 하드코딩 제거 및 동적 VRAM 바인딩)**: `config/server_config.json`의 static 11264MB 고정값을 제거하고 NVML 및 platform_profiles.json 감지 기반 동적 VRAM 용량을 기본 바인딩해야 한다.
- **FR-005 (server_config.json 내 관리자 암호 명시화 및 환경변수 지원)**: `config/server_config.json`에 `admin_secret` (`"aiservice"`), `api_key_enabled` (`false`), `api_keys` (`[]`) 항목을 명시적으로 표기하고, `VLLM_ADMIN_SECRET` 환경변수 오버라이드를 동시 지원해야 한다.
- **FR-006 (benchmark_context_scaling.py VRAM 연동 및 초과 시 400 에러 처리)**: 컨텍스트 스케일링 전용 벤치마크(`src/scripts/benchmark_context_scaling.py`)의 실측 VRAM 데이터 및 `estimate_kv_cache_vram()` 계산 결과를 활용하여 소형 모델(`gemma4-e2b`, `qwen3.5-2b`, `qwen3.5-4b`)은 8K~16K 컨텍스트 확장을 허용하고, 대형 모델(`gemma4-12b`, `qwen3.5-9b`)은 VRAM OOM 방지를 위해 4K=4096 상한을 동적으로 제어하며, 상한 초과 요청 시 `HTTP 400 Bad Request` 에러를 반환해야 한다.
- **FR-007 (setup.sh 초기 구축 파이프라인 Non-blocking 연동 & Fallback)**: 원스톱 구축 파이프라인(`scripts/setup.sh`) 실행 단계에서 컨텍스트 스케일링 벤치마크를 Non-blocking 1회 실행하여 `config/model_context_profiles.json`을 캐싱하고, 벤치마크 실패 시 파이프라인 중단 없이 `estimate_kv_cache_vram()`으로 자동 fallback되도록 연동해야 한다.

### Key Entities

- **PlatformProfile**: 각 장비별 CPU, GPU, RAM 및 네트워크 서브넷 규격 엔티티.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 3개 메인 장비 프로필(Platform A, B, C)의 RAM 사양 및 서브넷 IP 정보 100% 정확도 달성
- **SC-002**: 전체 148+ 개 단위/통합 Pytest 테스트 100% 통과

## Assumptions

- Platform B (Core i7-4770 / RTX 3060)는 물리적 RAM 16GB 장착 머신임.
- Platform A (Xeon E3-1231v3 / GTX 1080 Ti)는 개발망 `10.0.0.x` 대역에 위치함.
- Platform B와 Platform C는 동일한 사설 망 `192.168.0.x` 대역에서 통신함.

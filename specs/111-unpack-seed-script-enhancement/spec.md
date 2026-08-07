# Feature Specification: Seed Pack 복원 스크립트 고도화 (Unpack Seed Script Enhancement)

**Feature Branch**: `111-unpack-seed-script-enhancement`

**Created**: 2026-08-07

**Status**: Draft

**Input**: User description: "/speckit-specify 시드 팩 만드는 스크립트를 고도화 했으면, unpack_seed.sh 도 고도화 해야지"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 멀티 포맷(.tar.gz & .zip) 동적 자동 감지 및 비파괴형(-k/-n) 복원 (Priority: P1) 🎯 MVP

타겟 서버의 운영자가 `make_seed_pack.sh`로 생성된 `.tar.gz` 또는 `.zip` 포맷의 시드 팩 아카이브를 `unpack_seed.sh`로 복원할 때, 아카이브 포맷을 확장자 및 헤더 시그니처로 동적 자동 감지하고, 기존 서버의 검증 통과 바이너리를 덮어쓰지 않고 안전하게 비파괴 복원(non-destructive extraction)할 수 있어야 합니다.

**Why this priority**: `make_seed_pack.sh`에서 `.zip` 및 `.tar.gz` 포맷을 모두 지원하도록 고도화되었으므로, `unpack_seed.sh`가 동일한 포맷 호환성과 비파괴 복원성을 갖추는 것이 마이그레이션 파이프라인 완성의 핵심 MVP 조건입니다.

**Independent Test**: `.tar.gz` 및 `.zip` 아카이브 각각에 대해 `./scripts/unpack_seed.sh [archive_file]` 실행 시 포맷을 정확히 자동 인식하고 기존 유효 휠 바이너리를 보존하며 압축 해제에 성공함을 실측 검증.

**Acceptance Scenarios**:

1. **Given** 타겟 서버 디렉터리에 `vllm_serv_seed.zip` 또는 `vllm_serv_seed.tar.gz` 아카이브가 존재하는 환경에서, **When** `./scripts/unpack_seed.sh`를 실행하면, **Then** 파일 확장자 및 헤더를 분석하여 `unzip -n` 또는 `tar -xvkpf`를 동적 선택하여 압축 해제를 완료합니다.
2. **Given** 이미 검증을 통과한 `wheels/legacy_i7_930/*.whl` 사전 빌드 휠 바이너리가 존재하는 상태에서, **When** `unpack_seed.sh`를 구동하면, **Then** 기존 유효 바이너리를 덮어쓰지 않고 최우선 보존(Preserved)함을 안내 로그로 출력합니다.

---

### User Story 2 - CLI 입력 옵션 체계화 및 사전 무결성 검증 (Priority: P2)

개발자 및 시스템 관리자가 복원 대상 파일, 타겟 디렉터리, 덮어쓰기 여부 등을 유연하게 제어하고, 압축 해제 전 필수 구성 요소의 포함 여부를 검증(pre-unpack verification)할 수 있어야 합니다.

**Why this priority**: 다양하게 배치된 아카이브 경로 및 자동화 파이프라인에서 입력 옵션을 명확히 지정하고, 손상된 아카이브로 인한 복원 실패를 사전에 방지할 수 있습니다.

**Independent Test**: `./scripts/unpack_seed.sh -i custom_seed.zip -t /tmp/dest --verify-only` 실행 시 압축 해제 없이 아카이브 무결성 검증 결과 및 파일 목록이 정상 출력됨을 확인.

**Acceptance Scenarios**:

1. **Given** `-i` (`--input`), `-t` (`--target-dir`), `-f` (`--force-overwrite`), `--verify-only` 옵션이 제공되었을 때, **When** 스크립트를 구동하면, **Then** 옵션 파싱 결과에 따라 대상 경로, 목적지, 덮어쓰기 플래그가 정확히 적용되어 실행됩니다.
2. **Given** 손상되었거나 필수 파일(`platform_profiles.json`, `model_catalog.json`, `start_server.sh` 등)이 누락된 아카이브 파일이 지정되었을 때, **When** 무결성 검사를 수행하면, **Then** 명확한 오류 로그와 함께 비정상 종료(exit code 1)합니다.

---

### User Story 3 - 사후 무결성 검증 및 원클릭 `./setup.sh` 연동 안내 (Priority: P3)

압축 해제가 완료된 후 필수 파일이 정상 복원되었는지 사후 검증(post-unpack verification)을 수행하고, 바로 `./setup.sh`를 실행할 수 있도록 안내 및 인터랙티브 구동 옵션을 제공합니다.

**Why this priority**: 복원 후 환경 설정 단계로 매끄럽게 연결하여 사용자의 작업 편의성을 극대화합니다.

**Independent Test**: 복원 완료 후 사후 무결성 검사 통과 메세지와 함께 `./setup.sh` 실행 안내 및 자동 실행 플래그(`--run-setup`)가 정상 동작함을 확인.

**Acceptance Scenarios**:

1. **Given** 복원이 완결된 상황에서, **When** 스크립트 최종 단계에 진입하면, **Then** 주요 파일 복원 여부 체크 및 안내 문구를 출력합니다.
2. **Given** `--run-setup` 플래그가 지정되었을 때, **When** 복원이 정상 완료되면, **Then** 자동으로 `./setup.sh` 스크립트를 후속 실행합니다.

---

### Edge Cases

- **압축 도구 미설치**: 타겟 서버에 `unzip` 또는 `tar/gzip` 명령어가 없을 경우 친절한 설치 안내 메세지 출력 후 종료.
- **아카이브 파일 미존재**: 지정된 아카이브 경로나 `dist/` 내 기본 아카이브가 없을 경우 사용법(Show Help) 안내와 함께 종료.
- **권한 부족 및 경로 미존재**: 타겟 복원 디렉터리의 쓰기 권한이 없거나 생성 실패 시 안전한 에러 처리.

---

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `unpack_seed.sh` 스크립트에 멀티 포맷(.tar.gz & .zip) 동적 자동 감지, CLI 옵션 파싱, 사전/사후 무결성 검증, 비파괴 복원(-k/-n) 기능 구현 완결.
- **DoD-002**: `tests/unit/test_shell_scripts.py` 단위 테스트 수트에 `unpack_seed.sh` 포맷 감지, 비파괴 복원 및 옵션 처리 검증 케이스 추가 및 100% PASS 통과.
- **DoD-003**: `.tar.gz` 및 `.zip` 아카이브 실측 압축 해제 벤치마크 테스트 완료.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 스크립트는 입력 아카이브 파일의 확장자 및 시그니처를 분석하여 `.tar.gz` (tar/gzip) 및 `.zip` (unzip) 포맷을 동적 자동 감지하고 최적의 압축 해제 커맨드를 실행해야 합니다.
- **FR-002**: 스크립트는 표준 CLI 옵션을 지원해야 합니다 (`-i`/`--input`, `-t`/`--target-dir`, `-f`/`--force-overwrite`, `--verify-only`, `--run-setup`, `-h`/`--help`).
- **FR-003**: 기본 복원 모드는 비파괴형(non-destructive)이어야 하며, 기존 환경에 검증 통과 휠 바이너리가 존재할 경우 덮어쓰지 않고 보존(`tar -xvkpf` / `unzip -n`)해야 합니다 (`-f` 플래그 사용 시 덮어쓰기 허용).
- **FR-004**: 압축 해제 전 및 해제 후 아카이브 내 필수 구성 파일(`platform_profiles.json`, `model_catalog.json`, `gpu_detector.py`, `start_server.sh` 등) 존재 여부 무결성 검사를 수행해야 합니다.
- **FR-005**: 복원 완결 시 실행 결과 메트릭(파일 개수, 용량, 소요 시간)을 출력하고, `--run-setup` 옵션 지정 시 `./setup.sh`를 자동 후속 구동해야 합니다.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `.tar.gz` 및 `.zip` 시드 팩 아카이브 모두 10초 이내에 무결성 검증 및 복원이 완료됩니다.
- **SC-002**: 기존 검증 통과 휠 바이너리가 존재하는 타겟 환경에서 압축 해제 시 100% 기존 유효 바이너리가 보존되어 덮어쓰기 손실이 발생하지 않습니다.

---

## Assumptions

- 타겟 서버에는 POSIX 표준 쉘(Bash) 및 기본 아카이브 도구(`tar`, `gzip` 또는 `unzip`)가 설치되어 있습니다.
- 복원되는 파일은 프로젝트 루트 디렉터리 구조와 1:1 대응합니다.

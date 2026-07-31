# Data Model: 코드베이스 리팩토링 및 레거시 아카이브 명세 (026-archive-legacy-files)

## Data Entities

### 1. LegacyArchiveEntry

`.legacy/` 아카이브 디렉토리로 이동 및 보존 처리되는 레거시 파일의 엔티티 구조.

| Field Name | Type | Description | Constraints / Examples |
|---|---|---|---|
| `source_path` | `str` | 원본 파일 상대 경로 | `"ATEAM_ExtractionItem.py"`, `"get-pip.py"` |
| `archive_path` | `str` | `.legacy/` 하위 아카이브 상대 경로 | `".legacy/ATEAM_ExtractionItem.py"` |
| `is_moved` | `bool` | 파일 이동 완료 여부 | `True` |
| `archived_at` | `str` | 아카이빙 일시 (ISO-8601) | `"2026-07-30T06:27:00Z"` |

### 2. RefactoredModuleEntry

리팩토링 및 모듈 정돈 대상 소스코드 파일 엔티티 구조.

| Field Name | Type | Description | Constraints / Examples |
|---|---|---|---|
| `module_path` | `str` | 소스코드 파일 상대 경로 | `"src/core/config_manager.py"` |
| `dead_code_removed` | `bool` | 미사용 코드/임포트 제거 여부 | `True` |
| `verification_status` | `str` | 회귀 테스트 검증 결과 | `"PASS"` |

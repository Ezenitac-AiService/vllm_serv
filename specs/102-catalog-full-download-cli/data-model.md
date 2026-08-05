# Phase 1 Data Model: `scripts/ensure_models.py` 전체/특정 모델 다운로드 CLI 옵션 확장 (102-catalog-full-download-cli)

## Key Entities & Data Schemas

### 1. EnsureModelsCLIConfig (CLI 파싱 및 정규화 엔티티)

| Field Name | Type | Default | Description |
|------------|------|---------|-------------|
| `all_models` | `bool` | `False` | `--all` 또는 `--download-all` 플래그 지정 여부 |
| `target_model_arg` | `Optional[str]` | `None` | `--model` 인자로 전달된 단일/쉼표구분 모델 ID 문자열 |
| `check_only` | `bool` | `False` | `--check-only` 다운로드 스킵 및 상태 점검 전용 플래그 |
| `auto_download` | `bool` | `True` | `--no-auto-download` 옵션 미지정 시 자동 다운로드 수행 여부 |

### 2. ModelResolutionResult (타깃 모델 리졸버 결과 엔티티)

| Field Name | Type | Description |
|------------|------|-------------|
| `target_models` | `List[str]` | 최종 점검/다운로드 대상 모델 ID 리스트 (예: `['qwen3.6-27b']` 또는 14개 전체) |
| `resolution_mode` | `str` | `"ALL"`, `"SPECIFIC"`, `"DEFAULT_REQUIRED"` 중 하나 |
| `is_valid` | `bool` | 모든 요청된 모델 ID의 카탈로그 수록 여부 |
| `invalid_model_ids` | `List[str]` | 카탈로그에 존재하지 않아 거부된 모델 ID 리스트 |

---

## State Transition Diagram

```mermaid
stateDiagram-v2
    [*] --> ParseCLI: CLI 인자 수신 (sys.argv)
    ParseCLI --> ValidateConflict: --all & --model 인자 검사
    
    ValidateConflict --> ExitCode2: 동시에 둘 다 지정됨
    ExitCode2 --> [*]: sys.exit(2) [인자 구문 오류]

    ValidateConflict --> ResolveTargets: 상호 배타성 통과
    
    ResolveTargets --> ModeAll: --all 지정됨
    ModeAll --> QueryCatalogAll: config/model_catalog.json 14개 전수 추출
    
    ResolveTargets --> ModeSpecific: --model 지정됨
    ModeSpecific --> ValidateModelIDs: 쉼표 분할 식별자 카탈로그 검증
    ValidateModelIDs --> ExitCode1: 무효한 ID 포함됨
    ExitCode1 --> [*]: sys.exit(1) [Unknown model_id]
    ValidateModelIDs --> QueryCatalogSpecific: 유효 식별자 추출

    ResolveTargets --> ModeDefault: 인자 미지정
    ModeDefault --> QueryServerConfig: server_config.json 동적 필수 3종 추출

    QueryCatalogAll --> ExecuteProvisioning: target_models 확장
    QueryCatalogSpecific --> ExecuteProvisioning: target_models 확정
    QueryServerConfig --> ExecuteProvisioning: target_models 확정

    ExecuteProvisioning --> SmartSkipCheck: 모델별 is_model_available()
    SmartSkipCheck --> MetadataSync: 로컬 존재 (FR-012 Sync)
    SmartSkipCheck --> DownloadEngine: 부재 및 auto_download=True
    
    DownloadEngine --> MetadataSync: 다운로드 성공
    DownloadEngine --> ReportFailed: 다운로드 실패 (Retry 3회 초과)
    
    MetadataSync --> FinalReport: 종합 상태 리포트
    ReportFailed --> FinalReport: 종합 상태 리포트
    
    FinalReport --> ExitCode0: All models present
    FinalReport --> ExitCode1: Any model missing / check-only fail
    ExitCode0 --> [*]
```

# Data Model & Domain Entities: `scripts/` 디렉토리 스크립트 모듈화 및 결합도 완화 대대적 리팩토링 (`093-refactor-scripts-architecture`)

## Domain Entities

### 1. `ScriptModuleDependency` (스크립트 모듈 결합도 엔티티)

`scripts/` 하위 각 쉘/파이썬 스크립트의 타 디렉토리 결합도 및 모듈화 검증 엔티티.

- **Attributes**:
  - `script_name`: `str` - 스크립트 파일명 (예: `setup.sh`, `make_seed_pack.sh`)
  - `external_refs`: `List[str]` - 하드코딩 참조 경로 목록 (예: `['config/server_config.json', 'src/api/server.py']`)
  - `coupling_level`: `str` - 결합도 수준 (`DIRECT_HARDCODED`, `MIXIN_PARAMETRIZED`, `DECOUPLED`)
  - `has_safety_wrapper`: `bool` - `try_optional_step` 안전 래퍼 적용 여부
  - `refactored_status`: `bool` - 리팩토링 및 검증 완료 여부

---

### 2. `PortCascadeConfig` (포트 우선순위 설정 엔티티)

DevSecOps Cascade 포트 결정 엔티티.

- **Attributes**:
  - `port_key`: `str` - 포트 키 (`main_port`, `dashboard_port`, `aux_embedding_port`, `aux_rerank_port`)
  - `cli_override`: `Optional[int]` - CLI 인자로 전달된 포트
  - `env_override`: `Optional[int]` - 환경변수로 전달된 포트
  - `config_val`: `Optional[int]` - `config/server_config.json` 값
  - `default_val`: `int` - 기본 기본값 (예: 8081, 8082, 8090, 8091)
  - `resolved_port`: `int` - Cascade 4단계 우선순위 결과 확정 포트

# Research & Technical Decisions: `scripts/` 디렉토리 스크립트 모듈화 및 결합도 완화 대대적 리팩토링 (`093-refactor-scripts-architecture`)

## Phase 0: Research & Decision Log

### Decision 1: `scripts/common.sh` 믹스인 확장 및 SRE 안전 래퍼 함수(`try_optional_step`) 구현

- **Decision**: `scripts/common.sh`에 포트/경로 파싱 헬퍼, `try_optional_step` (옵셔널 헬퍼 구동 실패 시 non-fatal 에러 처리 및 경고 로그 래핑) 함수를 공식 추가한다.
- **Rationale**:
  - `ufw`, `firewall-cmd`, `nftables` 미설치 환경이나 `nvidia-smi` 패키지 업데이트 과정에서 발생하는 non-fatal 에러가 `set -e`로 인해 `setup.sh` 파이프라인 전체 폭사로 이어지는 위험을 차단함.
- **Alternatives Considered**:
  - *Option B (구문별 `|| true` 배치)*: 에러의 원인을 감추거나 가독성을 저해함.

---

### Decision 2: DevSecOps Cascade 포트 조회 및 경로 파라미터화

- **Decision**: `LLAMA_PORT` / `DASHBOARD_PORT` 등 포트 정보를 수신할 때 `CLI flag > Environment Variable > config/server_config.json > Default` Cascade 우선순위를 준수하는 믹스인 함수 `get_configured_port()`를 `common.sh` 및 `src/core/config_manager.py`에 적용한다.
- **Rationale**:
  - K8s / Docker / CI 환경변수 주입과 `config/server_config.json` 간의 포트 충돌을 명확한 규칙으로 해결.

---

### Decision 3: 비대 스크립트 모듈 분할 및 파이프라인 순수성 유지

- **Decision**: `setup.sh` 내부 800줄 비대 코드를 `scripts/modules/` 또는 믹스인 분할 함수로 구조화하되, 최상위 CLI 스크립트(`setup.sh`, `start_server.sh`, `stop_server.sh`, `status_server.sh`, `make_seed_pack.sh`)의 인자/호출 인터페이스는 100% 보존한다.
- **Rationale**:
  - 단일 책임 원칙(Single Responsibility Principle) 준수 및 외부 툴과의 하위 호환성 유지.

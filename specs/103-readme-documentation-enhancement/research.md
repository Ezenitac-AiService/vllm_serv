# Research Findings: `README.md` 프로젝트 설명, 셋업 파이프라인, 제어 쉘 명령 및 수동 스크립트 가이드 고도화 명세 (103-readme-documentation-enhancement)

## Technical Decisions & Best Practices

### Decision 1: GFM (GitHub Flavored Markdown) 및 Mermaid 시각화 파이프라인 채택
- **Decision**: GitHub 리포지토리 메인 README.md 문서 표준인 GFM 및 Mermaid JS 다이어그램을 활용하여 `./setup.sh` 구동 9단계 자동 셋업 흐름을 시각화한다.
- **Rationale**: 텍스트 설명만으로는 9단계의 복잡한 연동 구조(관리자 권한, uv sync, CUDA 검증, 컴파일, 방화벽 등록, 스크립트 생성, 4단계 벤치마크, 소유권 환원)를 이해하기 어려우므로 시각적 흐름도가 필수적이다.
- **Alternatives Considered**: HTML 이미지 렌더링, 텍스트 전용 리스트 (시각적 명확성이 떨어짐).

### Decision 2: 쉘 상태 변경 명령 및 CLI 인자 표 표준화
- **Decision**: 셋업 명령(`setup.sh`), 서버 상태 제어 명령(`start_server.sh`, `stop_server.sh`, `status_server.sh`), 백엔드 헬퍼 스크립트 수동 구동 커맨드를 마크다운 코드 블록 및 표준 4컬럼 표(파라미터명, 타입, 기본값, 설명)로 수록한다.
- **Rationale**: 개발자 및 시스템 운영자가 터미널에서 복사/붙여넣기로 즉시 구동할 수 있으며, CLI 옵션의 작동 원리를 직관적으로 이해할 수 있다.
- **Alternatives Considered**: 별도 외부 wiki 문서 링크 (로컬 레포지토리 독립성 훼손).

### Decision 3: SpecKit 슬래시 커맨드 및 백엔드 쉘 스크립트 명세 포함
- **Decision**: `.specify/scripts/bash/create-new-feature.sh` 및 `/speckit-specify` 커맨드의 스마트 슬러그 추출, 3자리 순차 번호/타임스탬프 접두사, `.specify/feature.json` 경로 영구화 메커니즘을 README.md에 수록한다.
- **Rationale**: SpecKit TDD 개발 환경의 투명성을 보장하고 신규 피처 생성 및 수렴 파이프라인 가이드를 제공하기 위함이다.
- **Alternatives Considered**: SpecKit 가이드 생략 (사용자가 스크립트 구동 방식을 알기 어려움).

# Research: sample_05_structured_output.py의 .legacy 모듈 의존성 제거 및 시드팩 독립성 보장 (071-seed-pack-include-legacy)

## Research Topic 1: sample_05_structured_output.py의 레거시 모듈 의존성 전면 제거 및 단독 구현

### Decision
`samples/sample_05_structured_output.py` 내부에서 `.legacy` 디렉터리 경로 추가(`sys.path.insert`) 및 `ATEAM_ExtractionItem`, `BTEAM_ExtractionItem` 모듈 임포트를 완전히 제거하고, 스크립트 내부에서 표준 Pydantic `StockAnalysisResponse` 및 `StockCommentItem` 스키마만으로 동작하도록 리팩토링.

### Rationale
- `.legacy` 디렉터리는 향후 프로젝트에서 완전히 삭제(Deprecation)될 임시 실험 코드 디렉터리입니다.
- `sample_05_structured_output.py`가 `.legacy` 폴더에 의존하는 구조를 유지하면, 시드 팩 배포 환경이나 `.legacy` 폴더 삭제 시 `ModuleNotFoundError` 예외가 발생합니다.
- `sample_05_structured_output.py` 스크립트 하나만 독립 추출(Self-contained)하여도 LLM Structured Output API의 Pydantic 파싱 실습이 100% 가능하도록 구현하는 것이 사용자 및 배포 관점에서 가장 안전합니다.

### Alternatives Considered
- `.legacy` 디렉터리를 시드 팩 아카이브에 포함시키기: 불필요한 레거시 코드가 패키지에 유입되어 용량이 늘어나고, 향후 `.legacy` 폴더 삭제 시 샘플 코드가 깨지므로 제외.
- 별도의 서드파티 스키마 라이브러리 사용: `samples/` 스크립트 경량화 원칙(표준 라이브러리 + `httpx`, `pydantic`만 사용)에 위배되므로 제외.

---

## Research Topic 2: scripts/make_seed_pack.sh의 .legacy 수록 제외 확인 및 테스트 검증

### Decision
`make_seed_pack.sh`에서 `.legacy` 디렉터리가 시드 팩 아카이브 번들링 대상에 포함되지 않도록 유지하고, `samples/sample_05_structured_output.py`가 시드 팩 이관 환경에서도 `.legacy` 없이 독립 작동함을 검증 수트에 수록.

### Rationale
- 시드 팩은 타 시스템 이관용 최소 소스코드 아카이브로서 `.legacy`와 같은 삭제 예정 코드를 포함해서는 안 됩니다.

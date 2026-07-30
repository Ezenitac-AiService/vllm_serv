# Research: 시드 팩 배제 항목 명시화 및 아카이브 경량화 (033-exclude-benchmark-cache-seed-pack)

## Research Topic 1: 시드 팩 호스트 독립성을 위한 배제 패턴 명시화

### Decision
`scripts/make_seed_pack.sh` 파일의 tar 및 zip 명령어 배제 옵션(`-x` / `--exclude`)에 아래 항목들을 추가 명시한다:

1. `config/model_context_profiles.json` (호스트 특정 GPU 컨텍스트 윈도우 스케일링 측정 프로필)
2. `.legacy` 및 `.legacy/*` (구형 히스토리 아카이브 디렉터리 및 아티팩트)
3. `benchmark_results.json` 및 `*.jsonl` (런타임 벤치마크 수행 결과 로그 파일)

### Rationale
- **타겟 장비 벤치마크 신규 수행 보장**: `config/model_context_profiles.json` 파일이 시드 팩에 포함되면 타겟 시스템의 `./setup.sh`가 이전 머신(개발 머신)의 캐시를 이미 존재하는 것으로 오판하여 벤치마크를 건너뜁니다.
- **아카이브 청정화 및 경량화**: 불필요한 `.legacy/` 파일 및 벤치마크 로그(`*.jsonl`)를 제거하여 타겟 배포 시드 팩의 가독성과 독립성을 향상시킵니다.
- **필수 공용 설정 유지**: `config/model_catalog.json`, `config/server_config.json`, `config/platform_profiles.json`은 공용 규격 설정이므로 시드 팩에 정상 포함시킵니다.

### Alternatives Considered
- **`setup.sh`에서 무조건 기존 벤치마크 캐시 삭제**: 기존 서버에서 `setup.sh` 재실행 시 매번 벤치마크가 강제 실행되는 side effect 발생 (기각).
- **시드 팩 생성 시 `config/` 디렉터리 전체 제외**: 필수 공용 설정 파일까지 배제되어 설치 파이프라인이 실패함 (기각).

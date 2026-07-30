# Data Model: 시드 팩 아카이브 수록 및 배제 필터엔티티 (033-exclude-benchmark-cache-seed-pack)

## Entities

### 1. SeedPackExclusionRule (엔티티)

`make_seed_pack.sh`에서 아카이브 생성 시 적용되는 호스트 특정 및 레거시 배제 규칙.

| Category | Filter Pattern | Reason for Exclusion |
|----------|----------------|----------------------|
| Large Artifacts | `models/`, `.venv/`, `.bin/` | 대용량 가중치 및 가상환경 배제 |
| Machine Benchmark Cache | `config/model_context_profiles.json` | 타겟 장비 신규 벤치마크 수행 보장 |
| Legacy Archives | `.legacy/` | 구형 코드 및 히스토리 아카이브 제외 |
| Benchmark Logs | `benchmark_results.json`, `*.jsonl` | 런타임 수집 로그 파일 배제 |
| Build & Dist | `build/`, `dist/`, `logs/`, `vllm_serv.pid` | 빌드/실행 상태 아티팩트 배제 |
| Git & Test Cache | `.git/`, `.github/`, `.pytest_cache/`, `.coverage` | 버전에 의존하지 않는 배포 아카이브 구성 |

---

## Seed Pack Inclusion vs Exclusion Schema

```text
dist/vllm_serv_seed.tar.gz
├── config/
│   ├── model_catalog.json        [INCLUDED]
│   ├── platform_profiles.json    [INCLUDED]
│   └── server_config.json        [INCLUDED]
│   └── model_context_profiles.json [EXCLUDED - Host-specific Cache]
├── wheels/legacy_i7_930/         [INCLUDED - Prebuilt Wheels]
├── src/                          [INCLUDED - Application Source]
├── scripts/                      [INCLUDED - Control Scripts]
├── tests/                        [INCLUDED - Test Suite]
├── specs/                        [INCLUDED - Feature Specs]
├── .legacy/                      [EXCLUDED - Legacy Archive]
├── models/                       [EXCLUDED - Large Weights]
└── .venv/                        [EXCLUDED - Virtual Environment]
```

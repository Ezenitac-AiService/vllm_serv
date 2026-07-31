# Data Model: 시드팩(Seed Pack) 패키징 시 명세서(specs/) 및 샘플 파일(samples/) 수록 포함 개선

**Feature**: `065-seed-pack-specs-samples`

## Entities & Data Schemas

### 1. Seed Pack Archive Structure Entity (`SeedPackArchive`)
시드팩 압축 패키지 내 수록 파일 구성 명세 (`dist/vllm_serv_seed.tar.gz`).

- **`scripts/`**: `setup.sh`, `start_server.sh`, `stop_server.sh`, `status_server.sh`, `make_seed_pack.sh`, `configure_firewall.sh`
- **`src/`**: 메인 인퍼런스 서버 및 코어 관리자 소스코드 전체
- **`config/`**: `platform_profiles.json` 멀티 플랫폼 설정 파일
- **`wheels/legacy_i7_930/`**: 사전 빌드 휠 아티팩트
- **`samples/`** *(New Included)*: `common.py`, `sample_01_chat.py` ~ `sample_05_structured_output.py`
- **`specs/`** *(New Included)*: 기능 명세서 001~065 전체 디렉터리 및 아티팩트
- **`.legacy/`** *(New Included)*: ATEAM/BTEAM 추출 모듈 및 Pydantic 데이터 모델
- **`pyproject.toml` / `pytest.ini` / `README.md`**: 프로젝트 루트 필수 설정 파일

# Quickstart Validation Guide: `scripts/` 디렉토리 스크립트 모듈화 및 결합도 완화 대대적 리팩토링 (`093-refactor-scripts-architecture`)

본 가이드는 `scripts/` 하위 스크립트들의 모듈화, 결합도 완화, 하드코딩 제거 및 호환성 검증 시나리오입니다.

---

## 사전 조건 (Prerequisites)

1. **프로젝트 환경 준비**: `uv sync`를 통한 가상환경 구축 완료

---

## 1 단계: 아키텍처 및 결합도 정적 스캔 수트 실행

```bash
uv run pytest tests/test_script_architecture.py -v
```

- **예상 결과**: `scripts/` 내 14개 스크립트의 하드코딩 외부 디렉토리 경로 정적 스캔 검사가 100% 통과(PASSED)함.

---

## 2 단계: `./setup.sh` 호환성 및 모듈화 가동 검증

```bash
# setup.sh 실행
./setup.sh
```

- **예상 결과**:
  1. `common.sh` 믹스인을 통한 포트/경로 조회 완료.
  2. SRE 안전 래퍼(`try_optional_step`) 구동으로 옵셔널 단계 non-fatal 감싸기 정상 처리.
  3. 결합도 완화 및 모듈화된 서브 스크립트가 100% 호환되면서 통과됨.

---

## 3 단계: 서버 가동/종료/상태 제어 스크립트 호환성 검증

```bash
# status_server.sh 구동
./status_server.sh
```

- **예상 결과**: 기존 명령어 인터페이스 및 서빙 리포트 정상 출력.

---

## 4 단계: 마이그레이션 시드팩 빌드 검증

```bash
bash scripts/make_seed_pack.sh --skip-legacy-build
```

- **예상 결과**: `dist/vllm_serv_seed.tar.gz` 아카이브가 에러 없이 생성됨.

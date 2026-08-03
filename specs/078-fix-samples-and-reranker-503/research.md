# Technical Research & Design Decisions: `078-fix-samples-and-reranker-503`

**Feature Directory**: [`specs/078-fix-samples-and-reranker-503`](file:///home/dev/storage/vllm_serv/specs/078-fix-samples-and-reranker-503)  
**Spec**: [`spec.md`](spec.md)  

---

## 1. Technical Decisions

### Decision 1: `samples/common.py` 외부 설정 기반 파싱 체계 및 하드코딩 완전 금지

- **Decision**: `samples/common.py` 모듈에서 소스코드 내 하드코딩된 특정 IP 주소를 전면 배제하고, (1) `SERVER_HOST` / `OPENAI_BASE_URL` 환경변수, (2) `samples/.env`, (3) `samples/config.json` 순서로 파싱합니다. 모든 설정 미존재 시 `http://127.0.0.1`로 기본 안전 폴백합니다.
- **Rationale**: 개발 플랫폼(`10.0.0.x`), 서비스 플랫폼(`192.168.0.x`) 등 다양한 클라이언트 네트워크 환경에서 소스코드 변경 없이 `samples/config.json` 수정만으로 모든 샘플 예제 코드가 구동 가능하도록 보장합니다.
- **Alternatives Considered**: 
  - 특정 IP 목록을 소스코드 내 배열로 가지고 있다가 무작위 탐색하는 방식 (특정 서브넷 변경 시 무효화되며 하드코딩 금지 지침 위반으로 기각)

### Decision 2: 프록시 라우터 내 `/v1/rerank` 및 `/v1/embeddings` 온디맨드 데몬 Readiness 보장

- **Decision**: `src/api/routes/inference_api.py`의 `reverse_proxy` 라우터 함수에서 `/v1/rerank` (포트 8091) 및 `/v1/embeddings` (포트 8090) 요청 수신 시, `auxiliary_manager.ensure_rerank_resident()` 및 `ensure_embedding_resident()`를 비동기 호출하여 8091/8090 인스턴스를 온디맨드로 자동 가동·확인한 후 백엔드로 요청을 포워딩합니다.
- **Rationale**: 메인 서버 구동 후 reranker 또는 embedding 데몬이 정지되었거나 지연 로딩 중일 때 발생하는 `503 Service Unavailable` 예외를 100% 방지하고 정상 200 OK 응답으로 수렴시킵니다.
- **Alternatives Considered**: 503 에러 리턴 후 클라이언트 재시도 유도 (비전공자 및 샘플 스크립트 실행 시 사용자 경험 저하로 기각)

### Decision 3: `samples/config.json.example` 안내 표준화

- **Decision**: `samples/config.json.example`에 개발 플랫폼(`10.0.0.x`) 및 서비스 플랫폼(`192.168.0.x`) 설정을 위한 가이드 주석 및 스키마 구조를 포함합니다.
- **Rationale**: 교육생이 자기 클라이언트 PC 환경에 적합한 IP 주소로 `samples/config.json`을 손쉽게 복사 및 수정할 수 있도록 지원합니다.

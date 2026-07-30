# Research & Architecture Decisions (043-api-key-auth-toggle)

## 1. SQLite WAL Mode for Async FastAPI Serving
- **Decision**: `aiosqlite` 또는 표준 `sqlite3` Connection Pool을 사용하여 `PRAGMA journal_mode=WAL;` 및 `PRAGMA synchronous=NORMAL;` 설정.
- **Rationale**: 초당 수십 건 이상의 인퍼런스 토큰 스트리밍 요청 시 데이터베이스 쓰기 동시성(Concurrency) 락 지연을 0ms 수준으로 최소화.
- **Alternatives Considered**: JSON 파일 인메모리 매핑 (서버 급작 비정상 종료 시 메트릭 유실 위험).

## 2. API Key Security Masking Standard
- **Decision**: `sk-vllm-` 접두사 및 마스킹 `sk-vllm-****-8f3a` 방식 적용.
- **Rationale**: OWASP Top 10 for LLM Applications 2026 규격 준수 및 대시보드 화면 캡처 시 민감 API 키 평문 노출 방지.

## 3. FinOps Cost Estimation Formula
- **Decision**: `estimated_cost_usd = (prompt_tokens * 0.0000005) + (completion_tokens * 0.0000015)`
- **Rationale**: 로컬 서빙 전력/GPU 서버 기회비용 상정 추정치 기준.

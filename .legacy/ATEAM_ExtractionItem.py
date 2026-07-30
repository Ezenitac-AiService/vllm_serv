import json
import os
import re
from typing import TypedDict, Literal
from dotenv import load_dotenv
from openai import OpenAI
from rank_bm25 import BM25Okapi
from kiwipiepy import Kiwi

# Kiwi 형태소 분석기 싱글톤 초기화
kiwi = Kiwi()

def kiwi_tokenize(text: str) -> list[str]:
    """
    Kiwi 형태소 분석기를 사용하여 한국어 텍스트에서 형태소(명사 등) 및 서브스트링 음절 토큰을 추출합니다.
    한국어 조사(은/는/이/가/을/를/의) 결합으로 인한 BM25 스코어 산출 왜곡을 정밀하게 방지합니다.
    """
    if not text or not text.strip():
        return []
    tokens = []
    morphs = [t.form for t in kiwi.tokenize(text)]
    tokens.extend(morphs)
    for m in morphs:
        if len(m) > 1:
            tokens.extend([m[i:i+2] for i in range(len(m)-1)])
            tokens.extend(list(m))
    return tokens

# 환경 변수 로드 (.env)
load_dotenv()

def get_local_llm_client() -> tuple[OpenAI, str]:
    """
    OpenAI API 규격 기반 로컬 LLM 클라이언트 및 엔드포인트 URL을 반환합니다.
    우선순위: OPENAI_BASE_URL > VLLM_API_BASE > http://10.0.0.41:8000/v1 (서버 할당 IP)
    """
    base_url = (
        os.getenv("OPENAI_BASE_URL")
        or os.getenv("VLLM_API_BASE")
        or "http://10.0.0.41:8000/v1"
    )
    api_key = os.getenv("OPENAI_API_KEY", "EMPTY")
    return OpenAI(base_url=base_url, api_key=api_key), base_url

def get_target_model_name() -> str:
    """
    추론 대상 모델명을 반환합니다.
    지원 모델: gemma4-e2b, gemma4-e4b, qwen3.5-2b, qwen3.5-4b, qwen3.5-9b
    우선순위: OPENAI_MODEL_NAME > MODEL_NAME > qwen3.5-2b
    """
    return (
        os.getenv("OPENAI_MODEL_NAME")
        or os.getenv("MODEL_NAME")
        or "qwen3.5-2b"
    )


client, base_url = get_local_llm_client()
model_name = get_target_model_name()


# 1. 주식 댓글 감성 요소 데이터 타입 정의
class StockCommentSentimentItem(TypedDict):
    speaker: str
    category: Literal["실적/재무", "매수/매도 의도", "차트/기술분석", "뉴스/호재·악재", "경영진/주주가치"]
    sentiment: Literal["매수/긍정", "매도/부정", "중립"]
    target: str
    sentence: str
    refined_sentence: str

# 2. 대표 주식 종목 키워드 및 약어/유의어 사전 정의
STOCK_KEYWORDS: set[str] = {
    "삼성전자", "SK하이닉스", "카카오", "카카오뱅크",
    "NAVER", "LG에너지솔루션", "현대차", "NVIDIA", "주식"
}

STOCK_SYNONYM_MAP: dict[str, str] = {
    "삼전": "삼성전자",
    "하닉": "SK하이닉스",
    "카뱅": "카카오뱅크",
    "네이버": "NAVER",
    "엔비": "NVIDIA",
    "상따": "상한가 매수",
    "손절": "매도",
    "익절": "매도",
    "줍줍": "매수",
}

# 3. 동적 서브스트링 오매칭 차단 패턴 딕셔너리 (NEGATIVE_PATTERNS)
# ==============================================================================
# [친절 가이드: 왜 동적 오매칭 차단 패턴이 필요한가요?]
# 한국어 자연어 처리(NLP) 및 RAG 실습에서는 부분 문자열(Substring) 오매칭 이슈가 빈번히 발생합니다.
# 
# 💡 문제 상황 예시:
# 1) '카카오' (주식 종목) ↔ '카카오톡' / '카톡' (단순 메신저 어플리케이션 언급)
#    - 문장: "카카오톡으로 알림 받았습니다."
#    - 타겟을 '카카오'로 매칭할 경우 주식 종목 맥락이 아닌데도 감성이 잘못 추출됩니다.
# 2) '삼성' (삼성전자/삼성그룹 종목) ↔ '삼성동' / '삼성마을' (지명/건물명)
# 3) '현대' (현대차/현대모비스) ↔ '현대백화점' / '현대아파트' (유통/주거)
# 4) '중공업' (HD현대중공업 등) ↔ '중공업부' (부서명)
# 5) '매도' (주식 매도 행위) ↔ '매도인' / '매도자' (부동산/계약 당사자)
# 6) '매수' (주식 매수 행위) ↔ '매수인' / '매수자' (부동산/계약 당사자)
#
# ⚙️ 데이터 구조 및 이관 로드맵 안내:
# - 본 실습 코드는 훈련생의 직관적 이해와 가독성을 위해 파이썬 인메모리 딕셔너리(`dict[str, list[str]]`) 구조로 작성되었습니다.
# - 실무 프로덕션 RAG 시스템 구축 시에는 이 패턴 데이터가 PostgreSQL / SQLite 등의 DBMS 또는 외부 사전 DB 파일로 관리되어 동적으로 적재됩니다.
# ==============================================================================
NEGATIVE_PATTERNS: dict[str, list[str]] = {
    "카카오": ["카카오톡", "카톡", "카카오T", "카카오택시"],
    "삼성": ["삼성동", "삼성마을", "삼성빌라", "삼성아파트", "삼성병원"],
    "현대": ["현대백화점", "현대아파트", "현대카드", "현대캐피탈"],
    "중공업": ["중공업부", "중공업팀"],
    "매도": ["매도인", "매도자", "매도계약서"],
    "매수": ["매수인", "매수자", "매수계약서"],
}

# 4. 정규표현식 기반 <think>...</think> 추론 태그 제거 헬퍼 함수
def strip_think_tags(text: str) -> str:
    """LLM 응답 내 추론 태그(<think>...</think>) 및 내부 텍스트를 정제합니다."""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

# 5. Kiwi 형태소 연동 2단계 하이브리드 BM25 오매칭 검증 클래스
# ==============================================================================
# [친절 가이드: 2단계 하이브리드 BM25 매칭 원리 이해하기]
# 1) 1차 가드레일 (문자열 제거 검증):
#    - text_context에서 query_keyword에 등록된 차단 단어(block_words)를 일시 제거(replace)합니다.
#    - 제거 후 문맥에 키워드가 남아있지 않다면 오매칭으로 판단하여 False (0점 즉시 차단)를 반환합니다.
# 2) 2차 BM25 스코어링 (Kiwi 형태소 연동 평가):
#    - 1차 검증을 통과한 문장에 대해 `kiwipiepy` 형태소 분석기로 문맥과 키워드를 토큰화합니다.
#    - `rank_bm25.BM25Okapi`를 통해 실제 통계적 유사도 점수를 계산하여 점수가 0보다 큰지(`score > 0`) 평가합니다.
# 3) 1차 가드레일 통과 AND 2차 BM25 유사도 점수 양수(> 0) 충족 시 최종 True 반환!
# ==============================================================================
class HybridBM25Matcher:
    """
    NEGATIVE_PATTERNS 딕셔너리 가드레일과 kiwipiepy 연동 BM25Okapi 스코어링을 결합한 2단계 하이브리드 검증 클래스입니다.
    """
    def __init__(self, corpus: list[str], negative_patterns: dict[str, list[str]] | None = None):
        self.corpus = corpus
        self.negative_patterns = negative_patterns or {}
        self.tokenized_corpus = [kiwi_tokenize(doc) for doc in corpus]
        self.bm25 = BM25Okapi(self.tokenized_corpus) if self.tokenized_corpus else None

    def validate_target(self, query_keyword: str, text_context: str) -> bool:
        """
        1차 문자열 가드레일과 2차 Kiwi 형태소 연동 BM25 스코어링(score > 0) 복합 평가를 수행합니다.
        
        Args:
            query_keyword (str): 검증할 주식/금융 대상 키워드 (예: '카카오', '삼성')
            text_context (str): 댓글 문장 원문 (예: '카카오톡 업데이트 알림')
            
        Returns:
            bool: 해당 문장 내에서 키워드가 정당한 독립 대상으로 언급되고 BM25 유사도가 인정되면 True, 아니면 False
        """
        if not query_keyword or not text_context:
            return False

        # 1차 가드레일: 차단 단어 제거 후 독립 존재 여부 검증
        cleaned = text_context
        if query_keyword in self.negative_patterns:
            for block_word in self.negative_patterns[query_keyword]:
                cleaned = cleaned.replace(block_word, "")
            if query_keyword not in cleaned:
                return False

        if query_keyword not in text_context:
            return False

        # 2차 BM25 스코어링: Kiwi 형태소 분석 토큰화 및 BM25Okapi 유사도 계산 (score > 0)
        context_tokens = kiwi_tokenize(cleaned)
        query_tokens = kiwi_tokenize(query_keyword)
        if not context_tokens or not query_tokens:
            return False

        # 문맥 토큰과 corpus 토큰을 조합하여 BM25 스코어링 산출
        temp_bm25 = BM25Okapi([context_tokens] + (self.tokenized_corpus or []))
        scores = temp_bm25.get_scores(query_tokens)
        bm25_score = scores[0] if len(scores) > 0 else 0.0

        return bm25_score > 0

# 5. 프롬프트 시스템 지침 정의
SYSTEM_PROMPT = """주어진 종목 토론방 다자간 대화 댓글 타임라인 및 게시글 메타정보(board_context)를 분석하여, 5가지 주식 투자 카테고리에 해당하는 문장을 파싱하고 화자(speaker), 투자 감성(sentiment), 맥락적 대상 종목(target), 그리고 후속 감성분석 모델 입력용 정제문(refined_sentence)을 추출해 주세요.

## 1. 투자 카테고리 및 감성 정의
- 카테고리 (5가지):
  - 실적/재무: 매출, 영업이익, 4분기 실적, 실적발표, 재무제표 등
  - 매수/매도 의도: 매수 시도, 줍줍, 상따, 손절, 익절, 매도 계획 등
  - 차트/기술분석: 이동평균선, 지지선, 이평선, 반등, 차트 패턴 등
  - 뉴스/호재·악재: 외국인/기관 수급, 호재 공시, 악재 뉴스, 시외 상승 등
  - 경영진/주주가치: 주주환원 정책, 배당, 경영진 응대, 물적분할 등

- 투자 감성 (3가지):
  - 매수/긍정: 호재성 언급, 매수 추천, 긍정 평가
  - 매도/부정: 악재성 언급, 매도 권유, 우려 및 비판
  - 중립: 단순 사실 전달, 질문, 정보 제공

## 2. 추출 및 정제 규칙 (중요)
- 화자 식별: 댓글 작성자 닉네임("작성자명")을 추출하여 `speaker`에 입력합니다. 작성자가 명시되지 않은 경우 "익명"으로 폴백 처리합니다.
- 단순 도배글("ㅋㅋㅋ 대박", "1111")이나 의미 없는 잡담은 자동 제외합니다.
- 대명사 및 약어 대상 복원: 문장 내 '삼전', '하닉', '걔네', '그 종목', '이거' 등의 표현이 있을 경우, 대화 타임라인 및 상위 게시글/종목코드 메타데이터(`board_context`)를 종합적으로 참조하여 정식 종목명("삼성전자", "SK하이닉스")으로 `target`을 복원해 주세요.
- 정제문(refined_sentence) 강화 생성 규칙:
  1. `refined_sentence`는 반드시 `"[정식종목명] 정제문장"` 포맷으로 시작해야 합니다. (예: `"[삼성전자] 오늘 개장 직후 4분기 실적 발표 내용 확인하셨나요?"`)
  2. 주어가 생략된 댓글 문장의 경우, 정식 종목명을 주어로 명시하여 완결된 문장으로 정제합니다. (예: "60일선 지지받고 반등 시도 중" ➡️ `"[삼성전자] 60일 이동평균선 지지받고 갭상승 반등 시도 중입니다."`)
  3. "삼전/하닉/걔네/이거" 등의 약어와 지시 대명사를 정식 종목명으로 전면 대체합니다.
  4. "줍줍", "상따", "손절 쳐야 함" 등 커뮤니티 은어/속어를 정식 금융 어휘("매수", "상한가 매수", "손절매")로 정제하여 다운스트림 감성분석 모델이 문장 하나만 보고도 즉시 감성을 정밀 분류할 수 있는 완성형 문장으로 가공해 주세요.

## 3. 출력 형식
출력은 반드시 다른 설명 없이 아래의 JSON 객체 형식으로만 작성해야 합니다. 최상위 키 이름은 반드시 "results"로 지정해 주세요.

{
  "results": [
    {
      "speaker": "댓글 작성자 닉네임",
      "category": "실적/재무 | 매수/매도 의도 | 차트/기술분석 | 뉴스/호재·악재 | 경영진/주주가치 중 하나",
      "sentiment": "매수/긍정 | 매도/부정 | 중립 중 하나",
      "target": "복원된 정식 종목명 (예: 삼성전자, SK하이닉스)",
      "sentence": "추출한 댓글 원문 문장",
      "refined_sentence": "[정식종목명] 대명사/약어/은어가 정식 용어로 정제된 감성분석 모델 입력용 독립 문장"
    }
  ]
}
"""

# 6. 핵심 추출 파이프라인 함수
def process_stock_comment_sentiment_extraction(
    comments_timeline: str, 
    board_context: str = "",
    llm_client: OpenAI | None = None
) -> list[dict[str, str]]:

    """
    5단계 하이브리드 파이프라인(LLM 화자/맥락 복원, 유의어 정규화, BM25 희소 검증, 가드레일, 감성모델용 정제문 생성)을 통해
    시간순 종목 토론 댓글에서 5대 주식 투자 감성 문장 및 정제문(refined_sentence)을 파싱하여 반환합니다.
    """
    if not comments_timeline or not comments_timeline.strip():
        return []

    print("[시스템] 종목 토론방 댓글 타임라인 감성 분석을 시작합니다...")
    print("[시스템] 1단계: 화자(speaker) 식별, 지시어/약어 대상(target) 복원 및 정제문(refined_sentence) 생성 진행 중...")

    user_input_content = f"## 상위 게시글/종목 메타정보\n{board_context if board_context else '없음'}\n\n## 분석할 댓글 타임라인\n\"{comments_timeline}\""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input_content}
    ]

    active_client = client if llm_client is None else llm_client
    target_model = get_target_model_name()

    try:
        try:
            response = active_client.chat.completions.create(
                model=target_model,
                messages=messages,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
        except Exception as json_mode_err:
            # response_format json_object 미지원 소형 모델 폴백 (일반 추론 후 태스크 정제)
            response = active_client.chat.completions.create(
                model=target_model,
                messages=messages,
                temperature=0.1
            )
        raw_content = response.choices[0].message.content or "{\"results\": []}"
    except Exception as e:
        print(f"[시스템] 로컬 LLM 서버 연결 실패: {base_url} 서버 상태를 확인하세요 ({e})")
        return []



    # 2단계: <think> 태그 제거 및 JSON 객체 변환
    cleaned_content = strip_think_tags(raw_content)
    try:
        data = json.loads(cleaned_content)
        if isinstance(data, dict):
            results = data.get("results", data.get("comments", data.get("items", [])))
            if not results and isinstance(data, list):
                results = data
        elif isinstance(data, list):
            results = data
        else:
            results = []
    except json.JSONDecodeError:
        print("[시스템] 경고: JSON 파싱 실패. 빈 결과를 반환합니다.")
        return []

    print("[시스템] 2단계: 주식 도메인 유의어/약어 사전 기반 정규화 진행 중...")
    normalized_results = []
    for item in results:
        speaker = item.get("speaker", "익명").strip()
        category = item.get("category", "").strip()
        sentiment = item.get("sentiment", "중립").strip()
        target = item.get("target", "").strip()
        sentence = item.get("sentence", "").strip()
        refined_sentence = item.get("refined_sentence", "").strip()

        # 약어 정규화
        target = STOCK_SYNONYM_MAP.get(target, target)
        
        # refined_sentence 기본 폴백 생성
        if not refined_sentence:
            refined_sentence = f"[{target}] {sentence}"

        normalized_results.append({
            "speaker": speaker,
            "category": category,
            "sentiment": sentiment,
            "target": target,
            "sentence": sentence,
            "refined_sentence": refined_sentence
        })

    print("[시스템] 3단계: 동적 NEGATIVE_PATTERNS 기반 서브스트링 오매칭 검증 진행 중...")
    matcher = HybridBM25Matcher(list(STOCK_KEYWORDS), negative_patterns=NEGATIVE_PATTERNS)

    # ==========================================================================
    # [친절 가이드: 3단계 오매칭 차단 필터 루프의 핵심]
    # ⚠️ 훈련생 주의사항: `if target_val == neg_keyword` (정확 일치) 조건!
    # - 만약 `if neg_keyword in target_val` (부분 포함)로 작성하면?
    #   target_val이 '카카오뱅크'일 때도 neg_keyword('카카오')가 포함되어 잘못 차단될 수 있습니다.
    # - 따라서 target_val이 정확히 '카카오'일 때만 차단기 검증을 수행하고,
    #   '카카오뱅크'처럼 독립된 다른 종목은 검증 없이 그대로 통과시킵니다.
    # ==========================================================================
    final_results = []
    for item in normalized_results:
        target_val = item["target"]
        sentence_val = item["sentence"]

        # 동적 차단 패턴에 등록된 키워드와 target이 정확히 일치할 때만 검증 (하드코딩 없음)
        # 예: target='카카오'이면 검증 발동, target='카카오뱅크'이면 통과
        is_blocked = False
        for neg_keyword in NEGATIVE_PATTERNS:
            if target_val == neg_keyword and not matcher.validate_target(neg_keyword, sentence_val):
                print(f"[시스템] 서브스트링 오매칭 차단: target('{target_val}')이 '{neg_keyword}' 종목 맥락에 일치하지 않습니다.")
                is_blocked = True
                break
        if is_blocked:
            continue

        final_results.append(item)

    print(f"[시스템] 분석 완료. 총 {len(final_results)}개의 주식 투자 감성 문장이 추출되었습니다.\n")
    return final_results


# 7. 실습 메인 실행부
if __name__ == "__main__":
    print("=" * 60)
    print(" [실습 1: 시간순 종목 토론방 다자간 대화 화자 파악 및 약어/지시어/5대 투자가치 복원]")
    print("=" * 60)
    sample_timeline_1 = (
        "주식초보 (14:00): 오늘 개장하자마자 삼전 4분기 실적 발표 나온 거 보셨나요?\n"
        "차트분석가 (14:01): 넵 어닝 서프라이즈 나왔네요. 덕분에 60일 이동평균선 지지받고 갭상승 반등 시도 중입니다.\n"
        "가치투자자 (14:02): 영업이익이 전년 대비 40% 증가했던데 이번에 주주환원 배당금 확대 소식도 같이 발표했더라고요.\n"
        "개미왕 (14:03): 삼전이랑 하닉 둘 다 시외 거래에서 급등하길래 바로 줍줍 했습니다.\n"
        "주식초보 (14:04): 걔네 오늘 기관이랑 외국인 동반 순매수 물량이 엄청나게 들어왔네요.\n"
        "단타의신 (14:05): ㅋㅋㅋ 대박 대박 가자 111111\n"
        "단타의신 (14:06): 하지만 8만원대 저항선 물량이 켜켜이 쌓여있어서 단기 손절 라인은 잡아둬야 할 듯합니다.\n"
        "개미왕 (14:07): 아싸 오늘 밤에 치킨 먹는다 ㅋㅋㅋㅋㅋ\n"
        "주주대표 (14:08): 경영진이 이번 신규 이사회에서 자사주 소각 건까지 의결해주면 최고일 텐데요."
    )

    print("\n[입력 댓글 타임라인 1]")
    print(sample_timeline_1 + "\n")

    extracted_items_1 = process_stock_comment_sentiment_extraction(sample_timeline_1)

    print("[최종 추출 결과 1 JSON (감성분석 모델 입력용 refined_sentence 포함)]")
    print(json.dumps(extracted_items_1, ensure_ascii=False, indent=2))

    print("\n" + "=" * 60)
    print(" [실습 2: 게시글/종목 메타데이터(board_context) 결합 대명사 복원 & BM25 차단 검증]")
    print("=" * 60)
    
    board_context_2 = "[005930] 삼성전자 & [035720] 카카오 토론방 - AI 반도체 수급 및 커뮤니티 사업 실적 전망"
    sample_timeline_2 = (
        "동학개미 (14:10): 주가 흐름 보니까 이거 오늘 외국인이 500만주 넘게 싹 쓸어 담았네요.\n"
        "전업투자자 (14:11): 걔네 HBM 공급 계약 뉴스 터진 게 결정적이었던 것 같습니다.\n"
        "차트매니아 (14:12): 차트상 전고점 돌파 직전이라 손절가 짧게 잡고 매수 들어가봅니다.\n"
        "모바일유저 (14:13): 카카오톡 최신 버전 이모티콘이랑 메신저 기능 업데이트가 정말 편해졌더라고요.\n"
        "개미보호 (14:14): 카뱅 신규 대출 금리 할인이랑 플랫폼 매출 성장세도 꽤 긍정적입니다."
    )

    print(f"\n[상위 게시글 메타정보]\n{board_context_2}")
    print(f"\n[입력 댓글 타임라인 2]\n{sample_timeline_2}\n")

    extracted_items_2 = process_stock_comment_sentiment_extraction(sample_timeline_2, board_context=board_context_2)

    print("[최종 추출 결과 2 JSON (감성분석 모델 입력용 refined_sentence 포함)]")
    print(json.dumps(extracted_items_2, ensure_ascii=False, indent=2))

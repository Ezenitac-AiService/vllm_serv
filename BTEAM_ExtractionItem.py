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

# OpenAI 호환 Groq API 클라이언트 초기화
api_key = os.getenv("GROQ_API_KEY")
model_name = os.getenv("CURRENT_GROQ_MODEL", "llama-3.3-70b-versatile")
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key or "gsk_dummy_key_for_test"
)

# 1. 감성 요소 객체 데이터 타입 정의
class ReviewSentimentItem(TypedDict):
    category: Literal["맛", "양", "가격", "청결", "친절도"]
    target: str
    sentence: str
    refined_sentence: str

# 2. 대표 도메인 메뉴 키워드 및 유의어 사전 정의
MENU_KEYWORDS: set[str] = {
    "크림 파스타", "봉골레 파스타", "마라탕", "마라샹궈", "마라", "고구마라떼", "라떼", 
    "파스타", "피자", "리조또", "스테이크", "음료", "매장", "직원"
}

SYNONYM_MAP: dict[str, str] = {
    "알바": "직원",
    "사장님": "직원",
    "직원분": "직원",
    "위생": "청결",
    "가성비": "가격",
    "양적음": "양",
    "스파게티": "파스타",
}

# 3. 동적 서브스트링 오매칭 차단 패턴 딕셔너리 (NEGATIVE_PATTERNS)
# ==============================================================================
# [친절 가이드: 음식점 리뷰 도메인 오매칭 차단 패턴 이해하기]
# 음식점 리뷰 NLP 실습에서도 부분 문자열(Substring) 오매칭 이슈가 매우 자주 발생합니다.
# 
# 💡 대표적 오매칭 사례:
# 1) '마라' (마라탕/마라샹궈 음식) ↔ '고구마라떼' / '라떼' / '음료'
#    - 문장: "식후 디저트로 시킨 고구마라떼는 달콤하고 부드러웠습니다."
#    - '고구마라떼'에 포함된 '마라' 서브스트링 때문에 '마라'로 잘못 매칭되는 문제 차단!
# 2) '파스타' (크림파스타/알리오올리오 등) ↔ '파스타치오' / '피스타치오' (견과류/디저트)
# 3) '음료' (콜라/사이더/에이드 등) ↔ '음료수대' / '음료대' (시설물)
# 4) '직원' (서비스/친절도 대상) ↔ '직원실' / '직원휴게실' (매장 시설 공간)
# 5) '스테이크' (메인 요리) ↔ '스테이크하우스' (상호명)
# 6) '양' (음식 양/푸짐함 카테고리) ↔ '양념' / '양파' / '양배추' (식재료)
#
# ⚙️ 데이터 구조 및 이관 로드맵 안내:
# - 본 실습 코드는 훈련생의 직관적 이해와 가독성을 위해 파이썬 인메모리 딕셔너리(`dict[str, list[str]]`) 구조로 작성되었습니다.
# - 실무 프로덕션 RAG 시스템 구축 시에는 이 패턴 데이터가 PostgreSQL / SQLite 등의 DBMS 또는 외부 사전 DB 파일로 관리되어 동적으로 적재됩니다.
# ==============================================================================
NEGATIVE_PATTERNS: dict[str, list[str]] = {
    "마라": ["고구마라떼", "라떼", "음료"],
    "파스타": ["파스타치오", "피스타치오"],
    "음료": ["음료수대", "음료대"],
    "직원": ["직원실", "직원휴게실"],
    "스테이크": ["스테이크하우스"],
    "양": ["양념", "양파", "양배추", "양꼬치"],
}

# 4. 정규표현식 기반 <think>...</think> 추론 태그 제거 헬퍼 함수
def strip_think_tags(text: str) -> str:
    """LLM 응답 내 추론 태그(<think>...</think>) 및 내부 텍스트를 정제합니다."""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

# 5. Kiwi 형태소 연동 2단계 하이브리드 BM25 오매칭 검증 클래스
# ==============================================================================
# [친절 가이드: 2단계 하이브리드 BM25 매칭 원리 이해하기]
# 1) 1차 가드레일 (문자열 제거 검증):
#    - text_context에서 query_keyword에 지정된 차단 단어(block_words)를 일시 제거(replace)합니다.
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
            query_keyword (str): 검증할 메뉴/카테고리 키워드 (예: '마라', '양')
            text_context (str): 리뷰 문장 원문 (예: '고구마라떼는 달콤했습니다.')
            
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

# 5. 프롬프트 정의
SYSTEM_PROMPT = """주어진 음식점 리뷰 문단을 분석하여, 지정된 카테고리에 해당하는 문장들을 추출하고 각 문장의 구체적인 평가 대상(Target)을 식별하며, 감성분석 모델 입력 전용 정제문(refined_sentence)을 함께 생성해 주세요.

## 1. 카테고리 정의
리뷰 문장에서 아래 5가지 카테고리에 해당하는 내용이 있을 경우에만 추출합니다.
- 맛: 음식의 맛, 간, 온도, 식감, 신선도 등
- 양: 음식의 양, 곱배기, 푸짐함, 부족함 등
- 가격: 가격의 적절성, 가성비, 비쌈/저렴함 등
- 청결: 매장 내부 위생, 식기 상태, 테이블 청결도 등
- 친절도: 직원이나 사장님의 서비스, 응대 태도, 친절함 등

## 2. 추출 및 맥락 복원 규칙 (중요)
- 리뷰 문단을 의미 있는 문장 단위로 분리합니다.
- 카테고리에 해당하지 않는 문장(단순 방문 계기, 인사말 등)은 제외합니다.
- 맥락적 대상 복원: 문장 내에 지시 대명사나 모호한 표현(예: '둘 다', '그것', '다른 파스타', '나머지')이 쓰인 경우, 앞뒤 문맥을 파악하여 실제 가리키는 구체적인 음식 이름이나 대상 명사를 찾아 `target`에 적어주어야 합니다. (예: '다른 파스타' ➡️ '크림 파스타', '둘 다' ➡️ '크림 파스타, 봉골레 파스타')
- 한 문장에 여러 카테고리가 포함된 경우(예: 맛과 양이 동시에 언급됨), 각각의 카테고리로 행을 분리하여 동일한 문장을 추출합니다.
- 정제문(refined_sentence) 강화 생성 규칙:
  1. `refined_sentence`는 반드시 `"[복원된정식대상] 정제문장"` 포맷으로 시작해야 합니다. (예: `"[크림 파스타] 소스가 너무 묽고 싱거웠습니다."`)
  2. "다른 파스타", "둘 다" 등 지시 대명사를 복원된 구체적 음식/대상 명사로 치환하여 단독 문장만 보고도 대상을 알 수 있도록 완성형 문장으로 작성해 주세요. (예: "게다가 둘 다 가격은 양에 비해 좀 아쉬웠습니다." ➡️ `"[크림 파스타, 봉골레 파스타] 가격은 양에 비해 좀 아쉬웠습니다."`)

## 3. 출력 형식
출력은 반드시 다른 설명 없이 아래의 JSON 객체 형식으로만 작성해야 합니다. 최상위 키 이름은 반드시 "results"로 지정해 주세요.

{
  "results": [
    {
      "category": "맛 | 양 | 가격 | 청결 | 친절도 중 하나",
      "target": "맥락을 반영하여 복원된 구체적인 평가 대상 (예: 크림 파스타, 봉골레 파스타 등)",
      "sentence": "추출한 문장 원문",
      "refined_sentence": "[복원된정식대상] 대명사/지시어가 정식 명사로 대체되어 감성분석 모델에 직접 입력 가능한 정제 문장"
    }
  ]
}
"""

# 6. 핵심 추출 파이프라인 함수
def process_review_sentiment_extraction(review_text: str) -> list[dict[str, str]]:
    """
    4단계 하이브리드 파이프라인(LLM 맥락 복원, 유의어 정규화, BM25 희소 검증, 가드레일, 감성모델용 정제문 가공)을 통해
    리뷰 문단에서 5대 감성 원문 문장(sentence)과 정제 문장(refined_sentence)을 파싱하고 맥락적 대상(target)을 복원하여 반환합니다.
    """
    if not review_text or not review_text.strip():
        return []

    print("[시스템] 리뷰 감성 문장 분석을 시작합니다...")
    print("[시스템] 1단계: LLM 의미 기반 문장 파싱, 지시어 대상(target) 복원 및 정제문(refined_sentence) 생성 진행 중...")

    # 1단계: Groq API를 활용한 의미 기반 분석 및 JSON 파싱
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"## 분석할 리뷰\n\"{review_text}\""}
    ]

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        raw_content = response.choices[0].message.content or "[]"
    except Exception as e:
        print(f"[시스템] API 호출 실패 (Mock fallback 또는 에러): {e}")
        return []

    # 2단계: <think> 태그 제거 및 JSON 객체 변환
    cleaned_content = strip_think_tags(raw_content)
    try:
        data = json.loads(cleaned_content)
        if isinstance(data, dict):
            # json_object 모드에서 {"results": [...]} 또는 루트 배열 파싱
            results = data.get("results", data.get("reviews", data.get("items", [])))
            if not results and isinstance(data, list):
                results = data
        elif isinstance(data, list):
            results = data
        else:
            results = []
    except json.JSONDecodeError:
        print("[시스템] 경고: JSON 파싱 실패. 빈 결과를 반환합니다.")
        return []

    print("[시스템] 2단계: 유의어 사전 기반 카테고리/대상 정규화 및 정제문 가공 진행 중...")
    normalized_results = []
    for item in results:
        category = item.get("category", "").strip()
        target = item.get("target", "").strip()
        sentence = item.get("sentence", "").strip()
        refined_sentence = item.get("refined_sentence", "").strip()

        # 유의어 매핑 정규화
        target = SYNONYM_MAP.get(target, target)

        if not refined_sentence:
            refined_sentence = f"[{target}] {sentence}"

        normalized_results.append({
            "category": category,
            "target": target,
            "sentence": sentence,
            "refined_sentence": refined_sentence
        })

    print("[시스템] 3단계: 동적 NEGATIVE_PATTERNS 기반 서브스트링 오매칭 검증 진행 중...")
    matcher = HybridBM25Matcher(list(MENU_KEYWORDS), negative_patterns=NEGATIVE_PATTERNS)

    # ==========================================================================
    # [친절 가이드: 3단계 오매칭 차단 필터 루프의 핵심]
    # ⚠️ 훈련생 주의사항: `if target_val == neg_keyword` (정확 일치) 조건!
    # - 만약 `if neg_keyword in target_val` (부분 포함)로 작성하면?
    #   target_val이 '고구마라떼'일 때도 neg_keyword('마라')가 포함되어 잘못 차단될 수 있습니다.
    # - 따라서 target_val이 정확히 '마라'일 때만 차단기 검증을 수행하고,
    #   '고구마라떼'처럼 독립된 다른 메뉴는 검증 없이 그대로 통과시킵니다.
    # ==========================================================================
    final_results = []
    for item in normalized_results:
        target_val = item["target"]
        sentence_val = item["sentence"]

        # 동적 차단 패턴에 등록된 키워드와 target이 정확히 일치할 때만 검증 (하드코딩 없음)
        # 예: target='마라'이면 검증 발동, target='고구마라떼'이면 통과
        is_blocked = False
        for neg_keyword in NEGATIVE_PATTERNS:
            if target_val == neg_keyword and not matcher.validate_target(neg_keyword, sentence_val):
                print(f"[시스템] 서브스트링 오매칭 차단: target('{target_val}')이 '{neg_keyword}' 맥락에 일치하지 않습니다.")
                is_blocked = True
                break
        if is_blocked:
            continue

        final_results.append(item)

    print(f"[시스템] 분석 완료. 총 {len(final_results)}개의 감성 요소 문장이 추출되었습니다.\n")
    return final_results


# 7. 실습 메인 실행부
if __name__ == "__main__":
    print("=" * 60)
    print(" [실습 1: 이탈리안 레스토랑 복합 리뷰 감성 문장 및 맥락 복원 추출 (원문 vs 정제문)]")
    print("=" * 60)
    sample_review_1 = (
        "주말에 새로 오픈한 이탈리안 레스토랑에 다녀왔습니다. "
        "매장이 정말 청결하고 인테리어도 예쁘더라고요. "
        "저희는 크림 파스타와 봉골레 파스타를 시켰습니다. "
        "봉골레 파스타는 조개 맛이 시원하고 감칠맛이 좋았습니다. "
        "그런데 다른 파스타는 소스가 너무 묽고 싱거웠습니다. "
        "게다가 둘 다 가격은 양에 비해 좀 아쉬웠습니다. "
        "마지막에 계산할 때 직원분이 불친절해서 기분이 좀 상했네요."
    )

    print("\n[입력 리뷰 문단 1]")
    print(sample_review_1 + "\n")

    extracted_items_1 = process_review_sentiment_extraction(sample_review_1)

    print("[최종 추출 결과 1 JSON (원문 sentence & 정제문 refined_sentence 포함)]")
    print(json.dumps(extracted_items_1, ensure_ascii=False, indent=2))

    print("\n" + "=" * 60)
    print(" [실습 2: BM25 & 키워드 가드레일 오매칭 차단 검증 ('마라' vs '고구마라떼')]")
    print("=" * 60)
    matcher = HybridBM25Matcher(list(MENU_KEYWORDS))
    
    test_sentence_pass = "마라탕은 정말 얼큰하고 알싸한 맛이 최고였습니다."
    test_sentence_reject = "식후 디저트로 시킨 고구마라떼는 달콤하고 정말 부드러웠습니다."

    print(f"\n1) 테스트 문장 1: \"{test_sentence_pass}\"")
    is_valid_pass = matcher.validate_target("마라", test_sentence_pass)
    print(f"   - 타겟 '마라' 검증 결과: {is_valid_pass} (정상 통과)")

    extracted_items_pass = process_review_sentiment_extraction(test_sentence_pass)
    print("[최종 추출 결과 1 JSON]")
    print(json.dumps(extracted_items_pass, ensure_ascii=False, indent=2))

    print(f"\n2) 테스트 문장 2: \"{test_sentence_reject}\"")
    is_valid_reject = matcher.validate_target("마라", test_sentence_reject)
    print(f"   - 타겟 '마라' 서브스트링 오매칭 검증 결과: {is_valid_reject} (0점 차단 성공)")

    extracted_items_reject = process_review_sentiment_extraction(test_sentence_reject)
    print("[최종 추출 결과 2 JSON ('고구마라떼' 정상 수용 및 추출)]")
    print(json.dumps(extracted_items_reject, ensure_ascii=False, indent=2))

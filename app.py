import os
import re
import json
from pypdf import PdfReader
import streamlit as st
from google import genai
from google.genai import types

# ==========================================
# 1. 기본 설정 및 커스텀 CSS
# ==========================================
st.set_page_config(
    page_title="2026 고등학교 생기부 기재요령 Q&A",
    page_icon="📘",
    layout="wide",
)

CUSTOM_CSS = """
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

html, body, [class*="css"] {
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Malgun Gothic', sans-serif;
    word-break: keep-all;
}

.block-container {
    max-width: 920px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

/* 상단 헤더 배너 */
.hero-header {
    background: linear-gradient(135deg, #f0f5ff 0%, #f8fafc 100%);
    border: 1px solid #dbeafe;
    border-radius: 16px;
    padding: 1.6rem 2rem;
    margin-bottom: 1.8rem;
}
.hero-badge {
    display: inline-block;
    background-color: #2563eb;
    color: #ffffff;
    font-size: 0.78rem;
    font-weight: 600;
    padding: 0.25rem 0.7rem;
    border-radius: 999px;
    margin-bottom: 0.6rem;
    letter-spacing: -0.01em;
}
.hero-title {
    font-size: 1.75rem;
    font-weight: 800;
    color: #0f172a;
    margin: 0 0 0.45rem 0;
    letter-spacing: -0.02em;
}
.hero-subtitle {
    font-size: 0.95rem;
    color: #475569;
    margin: 0;
    line-height: 1.55;
}

/* 채팅 메시지 기본 카드 */
[data-testid="stChatMessage"] {
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.9rem;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
}

/* 질문 카드: 연회색 배경 */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background-color: #f1f5f9;
    border: 1px solid #cbd5e1;
}

/* 답변 카드: 깔끔한 흰색 배경 */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
}

/* 질문 아이콘: 파스텔 파란색 */
[data-testid="stChatMessageAvatarUser"] {
    background-color: #dbeafe !important;
    color: #1d4ed8 !important;
    border: 1px solid #bfdbfe !important;
}

/* 답변 아이콘: 파스텔 코랄/피치색 */
[data-testid="stChatMessageAvatarAssistant"] {
    background-color: #ffedd5 !important;
    color: #c2410c !important;
    border: 1px solid #fed7aa !important;
}

/* 표(Table) 디자인 및 한글 줄바꿈 깨짐 방지 */
[data-testid="stChatMessage"] table {
    width: 100%;
    border-collapse: collapse;
    margin: 0.9rem 0 1.1rem 0;
    font-size: 0.92rem;
    line-height: 1.6;
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid #e2e8f0;
}
[data-testid="stChatMessage"] thead th {
    background-color: #f1f5f9;
    color: #1e293b;
    font-weight: 700;
    text-align: left;
    padding: 0.75rem 0.9rem;
    border-bottom: 2px solid #cbd5e1;
    word-break: keep-all;
}
[data-testid="stChatMessage"] tbody td {
    padding: 0.75rem 0.9rem;
    border-bottom: 1px solid #e2e8f0;
    vertical-align: top;
    color: #334155;
    word-break: keep-all;
}
[data-testid="stChatMessage"] tbody td:first-child,
[data-testid="stChatMessage"] thead th:first-child {
    min-width: 135px;
    font-weight: 600;
    color: #0f172a;
    background-color: #f8fafc;
}
[data-testid="stChatMessage"] tbody tr:last-child td {
    border-bottom: none;
}

/* 임호고 자체 기준 보충 박스 */
.imho-box {
    background-color: #fffbeb;
    border: 1px solid #fde68a;
    border-left: 4px solid #d97706;
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    margin-top: 0.8rem;
    margin-bottom: 0.7rem;
    color: #78350f;
    font-size: 0.93rem;
    line-height: 1.6;
}
.imho-box-title {
    font-weight: 700;
    color: #92400e;
    margin-bottom: 0.35rem;
    font-size: 0.95rem;
}

/* 근거 배지 */
.source-badge {
    display: inline-block;
    background-color: #f8fafc;
    color: #475569;
    font-size: 0.82rem;
    padding: 0.3rem 0.75rem;
    border-radius: 8px;
    margin-top: 0.4rem;
    margin-bottom: 0.6rem;
    border: 1px solid #e2e8f0;
}

/* 버튼 스타일 */
.stButton > button {
    border-radius: 10px;
    border: 1px solid #e2e8f0;
    background-color: #ffffff;
    color: #1e293b;
    font-weight: 500;
    text-align: left;
    padding: 0.6rem 0.9rem;
    transition: all 0.15s ease;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
}
.stButton > button:hover {
    border-color: #3b82f6;
    background-color: #eff6ff;
    color: #1d4ed8;
    transform: translateY(-1px);
}

[data-testid="stSidebar"] {
    background-color: #f8fafc;
    border-right: 1px solid #e2e8f0;
}

/* 모바일 화면(가로 768px 이하) 글자 크기 및 여백 최적화 */
@media (max-width: 768px) {
    .block-container {
        padding-top: 1rem;
        padding-left: 0.9rem;
        padding-right: 0.9rem;
        padding-bottom: 3rem;
    }
    .hero-header {
        padding: 1.1rem 1.2rem;
        border-radius: 12px;
        margin-bottom: 1.1rem;
    }
    .hero-badge {
        font-size: 0.7rem;
        padding: 0.2rem 0.55rem;
    }
    .hero-title {
        font-size: 1.25rem;
    }
    .hero-subtitle {
        font-size: 0.84rem;
        line-height: 1.45;
    }
    [data-testid="stChatMessage"] {
        padding: 0.85rem 0.95rem;
        font-size: 0.9rem;
        line-height: 1.55;
    }
    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li {
        font-size: 0.9rem;
    }
    [data-testid="stChatMessage"] table {
        font-size: 0.8rem;
        line-height: 1.45;
    }
    [data-testid="stChatMessage"] thead th,
    [data-testid="stChatMessage"] tbody td {
        padding: 0.55rem 0.6rem;
    }
    [data-testid="stChatMessage"] tbody td:first-child,
    [data-testid="stChatMessage"] thead th:first-child {
        min-width: 88px;
    }
    .imho-box {
        padding: 0.75rem 0.85rem;
        font-size: 0.84rem;
    }
    .imho-box-title {
        font-size: 0.88rem;
    }
    .source-badge {
        font-size: 0.76rem;
    }
    .stButton > button {
        font-size: 0.84rem;
        padding: 0.5rem 0.7rem;
    }
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

PDF_PATH = "guide_2026.pdf"
IMHO_PDF_PATH = "imho_2026_v1.pdf"
CACHE_PATH = "pdf_cache.json"
KEY_FILE = "api_key.txt"

SYNONYM_MAP = {
    "세특": ["세부능력 및 특기사항", "세부능력", "특기사항"],
    "행특": ["행동특성 및 종합의견", "행동특성", "종합의견"],
    "창체": ["창의적 체험활동", "자율·자치활동", "동아리활동", "진로활동", "봉사활동"],
    "자율": ["자율·자치활동", "자율활동"],
    "동아리": ["동아리활동", "자율동아리", "학교스포츠클럽"],
    "진로": ["진로활동", "진로희망"],
    "봉사": ["봉사활동", "봉사활동실적"],
    "학폭": ["학교폭력", "조치상황", "전담기구"],
    "생기부": ["학교생활기록부"],
    "공결": ["출석인정", "출석 인정 결석"],
    "인정결석": ["출석인정", "출석 인정 결석"],
    "병결": ["질병으로 인한 결석", "질병결석"],
    "미인정": ["미인정 결석"],
    "체험학습": ["교외체험학습"],
    "수상": ["수상경력", "교내상", "대회"],
    "대회": ["수상경력", "교내대회", "교외대회"],
    "정정": ["자료의 정정", "정정대장"],
    "독서": ["독서활동상황"],
    "자격증": ["자격증 취득", "국가직무능력표준"],
    "지필": ["정기시험"],
    "수행": ["수행평가"],
    "학점제": ["고교학점제", "학점", "미이수", "최소 성취수준"],
    "학적": ["인적·학적사항", "전입학", "편입학", "재입학", "자퇴", "휴학", "유급"],
    "누가": ["누가기록", "보조부"],
}

STOPWORDS = {
    "은", "는", "이", "가", "을", "를", "에", "의", "로", "으로", "에서", "도", "만", "과", "와",
    "어떻게", "어떨", "언제", "어디", "무엇", "뭐", "왜", "누가", "알려줘", "궁금해요", "궁금해",
    "인가요", "하나요", "되나요", "있나요", "없나요", "써야돼", "써도", "해도", "가능해", "관련",
    "관련된", "내용", "경우", "대해", "대한", "학생", "선생님", "질문", "답변",
}

SUFFIXES = ("에서는", "으로는", "에서", "으로", "까지", "부터", "처럼", "보다", "은", "는", "이", "가", "을", "를", "로", "에", "의", "와", "과", "도", "만")

SYSTEM_PROMPT = """
당신은 대한민국 고등학교 '2026학년도 학교생활기록부 기재요령' 및 '김해 임호고등학교 자체 기준' 전문 안내 도우미입니다.
반드시 제공된 [교육부 기재요령 원문]과 [임호고 자체 기준]만을 근거로 아래 규칙을 철저히 지켜 JSON 형식으로 답변하세요.

[답변 규칙]
1. [질문 유형에 맞는 자연스러운 첫 문장]
  - 가능/불가능을 묻는 질문("~해도 돼?", "~인가요?")에는 "가능합니다.", "안 됩니다.", "원칙적으로 불가합니다."처럼 결론을 먼저 명확히 말하세요.
  - 기준·방법·일정을 묻는 질문("어떤 경우에~?", "어떻게~?", "언제야?")에는 절대 "가능합니다/안 됩니다"로 시작하지 말고, 핵심 내용을 요약하는 자연스러운 문장으로 시작하세요.

2. [가독성 극대화 (표와 글머리 기호 적극 활용)]
- 유형별·항목별·학년별(1·2학년 vs 3학년) 기준을 비교하거나 조건이 2가지 이상일 때는 **마크다운 표(Table)**로 정리하세요.
  - 표의 첫 번째 열(항목명)은 짧고 간결하게 적고, 부가 유의사항이나 예외 조항은 표 아래에 글머리 기호(`-`)로 분리해 적으세요.
  - 표 셀 안에서 줄바꿈이 꼭 필요할 때만 `<br>`을 사용하세요.

3. [원문에 없는 구체적 사례 처리 — 자의적 판단·왜곡 절대 금지]
- 질문한 특정 사례가 [교육부 기재요령 원문]과 [임호고 자체 기준] 어디에도 **직접 명시되어 있지 않다면**, 절대 추측해 단정하지 마세요.
  - 대신 ① "기재요령 원문에는 'OO'에 대한 직접적인 규정이 명시되어 있지 않습니다."라고 선을 긋고, ② "다만, 판단 시 참고할 수 있는 관련 규정은 다음과 같습니다."로 일반 원칙을 객관적으로 제시하세요.

4. [임호고 자체 기준 보충 (`imho_note` 필드 활용 — 중복 금지)]
- `answer`는 기본적으로 [교육부 기재요령 원문]을 중심으로 작성하세요. (단, 질문 자체가 임호고 1학기 마감 일정·교차 점검자 등 학교 내부 사안인 경우 `answer`에 바로 답하세요.)
  - [임호고 자체 기준]에 질문과 관련된 **학교장 결정 사항, 학업성적관리위원회 심의 결과, 본교만의 예외·세부 기준**이 있는 경우에만 `imho_note`에 간결하게 작성하세요.
  - **[중요] 중복 금지:** [임호고 자체 기준]의 내용이 [교육부 기재요령 원문]과 동일한 일반 개정 사항이라면 `imho_note`를 반드시 빈 문자열(`""`)로 비워두세요.

5. [1·2학년 vs 3학년 구분 및 출처·추가 질문]
- 1·2학년(2022 개정 교육과정)과 3학년 규정이 다른 항목은 반드시 구분해 설명하세요.
  - `source`: 근거가 된 기재요령 쪽수/항목명 (임호고 자료를 참고한 경우 함께 표기. 예: 2026 기재요령 58쪽 '출결상황' / 임호고 자체 기준 2쪽)
  - `follow_up_questions`: 이어서 궁금해할 실무 질문 3개를 짧고 구체적으로 제시하세요.

[출력 JSON 형식]
{
  "answer": "교육부 기재요령 기반의 마크다운(표, 글머리 기호 포함) 답변",
  "imho_note": "임호고 학교장 결정/자체 예외 기준이 있을 때만 간결하게 작성 (없거나 교육부 기준과 동일하면 반드시 빈 문자열 '')",
  "source": "2026 기재요령 OO쪽 '항목명'",
  "follow_up_questions": [
    "관련 추가 질문 1",
    "관련 추가 질문 2",
    "관련 추가 질문 3"
  ]
}
"""

# ==========================================
# 2. 유틸리티 함수
# ==========================================
def get_saved_api_key() -> str:
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"].strip()
    except Exception:
        pass
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r", encoding="utf-8") as f:
            key = f.read().strip()
            if key:
                return key
    return ""


@st.cache_data(ttl=3600, show_spinner=False)
def get_candidate_models(api_key: str):
    fallback = ["gemini-3.8-flash-lite", "gemini-2.5-flash-lite", "gemini-3.8-flash", "gemini-2.0-flash"]
    try:
        client = genai.Client(api_key=api_key)
        found = []
        for m in client.models.list():
            name = (m.name or "").replace("models/", "")
            methods = getattr(m, "supported_actions", None) or getattr(m, "supported_generation_methods", None) or []
            if "flash" in name.lower() and "audio" not in name.lower() and "image" not in name.lower():
                if not methods or any("generateContent" in str(x) for x in methods):
                    found.append(name)
        if not found:
            return fallback
        lite_models = sorted([x for x in found if "lite" in x.lower()], reverse=True)
        other_flash = sorted([x for x in found if "lite" not in x.lower()], reverse=True)
        return (lite_models + other_flash)[:6]
    except Exception:
        return fallback


@st.cache_data(show_spinner="기재요령 PDF를 분석하고 인덱싱하는 중입니다...")
def load_pdf_pages(pdf_path: str, cache_path: str):
    pdf_mtime = os.path.getmtime(pdf_path)
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cached = json.load(f)
            if cached.get("mtime") == pdf_mtime and cached.get("pages"):
                return cached["pages"]
        except Exception:
            pass

    reader = PdfReader(pdf_path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        pages.append({"pdf_page": i + 1, "text": text})

    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump({"mtime": pdf_mtime, "pages": pages}, f, ensure_ascii=False)
    except Exception:
        pass
    return pages


@st.cache_data(show_spinner=False)
def load_imho_text(imho_path: str) -> str:
    if not os.path.exists(imho_path):
        return ""
    reader = PdfReader(imho_path)
    blocks = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        blocks.append(f"--- [임호고 자료 {i + 1}쪽] ---\n{text}")
    return "\n\n".join(blocks)


def extract_expanded_keywords(query: str):
    clean_q = re.sub(r"[^\w\s가-힣·]", " ", query)
    raw_words = clean_q.split()

    base_keywords = []
    for w in raw_words:
        if w in STOPWORDS or len(w) < 2:
            continue
        for s in SUFFIXES:
            if w.endswith(s) and len(w) - len(s) >= 2:
                w = w[: -len(s)]
                break
        if w not in STOPWORDS and w not in base_keywords:
            base_keywords.append(w)

    expanded = list(base_keywords)
    for kw in base_keywords:
        for abbr, targets in SYNONYM_MAP.items():
            if abbr in kw or kw in abbr:
                for t in targets:
                    if t not in expanded:
                        expanded.append(t)

    return base_keywords, expanded


def retrieve_relevant_pages(pages, query: str, max_pages: int = 6):
    base_kws, expanded_kws = extract_expanded_keywords(query)
    if not expanded_kws:
        return []

    scored = []
    for p in pages:
        text = p["text"]
        base_unique = sum(1 for kw in base_kws if kw in text)
        exp_unique = sum(1 for kw in expanded_kws if kw in text)
        total_hits = sum(text.count(kw) for kw in expanded_kws)

        if exp_unique > 0:
            score = (base_unique * 150) + (exp_unique * 60) + min(total_hits, 20) * 3
            scored.append((score, p))

    scored.sort(key=lambda x: x[0], reverse=True)

    selected_map = {}
    for _, p in scored[:4]:
        p_num = p["pdf_page"]
        selected_map[p_num] = p
        if p_num + 1 <= len(pages) and len(selected_map) < max_pages:
            selected_map[p_num + 1] = pages[p_num]

    for common_p in (26, 27):
        if common_p <= len(pages) and common_p not in selected_map and len(selected_map) < max_pages + 2:
            selected_map[common_p] = pages[common_p - 1]

    return [selected_map[k] for k in sorted(selected_map.keys())]


def parse_ai_json(raw_text: str):
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        data = json.loads(cleaned)
        return (
            data.get("answer", raw_text),
            data.get("imho_note", "").strip(),
            data.get("source", ""),
            data.get("follow_up_questions", []),
        )
    except Exception:
        return raw_text, "", "", []


def ask_gemini(api_key: str, prompt: str, relevant_pages, imho_text: str, recent_messages, candidate_models):
    client = genai.Client(api_key=api_key)

    context_blocks = [
        f"=== [PDF {p['pdf_page']}쪽] ===\n{p['text']}" for p in relevant_pages
    ]
    context_text = "\n\n".join(context_blocks) if context_blocks else "관련 페이지 없음"

    history_lines = []
    for m in recent_messages[-4:]:
        role_label = "질문" if m["role"] == "user" else "답변"
        history_lines.append(f"{role_label}: {m['content']}")
    history_text = "\n".join(history_lines) if history_lines else "없음"

    full_prompt = f"""[교육부 기재요령 원문]
{context_text}

[임호고 자체 기준 및 연수자료]
{imho_text if imho_text else '없음'}

[이전 대화]
{history_text}

[현재 질문]
{prompt}
"""

    last_error = None
    for model_name in candidate_models:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.1,
                    response_mime_type="application/json",
                ),
            )
            answer, imho_note, source, follow_ups = parse_ai_json(response.text)
            return answer, imho_note, source, follow_ups, model_name
        except Exception as e:
            last_error = e
            continue

    raise last_error


# ==========================================
# 3. 사이드바 및 상단 헤더
# ==========================================
saved_key = get_saved_api_key()
imho_text = load_imho_text(IMHO_PDF_PATH)

with st.sidebar:
    st.markdown("### ⚙️ 설정 및 상태")
    if saved_key:
        api_key = saved_key
        st.success("🔑 API 키 자동 연결됨")
    else:
        api_key = st.text_input("Gemini API Key 입력", type="password", placeholder="AIza...")
        st.caption("💡 폴더에 `api_key.txt`를 만들거나 Streamlit Secrets에 등록하면 자동 연결됩니다.")

    st.markdown("---")
    if os.path.exists(PDF_PATH):
        st.info(f"📄 기본 문서\n\n`{PDF_PATH}`")
    else:
        st.error(f"❌ `{PDF_PATH}` 파일이 없습니다.")

    if imho_text:
        st.success(f"🏫 본교 기준 반영됨\n\n`{IMHO_PDF_PATH}`")
    else:
        st.caption(f"ℹ️ `{IMHO_PDF_PATH}` 파일이 있으면 임호고 자체 기준이 함께 반영됩니다.")

    if st.button("🗑️ 대화 내용 초기화", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_question = None
        st.rerun()

    st.markdown("---")
    st.caption("⚠️ 학생 실명·주민번호 등 개인정보는 입력하지 마세요.")

st.markdown(
    """
    <div class="hero-header">
        <div class="hero-badge">2026학년도 공식 기준 · 임호고 반영</div>
        <h1 class="hero-title">📘 고등학교 학교생활기록부 기재요령 Q&A</h1>
        <p class="hero-subtitle">교육부 공식 기재요령(2026년) 원문을 근거로 답변합니다. 임호고등학교 학교장 결정 및 자체 안내 기준도 함께 반영해 안내해 드립니다.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if not os.path.exists(PDF_PATH):
    st.error(f"폴더에 `{PDF_PATH}` 파일이 있는지 확인해 주세요.")
    st.stop()

pages = load_pdf_pages(PDF_PATH, CACHE_PATH)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

# ==========================================
# 4. 첫 화면 자주 묻는 질문
# ==========================================
if not st.session_state.messages:
    st.markdown("##### 💡 자주 묻는 질문")
    faq_list = [
        "출결 특기사항은 어떤 경우에 써야 돼?",
        "횟수가 많은 질병결석인데 사유가 정신과 진료인 경우는?",
        "대회 참가 내용을 세부능력 및 특기사항에 써도 돼?",
        "창의적 체험활동 및 행특 누가기록은 어떻게 해?",
        "1·2학년과 3학년의 창의적 체험활동 차이가 뭐야?",
        "1학기 생기부 작성 마감과 점검 일정이 어떻게 돼?",
    ]
    cols = st.columns(2)
    for i, faq in enumerate(faq_list):
        if cols[i % 2].button(f"💬  {faq}", use_container_width=True):
            st.session_state.pending_question = faq
            st.rerun()

# ==========================================
# 5. 대화 기록 출력
# ==========================================
for idx, msg in enumerate(st.session_state.messages):
    avatar = "👤" if msg["role"] == "user" else "📘"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"], unsafe_allow_html=True)

        if msg.get("imho_note"):
            imho_html = msg["imho_note"].replace("\n", "<br>")
            st.markdown(
                f"""
                <div class="imho-box">
                    <div class="imho-box-title">🏫 임호고 자체 기준 (학교장 결정·본교 안내)</div>
                    <div>{imho_html}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if msg.get("source"):
            st.markdown(
                f'<div class="source-badge">📌 근거: {msg["source"]}</div>',
                unsafe_allow_html=True,
            )

        if msg.get("ref_pages"):
            page_nums = ", ".join([f"{p['pdf_page']}쪽" for p in msg["ref_pages"]])
            with st.expander(f"📖 참고한 기재요령 PDF 원문 확인하기 ({page_nums})"):
                for p in msg["ref_pages"]:
                    st.markdown(f"**[PDF {p['pdf_page']}쪽]**")
                    st.text(p["text"])
                    st.markdown("---")

        if msg["role"] == "assistant" and idx == len(st.session_state.messages) - 1:
            follow_ups = msg.get("follow_up_questions", [])
            if follow_ups:
                st.markdown("")
                st.markdown("**💡 이어서 물어볼 만한 질문**")
                for q_idx, fq in enumerate(follow_ups):
                    if st.button(f"👉  {fq}", key=f"fq_{idx}_{q_idx}"):
                        st.session_state.pending_question = fq
                        st.rerun()

# ==========================================
# 6. 질문 입력 및 답변 생성
# ==========================================
user_input = st.chat_input("생기부 기재요령에 대해 궁금한 점을 물어보세요.")
prompt = st.session_state.pending_question or user_input

if prompt:
    st.session_state.pending_question = None

    if not api_key:
        st.warning("왼쪽 사이드바에 Gemini API Key를 먼저 입력해 주세요.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="📘"):
        with st.spinner("기재요령과 임호고 자체 기준을 확인하고 있습니다..."):
            relevant_pages = retrieve_relevant_pages(pages, prompt, max_pages=6)
            if not relevant_pages and not imho_text:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "질문에서 기재요령과 일치하는 핵심 단어를 찾지 못했습니다. 항목명(예: 출결, 세특, 수상, 봉사 등)을 포함해 다시 질문해 주세요.",
                    "imho_note": "",
                    "source": "",
                    "follow_up_questions": [],
                    "ref_pages": [],
                })
                st.rerun()

            try:
                candidate_models = get_candidate_models(api_key)
                answer, imho_note, source, follow_ups, used_model = ask_gemini(
                    api_key=api_key,
                    prompt=prompt,
                    relevant_pages=relevant_pages,
                    imho_text=imho_text,
                    recent_messages=st.session_state.messages[:-1],
                    candidate_models=candidate_models,
                )
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "imho_note": imho_note,
                    "source": source,
                    "follow_up_questions": follow_ups,
                    "ref_pages": relevant_pages,
                    "used_model": used_model,
                })
                st.rerun()
            except Exception as e:
                st.warning(f"현재 구글 무료 AI 서버가 일시적으로 혼잡해 요약 답변을 생성하지 못했습니다. 아래 관련 원문을 먼저 확인하시거나 잠시 후 다시 시도해 주세요.\n\n*(상세 오류: {e})*")
                if relevant_pages:
                    page_nums = ", ".join([f"{p['pdf_page']}쪽" for p in relevant_pages])
                    with st.expander(f"📖 관련 PDF 원문 바로 보기 ({page_nums})", expanded=True):
                        for p in relevant_pages:
                            st.markdown(f"**[PDF {p['pdf_page']}쪽]**")
                            st.text(p["text"])
                            st.markdown("---")
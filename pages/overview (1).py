import streamlit as st

# ── 페이지 설정 ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="맞춤형 AI 영어 학습 — 앱 소개",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── 커스텀 CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;600;700&family=Playfair+Display:wght@700&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
    background-color: #f0f4ff;
    color: #1e293b;
}
[data-testid="stAppViewContainer"] { background: #f0f4ff; }
[data-testid="stHeader"]           { background: transparent; }
section[data-testid="stSidebar"]   { display: none !important; }
button[data-testid="collapsedControl"] { display: none !important; }
.main .block-container { padding-left: 2rem !important; max-width: 100% !important; }

/* ── 히어로 ── */
.hero {
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 45%, #4338ca 100%);
    border-radius: 20px;
    padding: 64px 56px 56px;
    margin-bottom: 40px;
    position: relative;
    overflow: hidden;
}
.hero::after {
    content: "🎧";
    position: absolute;
    right: 52px; top: 40px;
    font-size: 120px;
    opacity: 0.08;
}
.hero-eyebrow {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: #a5b4fc;
    margin-bottom: 14px;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 52px;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.15;
    margin-bottom: 10px;
}
.hero-sub {
    font-size: 18px;
    color: #c7d2fe;
    margin-bottom: 24px;
    line-height: 1.7;
    max-width: 580px;
}
.pill {
    display: inline-block;
    border-radius: 20px;
    padding: 6px 18px;
    font-size: 12px;
    font-weight: 700;
    margin-right: 8px;
    margin-bottom: 8px;
}
.pill-blue   { background: #4f6ef7; color: #fff; }
.pill-purple { background: #7c4fff; color: #fff; }
.pill-green  { background: #059669; color: #fff; }
.pill-red    { background: #e94560; color: #fff; }

/* ── 통계 스트립 ── */
.stats-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 40px;
}
.stat-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 28px 20px;
    text-align: center;
    border: 1px solid #e0e7ff;
    box-shadow: 0 2px 12px rgba(79,110,247,0.07);
}
.stat-icon { font-size: 30px; margin-bottom: 8px; }
.stat-num  {
    font-family: 'Playfair Display', serif;
    font-size: 36px;
    font-weight: 700;
    color: #4f6ef7;
    line-height: 1;
    margin-bottom: 6px;
}
.stat-label { font-size: 13px; color: #64748b; }

/* ── 섹션 레이블 ── */
.sec-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: #4f6ef7;
    margin-bottom: 8px;
}
.sec-title {
    font-family: 'Playfair Display', serif;
    font-size: 32px;
    font-weight: 700;
    color: #1e1b4b;
    margin-bottom: 28px;
    line-height: 1.2;
}

/* ── 기능 카드 ── */
.feat-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
    margin-bottom: 48px;
}
.feat-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 28px 24px;
    border: 1px solid #e0e7ff;
    border-top: 4px solid #4f6ef7;
    transition: transform .18s, box-shadow .18s;
}
.feat-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 16px 40px rgba(79,110,247,0.13);
}
.feat-icon { font-size: 32px; margin-bottom: 12px; }
.feat-name { font-size: 17px; font-weight: 700; color: #1e1b4b; margin-bottom: 8px; }
.feat-desc { font-size: 13.5px; color: #475569; line-height: 1.75; }

/* ── 플로우 카드 ── */
.flow-row {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    margin-bottom: 48px;
    align-items: center;
}
.flow-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 22px 14px;
    text-align: center;
    border: 1px solid #e0e7ff;
    position: relative;
}
.flow-step {
    position: absolute;
    top: -10px; left: 50%;
    transform: translateX(-50%);
    background: #4f6ef7;
    color: #fff;
    border-radius: 50%;
    width: 22px; height: 22px;
    font-size: 11px; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
}
.flow-icon  { font-size: 28px; margin: 8px 0 8px; }
.flow-name  { font-size: 13px; font-weight: 700; color: #1e1b4b; margin-bottom: 5px; }
.flow-desc  { font-size: 11.5px; color: #64748b; line-height: 1.55; }

/* ── 탭 미리보기 박스 ── */
.tab-preview {
    background: #ffffff;
    border-radius: 16px;
    border: 1px solid #e0e7ff;
    padding: 24px 28px;
    margin-bottom: 14px;
}
.tab-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 14px;
}
.tab-badge {
    display: inline-block;
    background: linear-gradient(135deg, #4f6ef7, #7c4fff);
    color: white;
    border-radius: 8px;
    padding: 4px 12px;
    font-size: 13px;
    font-weight: 700;
}
.feature-list {
    list-style: none;
    padding: 0; margin: 10px 0 0;
}
.feature-list li {
    padding: 5px 0;
    font-size: 13px;
    color: #334155;
    display: flex;
    gap: 8px;
    align-items: flex-start;
    border-bottom: 1px solid #f1f5f9;
}
.feature-list li:last-child { border-bottom: none; }

/* ── 하이라이트 박스 ── */
.hl-box {
    background: linear-gradient(135deg, #1e1b4b, #312e81);
    border-radius: 16px;
    padding: 32px;
    color: #c7d2fe;
}
.hl-box ul {
    list-style: none;
    padding: 0; margin: 0;
}
.hl-box li {
    padding: 10px 0;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    font-size: 14px;
    display: flex;
    gap: 10px;
}
.hl-box li:last-child { border-bottom: none; }
.hl-check { color: #818cf8; font-weight: 700; flex-shrink: 0; }

/* ── CTA ── */
.cta-box {
    background: linear-gradient(135deg, #4f6ef7, #7c4fff);
    border-radius: 20px;
    padding: 52px 40px;
    text-align: center;
    margin-top: 48px;
}
.cta-title {
    font-family: 'Playfair Display', serif;
    font-size: 36px;
    font-weight: 700;
    color: #fff;
    margin-bottom: 14px;
}
.cta-desc {
    font-size: 15px;
    color: rgba(255,255,255,0.85);
    line-height: 1.8;
    margin-bottom: 28px;
}
.cta-btn {
    display: inline-block;
    background: #fff;
    color: #4f6ef7;
    font-weight: 700;
    font-size: 14px;
    letter-spacing: 1px;
    padding: 14px 36px;
    border-radius: 50px;
}
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# 1. HERO
# ════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Spring 2026 · Miniproject</div>
    <div class="hero-title">맞춤형 AI 영어 학습</div>
    <div class="hero-sub">
        수능 영어 지문을 원어민 음성으로 듣고, AI가 만든 퀴즈로 풀고,<br>
        AI 튜터에게 바로 물어보세요. 단어장까지 한 번에.
    </div>
    <span class="pill pill-blue">🎧 TTS 음성 듣기</span>
    <span class="pill pill-purple">🤖 AI 퀴즈</span>
    <span class="pill pill-green">📖 실시간 단어 사전</span>
    <span class="pill pill-red">🎬 유튜브 추천</span>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# 2. STATS
# ════════════════════════════════════════════════════════════
st.markdown("""
<div class="stats-row">
    <div class="stat-card">
        <div class="stat-icon">📄</div>
        <div class="stat-num">다양한</div>
        <div class="stat-label">소재별 수능 지문 제공</div>
    </div>
    <div class="stat-card">
        <div class="stat-icon">🤖</div>
        <div class="stat-num">3종</div>
        <div class="stat-label">AI 퀴즈 유형<br>(단어·독해·문법)</div>
    </div>
    <div class="stat-card">
        <div class="stat-icon">🎧</div>
        <div class="stat-num">5단계</div>
        <div class="stat-label">TTS 재생 속도 조절</div>
    </div>
    <div class="stat-card">
        <div class="stat-icon">💬</div>
        <div class="stat-num">AI</div>
        <div class="stat-label">1:1 튜터 실시간 답변</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# 3. CORE FEATURES
# ════════════════════════════════════════════════════════════
st.markdown('<div class="sec-label">핵심 기능</div>', unsafe_allow_html=True)
st.markdown('<div class="sec-title">앱이 제공하는 6가지 학습 도구</div>', unsafe_allow_html=True)

st.markdown("""
<div class="feat-grid">
    <div class="feat-card">
        <div class="feat-icon">🎧</div>
        <div class="feat-name">TTS 원어민 읽기</div>
        <div class="feat-desc">
            지문을 문장 단위로 나눠 원어민 음성으로 재생합니다.
            재생 속도(0.7×~1.5×) 조절, 문장 클릭으로 원하는 위치부터 재생,
            현재 읽는 문장 하이라이트 기능을 제공합니다.
        </div>
    </div>
    <div class="feat-card">
        <div class="feat-icon">📖</div>
        <div class="feat-name">실시간 단어 사전</div>
        <div class="feat-desc">
            지문 내 단어를 클릭하면 영영사전(Dictionary API)에서
            발음기호·품사·정의·예문을 즉시 표시합니다.
            🔊 버튼으로 원어민 발음도 바로 들을 수 있습니다.
        </div>
    </div>
    <div class="feat-card">
        <div class="feat-icon">📚</div>
        <div class="feat-name">나만의 단어장</div>
        <div class="feat-desc">
            사전에서 확인한 단어를 한 번의 클릭으로 단어장에 저장합니다.
            단어·발음기호·품사·정의를 한눈에 확인하고
            언제든지 삭제·관리할 수 있습니다.
        </div>
    </div>
    <div class="feat-card">
        <div class="feat-icon">🤖</div>
        <div class="feat-name">AI 퀴즈 생성</div>
        <div class="feat-desc">
            Gemini AI가 지문을 분석해 수능형 문제를 자동 생성합니다.
            단어 퀴즈(5지선다 3문제), 독해 문제(주제·요지 파악),
            문법 문제(어법 판단) 세 가지 유형을 제공합니다.
        </div>
    </div>
    <div class="feat-card">
        <div class="feat-icon">💬</div>
        <div class="feat-name">AI 튜터 채팅</div>
        <div class="feat-desc">
            지문·어휘·문법·해석 등 궁금한 것을 한국어로 바로 질문하세요.
            Gemini AI가 지문 문맥을 이해하고 3~5문장으로 명확히 답변합니다.
            대화 히스토리를 유지해 연속 질문도 가능합니다.
        </div>
    </div>
    <div class="feat-card">
        <div class="feat-icon">🎬</div>
        <div class="feat-name">유튜브 영상 추천</div>
        <div class="feat-desc">
            AI가 지문 주제를 분석해 배경지식·어휘학습·독해전략·수능영어
            4가지 유형의 관련 유튜브 영상을 추천합니다.
            한국어/영어 영상을 골고루 추천합니다.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# 4. 학습 플로우
# ════════════════════════════════════════════════════════════
st.markdown('<div class="sec-label">학습 흐름</div>', unsafe_allow_html=True)
st.markdown('<div class="sec-title">이렇게 사용해요</div>', unsafe_allow_html=True)

st.markdown("""
<div class="flow-row">
    <div class="flow-card">
        <div class="flow-step">1</div>
        <div class="flow-icon">🗂️</div>
        <div class="flow-name">소재 선택</div>
        <div class="flow-desc">카테고리별 수능 지문 목록에서 학습할 지문을 선택</div>
    </div>
    <div class="flow-card">
        <div class="flow-step">2</div>
        <div class="flow-icon">🎧</div>
        <div class="flow-name">TTS 듣기</div>
        <div class="flow-desc">원어민 음성으로 듣고, 단어 클릭해 사전 확인 & 단어장 저장</div>
    </div>
    <div class="flow-card">
        <div class="flow-step">3</div>
        <div class="flow-icon">🤖</div>
        <div class="flow-name">AI 퀴즈</div>
        <div class="flow-desc">단어·독해·문법 3종 퀴즈를 AI가 즉석 생성, 바로 풀기</div>
    </div>
    <div class="flow-card">
        <div class="flow-step">4</div>
        <div class="flow-icon">📊</div>
        <div class="flow-name">AI 피드백</div>
        <div class="flow-desc">채점 후 AI가 점수 평가 + 오답 해설 + 학습 조언 제공</div>
    </div>
    <div class="flow-card">
        <div class="flow-step">5</div>
        <div class="flow-icon">🎬</div>
        <div class="flow-name">심화 학습</div>
        <div class="flow-desc">AI 튜터 질문 & 유튜브 추천 영상으로 배경지식 확장</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# 5. 탭별 기능 상세 + 기술 스택
# ════════════════════════════════════════════════════════════
col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    st.markdown('<div class="sec-label">화면 구성</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">5개 탭으로 구성된<br>학습 공간</div>', unsafe_allow_html=True)

    tabs_info = [
        ("🎧", "듣기 (TTS)",
         ["문장 단위 분리 & 순차 재생",
          "재생·일시정지·정지·이전/다음 문장 버튼",
          "재생 속도 5단계 조절 (0.7× ~ 1.5×)",
          "문장 클릭 → 해당 위치부터 재생",
          "단어 클릭 → 발음·품사·정의 즉시 표시",
          "단어장 추가 버튼 (중복 방지 자동 처리)"]),
        ("🎬", "유튜브 추천",
         ["AI가 지문 주제 자동 분석",
          "배경지식·어휘·독해전략·수능영어 4유형 추천",
          "한국어/영어 영상 구분 표시",
          "YouTube 직접 검색 링크 제공"]),
        ("🔤", "단어 퀴즈",
         ["AI가 어휘 목록 기반 5지선다 3문제 생성",
          "정답 제출 후 O/X 즉시 표시 및 해설",
          "점수 배지 + AI 맞춤 피드백",
          "AI 튜터 연동 (지문·어휘 질문 가능)"]),
        ("📝", "독해 문제",
         ["수능형 주제 파악·요지 파악 문제 2개",
          "AI 해설 + 점수 평가",
          "AI 튜터로 지문 해석 질문 가능",
          "다시 풀기 / 새 문제 생성 선택 가능"]),
        ("🔍", "문법 문제",
         ["지문 기반 어법 판단 문제 2개",
          "밑줄 친 부분 어법상 틀린 것 찾기",
          "문법 포인트 포함 한국어 해설",
          "AI 튜터로 문법 개념 추가 질문 가능"]),
    ]

    for icon, name, points in tabs_info:
        st.markdown(f"""
        <div class="tab-preview">
            <div class="tab-header">
                <span class="tab-badge">{icon} {name}</span>
            </div>
            <ul class="feature-list">
                {''.join(f'<li><span>✦</span><span>{pt}</span></li>' for pt in points)}
            </ul>
        </div>
        """, unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="sec-label">기술 스택 & 특징</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">어떻게<br>만들었나요?</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="hl-box">
        <ul>
            <li><span class="hl-check">🧠</span><span>Gemini 2.5 Flash — 퀴즈 생성 · AI 튜터 · 유튜브 추천</span></li>
            <li><span class="hl-check">🌐</span><span>Web Speech API (브라우저 내장 TTS) — 별도 API 키 불필요</span></li>
            <li><span class="hl-check">📖</span><span>Dictionary API — 무료 영영사전 단어 조회</span></li>
            <li><span class="hl-check">📂</span><span>CSV 기반 지문 데이터 — 카테고리별 관리 용이</span></li>
            <li><span class="hl-check">🐍</span><span>Streamlit + Python — 빠른 프로토타이핑 및 배포</span></li>
            <li><span class="hl-check">💾</span><span>localStorage — 단어장 데이터 브라우저 로컬 저장</span></li>
            <li><span class="hl-check">📱</span><span>반응형 레이아웃 — 모바일/PC 모두 대응</span></li>
            <li><span class="hl-check">🔒</span><span>Streamlit Secrets — API 키 안전 관리</span></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="sec-label">AI 퀴즈 생성 방식</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="tab-preview">
        <ul class="feature-list">
            <li><span>1️⃣</span><span>지문·어휘·문법 데이터를 프롬프트에 포함</span></li>
            <li><span>2️⃣</span><span>Gemini가 수능 유형에 맞는 문제를 JSON으로 출력</span></li>
            <li><span>3️⃣</span><span>JSON 파싱 후 Streamlit UI로 즉시 렌더링</span></li>
            <li><span>4️⃣</span><span>제출 후 정오답 판별 & AI 피드백 문장 생성</span></li>
            <li><span>5️⃣</span><span>'새 문제' 클릭 시 같은 지문으로 새 문제 재생성</span></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# 6. 인터랙티브 데모
# ════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown('<div class="sec-label">앱 미리보기</div>', unsafe_allow_html=True)
st.markdown('<div class="sec-title">학습 화면을 체험해보세요</div>', unsafe_allow_html=True)

demo_tab1, demo_tab2, demo_tab3 = st.tabs(["🔤 단어 퀴즈 체험", "📊 학습 진행 현황", "🗂️ 지문 목록 예시"])

with demo_tab1:
    st.subheader("단어 퀴즈 샘플")
    st.caption("실제 앱에서는 AI가 지문 어휘를 분석해 문제를 자동 생성합니다.")

    sample_q = {
        "다음 단어의 뜻으로 가장 적절한 것은?\n🔤 **prevalent**": {
            "options": ["① 드문, 희귀한", "② 널리 퍼진, 만연한", "③ 새롭게 등장한", "④ 억압적인", "⑤ 기술적인"],
            "answer": "② 널리 퍼진, 만연한",
            "explanation": "prevalent는 '널리 퍼진, 만연한'을 의미하는 형용사입니다. (예: a prevalent belief — 널리 퍼진 믿음)"
        },
        "다음 단어의 뜻으로 가장 적절한 것은?\n🔤 **deduce**": {
            "options": ["① 추론하다", "② 파괴하다", "③ 수집하다", "④ 거부하다", "⑤ 증가시키다"],
            "answer": "① 추론하다",
            "explanation": "deduce는 '추론하다, 연역하다'를 의미합니다. (예: deduce the answer from evidence)"
        },
        "다음 단어의 뜻으로 가장 적절한 것은?\n🔤 **alleviate**": {
            "options": ["① 악화시키다", "② 무시하다", "③ 완화하다, 경감하다", "④ 강조하다", "⑤ 발생시키다"],
            "answer": "③ 완화하다, 경감하다",
            "explanation": "alleviate는 '(고통·문제를) 완화하다, 경감하다'를 의미합니다. (예: alleviate stress)"
        },
    }

    q_text = st.selectbox("문제 선택", list(sample_q.keys()), label_visibility="visible")
    q_data = sample_q[q_text]
    st.markdown(q_text)
    answer = st.radio("정답을 고르세요:", q_data["options"], horizontal=False, index=None)

    if st.button("✅ 정답 확인", type="primary"):
        if answer is None:
            st.warning("보기를 먼저 선택하세요.")
        elif answer == q_data["answer"]:
            st.success(f"🎉 정답입니다!\n\n📖 해설: {q_data['explanation']}")
            st.balloons()
        else:
            st.error(f"❌ 오답입니다.\n\n✅ 정답: {q_data['answer']}\n\n📖 해설: {q_data['explanation']}")

with demo_tab2:
    import datetime, random
    import pandas as pd

    st.subheader("학습 진행 현황 (샘플 데이터)")
    st.caption("실제 앱에서는 학습 이력이 누적됩니다.")

    dates = [datetime.date.today() - datetime.timedelta(days=i) for i in range(13, -1, -1)]
    vocab_scores = [random.randint(60, 100) for _ in dates]
    comp_scores  = [random.randint(55, 95)  for _ in dates]
    gram_scores  = [random.randint(50, 90)  for _ in dates]

    df = pd.DataFrame({
        "날짜": dates,
        "단어 퀴즈": vocab_scores,
        "독해 문제": comp_scores,
        "문법 문제": gram_scores,
    }).set_index("날짜")

    st.line_chart(df, height=240)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("학습 지문 수",     "14편",   "+3편")
    c2.metric("단어장 저장",     "42단어", "+8단어")
    c3.metric("평균 퀴즈 점수", f"{sum(vocab_scores)//len(vocab_scores)}점", "+4점")
    c4.metric("AI 튜터 질문",    "23회",   "+5회")

with demo_tab3:
    import pandas as pd

    st.subheader("지문 목록 예시")
    st.caption("CSV 파일의 카테고리명이 소재 필터로 자동 등록됩니다.")

    sample_passages = [
        {"소재": "환경", "지문 #": 1, "미리보기": "Climate change poses unprecedented challenges to ecosystems worldwide..."},
        {"소재": "환경", "지문 #": 2, "미리보기": "The rapid decline of biodiversity is linked to human activities such as..."},
        {"소재": "심리", "지문 #": 3, "미리보기": "Cognitive biases influence how individuals perceive and interpret information..."},
        {"소재": "과학", "지문 #": 4, "미리보기": "Recent advances in quantum computing have opened new possibilities for..."},
        {"소재": "사회", "지문 #": 5, "미리보기": "Social media platforms have fundamentally altered the way people communicate..."},
    ]
    st.dataframe(pd.DataFrame(sample_passages), use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════════
# 7. CTA
# ════════════════════════════════════════════════════════════
st.markdown("""
<div class="cta-box">
    <div class="cta-title">지금 바로 학습을 시작해보세요</div>
    <div class="cta-desc">
        소재별 지문 선택 → TTS 듣기 → AI 퀴즈 → AI 튜터 질문까지<br>
        영어 학습의 모든 과정을 한 앱에서 경험하세요.
    </div>
    <span class="cta-btn">🎧 앱 실행하기</span>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.caption("맞춤형 AI 영어 학습 · Spring 2026 Miniproject · Powered by Gemini 2.5 Flash & Streamlit")

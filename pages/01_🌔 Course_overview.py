import streamlit as st

# ── 페이지 설정 ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EduLingo – English Learning App",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── 커스텀 CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,400&family=DM+Sans:wght@300;400;500&display=swap');

/* ── 전역 리셋 ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #F5F0E8;
    color: #1a1a2e;
}
[data-testid="stAppViewContainer"] {
    background: #F5F0E8;
}
[data-testid="stHeader"] { background: transparent; }

/* ── 히어로 배너 ── */
.hero {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border-radius: 24px;
    padding: 72px 56px;
    margin-bottom: 48px;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: "A B C";
    position: absolute;
    right: 48px; top: 36px;
    font-family: 'Playfair Display', serif;
    font-size: 96px;
    color: rgba(255,255,255,0.05);
    letter-spacing: 24px;
}
.hero-eyebrow {
    font-size: 12px;
    font-weight: 500;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: #e94560;
    margin-bottom: 16px;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 64px;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.1;
    margin-bottom: 8px;
}
.hero-subtitle {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: 28px;
    color: #a8b2d8;
    margin-bottom: 28px;
}
.hero-desc {
    font-size: 16px;
    color: #ccd6f6;
    max-width: 560px;
    line-height: 1.8;
}
.hero-badge {
    display: inline-block;
    background: #e94560;
    color: white;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 6px 16px;
    border-radius: 20px;
    margin-top: 28px;
}

/* ── 섹션 헤더 ── */
.section-label {
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: #e94560;
    margin-bottom: 8px;
}
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 36px;
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 40px;
    line-height: 1.2;
}

/* ── 기능 카드 ── */
.feature-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin-bottom: 48px;
}
.feature-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 32px 28px;
    border: 1px solid rgba(26,26,46,0.08);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.feature-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 48px rgba(26,26,46,0.12);
}
.feature-icon {
    font-size: 36px;
    margin-bottom: 16px;
}
.feature-name {
    font-family: 'Playfair Display', serif;
    font-size: 20px;
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 10px;
}
.feature-desc {
    font-size: 14px;
    color: #5a5a7a;
    line-height: 1.7;
}

/* ── 통계 스트립 ── */
.stats-strip {
    background: #1a1a2e;
    border-radius: 16px;
    padding: 40px 48px;
    display: flex;
    justify-content: space-around;
    margin-bottom: 48px;
}
.stat-item { text-align: center; }
.stat-number {
    font-family: 'Playfair Display', serif;
    font-size: 48px;
    font-weight: 700;
    color: #e94560;
}
.stat-label {
    font-size: 13px;
    color: #a8b2d8;
    letter-spacing: 1px;
}

/* ── 커리큘럼 테이블 ── */
.curriculum-row {
    display: flex;
    align-items: center;
    background: #ffffff;
    border-radius: 12px;
    padding: 20px 28px;
    margin-bottom: 10px;
    border-left: 4px solid #e94560;
    gap: 20px;
}
.curriculum-week {
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #e94560;
    min-width: 60px;
}
.curriculum-topic {
    font-family: 'Playfair Display', serif;
    font-size: 18px;
    font-weight: 700;
    color: #1a1a2e;
    flex: 1;
}
.curriculum-tag {
    display: inline-block;
    background: #F5F0E8;
    color: #5a5a7a;
    font-size: 11px;
    padding: 4px 12px;
    border-radius: 20px;
    letter-spacing: 1px;
}

/* ── CTA 섹션 ── */
.cta-box {
    background: linear-gradient(135deg, #e94560, #c0392b);
    border-radius: 20px;
    padding: 56px 48px;
    text-align: center;
    margin-top: 48px;
}
.cta-title {
    font-family: 'Playfair Display', serif;
    font-size: 40px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 16px;
}
.cta-desc {
    font-size: 16px;
    color: rgba(255,255,255,0.85);
    margin-bottom: 32px;
    line-height: 1.8;
}
.cta-btn {
    display: inline-block;
    background: #ffffff;
    color: #e94560;
    font-weight: 600;
    font-size: 14px;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 14px 36px;
    border-radius: 50px;
}

/* ── 퀘스트 박스 (주요 특징) ── */
.highlight-box {
    background: #0f3460;
    border-radius: 16px;
    padding: 36px;
    color: white;
}
.highlight-box ul {
    list-style: none;
    padding: 0;
    margin: 0;
}
.highlight-box li {
    padding: 10px 0;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    font-size: 15px;
    color: #ccd6f6;
    display: flex;
    align-items: center;
    gap: 12px;
}
.highlight-box li:last-child { border-bottom: none; }
.check { color: #e94560; font-weight: bold; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# 1. HERO SECTION
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Spring 2026 · Miniproject</div>
    <div class="hero-title">EduLingo</div>
    <div class="hero-subtitle">Your AI-powered English companion</div>
    <div class="hero-desc">
        단어 암기부터 실전 회화까지 — 인공지능이 개인 맞춤형 학습 경로를 설계합니다.
        언제, 어디서나 영어 실력을 키워보세요.
    </div>
    <div class="hero-badge">🎓 학습 시작하기</div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# 2. STATS STRIP
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="stats-strip">
    <div class="stat-item">
        <div class="stat-number">5,000+</div>
        <div class="stat-label">필수 영단어</div>
    </div>
    <div class="stat-item">
        <div class="stat-number">12</div>
        <div class="stat-label">학습 레벨</div>
    </div>
    <div class="stat-item">
        <div class="stat-number">AI</div>
        <div class="stat-label">맞춤형 피드백</div>
    </div>
    <div class="stat-item">
        <div class="stat-number">24/7</div>
        <div class="stat-label">학습 가능</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# 3. CORE FEATURES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-label">핵심 기능</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">무엇을 배울 수 있나요?</div>', unsafe_allow_html=True)

st.markdown("""
<div class="feature-grid">
    <div class="feature-card">
        <div class="feature-icon">🧠</div>
        <div class="feature-name">스마트 단어장</div>
        <div class="feature-desc">
            AI가 학습자의 수준과 망각 곡선을 분석해
            최적의 복습 타이밍에 단어를 다시 제시합니다.
        </div>
    </div>
    <div class="feature-card">
        <div class="feature-icon">🎤</div>
        <div class="feature-name">AI 회화 연습</div>
        <div class="feature-desc">
            실시간 음성 인식과 발음 교정으로
            원어민 수준의 Speaking 훈련을 제공합니다.
        </div>
    </div>
    <div class="feature-card">
        <div class="feature-icon">✍️</div>
        <div class="feature-name">Writing 코치</div>
        <div class="feature-desc">
            문장 구조, 문법, 어휘 선택까지
            AI가 상세한 피드백을 즉각 제공합니다.
        </div>
    </div>
    <div class="feature-card">
        <div class="feature-icon">📖</div>
        <div class="feature-name">맞춤형 독해</div>
        <div class="feature-desc">
            관심 분야 기사·에세이를 활용한
            실전 독해 훈련과 요약 연습을 지원합니다.
        </div>
    </div>
    <div class="feature-card">
        <div class="feature-icon">📊</div>
        <div class="feature-name">학습 대시보드</div>
        <div class="feature-desc">
            학습 시간, 정답률, 성장 곡선을
            시각적 데이터로 한눈에 확인하세요.
        </div>
    </div>
    <div class="feature-card">
        <div class="feature-icon">🏆</div>
        <div class="feature-name">레벨 & 뱃지</div>
        <div class="feature-desc">
            목표를 달성할 때마다 뱃지를 획득하고
            랭킹 시스템으로 동기를 유지하세요.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# 4. CURRICULUM + HIGHLIGHT  (2-column)
# ══════════════════════════════════════════════════════════════════════════════
col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    st.markdown('<div class="section-label">커리큘럼</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">12주 학습 로드맵</div>', unsafe_allow_html=True)

    curriculum = [
        ("W 01–02", "기초 발음 & 파닉스",      "Beginner"),
        ("W 03–04", "핵심 문법 패턴 1,000",     "Grammar"),
        ("W 05–06", "비즈니스 영어 어휘",        "Vocabulary"),
        ("W 07–08", "실전 이메일 & 라이팅",      "Writing"),
        ("W 09–10", "AI 회화 롤플레이",          "Speaking"),
        ("W 11–12", "종합 모의 시험 & 피드백",   "Assessment"),
    ]
    for week, topic, tag in curriculum:
        st.markdown(f"""
        <div class="curriculum-row">
            <span class="curriculum-week">{week}</span>
            <span class="curriculum-topic">{topic}</span>
            <span class="curriculum-tag">{tag}</span>
        </div>
        """, unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="section-label">왜 EduLingo인가?</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">차별화된<br>학습 경험</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="highlight-box">
        <ul>
            <li><span class="check">✦</span> 개인 맞춤형 AI 커리큘럼 자동 생성</li>
            <li><span class="check">✦</span> 실시간 발음 & 문법 교정 피드백</li>
            <li><span class="check">✦</span> 망각 곡선 기반 스마트 복습 시스템</li>
            <li><span class="check">✦</span> 직업·관심사별 특화 콘텐츠</li>
            <li><span class="check">✦</span> 오프라인 모드 지원 (모바일 앱)</li>
            <li><span class="check">✦</span> 교사 대시보드 & 학급 관리 기능</li>
            <li><span class="check">✦</span> CEFR A1 → C1 레벨 전 구간 커버</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# 5. INTERACTIVE DEMO  (Streamlit 위젯)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown('<div class="section-label">인터랙티브 데모</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">지금 바로 체험해보세요</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📝 단어 퀴즈", "🎯 레벨 진단", "📈 학습 현황"])

with tab1:
    st.subheader("오늘의 단어 퀴즈")
    quiz = {
        "Collaboration": ["협력", "경쟁", "분리", "분석"],
        "Iteration":     ["반복", "혁신", "정지", "전환"],
        "Deployment":    ["배포", "개발", "설계", "테스트"],
    }
    word = st.selectbox("단어를 선택하세요", list(quiz.keys()))
    answer = st.radio("올바른 뜻을 고르세요:", quiz[word], horizontal=True)
    if st.button("정답 확인", key="quiz_btn"):
        if answer == quiz[word][0]:
            st.success(f"🎉 정답입니다! **{word}** = {quiz[word][0]}")
            st.balloons()
        else:
            st.error(f"❌ 오답! 정답은 **{quiz[word][0]}** 입니다.")

with tab2:
    st.subheader("영어 레벨 진단")
    q1 = st.radio("1. 영어 학습 경력은?",
                  ["처음 시작 (0–1년)", "초급 (1–3년)", "중급 (3–5년)", "고급 (5년 이상)"])
    q2 = st.radio("2. 가장 약한 영역은?",
                  ["말하기 (Speaking)", "쓰기 (Writing)", "읽기 (Reading)", "듣기 (Listening)"])
    q3 = st.radio("3. 하루 학습 가능 시간은?",
                  ["15분 이하", "15–30분", "30–60분", "60분 이상"])
    if st.button("나의 추천 레벨 보기", key="level_btn"):
        level_map = {
            "처음 시작 (0–1년)": "A1 – Beginner",
            "초급 (1–3년)":      "A2–B1 – Elementary",
            "중급 (3–5년)":      "B1–B2 – Intermediate",
            "고급 (5년 이상)":   "C1 – Advanced",
        }
        recommended = level_map[q1]
        st.info(f"📚 추천 시작 레벨: **{recommended}**\n\n약점 영역 **{q2}** 강화 커리큘럼을 우선 배정합니다.")

with tab3:
    st.subheader("샘플 학습 현황 (데모)")
    import random, datetime
    import pandas as pd

    dates = [datetime.date.today() - datetime.timedelta(days=i) for i in range(13, -1, -1)]
    scores = [random.randint(60, 100) for _ in dates]
    df = pd.DataFrame({"날짜": dates, "학습 점수": scores})
    st.line_chart(df.set_index("날짜"), height=260)

    c1, c2, c3 = st.columns(3)
    c1.metric("총 학습일", "14일", "+3일")
    c2.metric("평균 점수", f"{sum(scores)//len(scores)}점", "+5점")
    c3.metric("획득 뱃지", "7개", "+2개")


# ══════════════════════════════════════════════════════════════════════════════
# 6. CTA
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="cta-box">
    <div class="cta-title">지금 무료로 시작하세요</div>
    <div class="cta-desc">
        AI가 설계한 나만의 영어 학습 경로 — 첫 12주 무료 체험.<br>
        별도 설치 없이 브라우저에서 바로 시작할 수 있습니다.
    </div>
    <span class="cta-btn">🚀 무료 체험 시작</span>
</div>
""", unsafe_allow_html=True)

# ── 푸터 ──────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.caption("EduLingo · Spring 2026 Miniproject · Built with Streamlit & AI")

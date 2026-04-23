import streamlit as st
import json
import os
import glob
import csv
import google.generativeai as genai
from google.generativeai.types import GenerationConfig


# ── AI 설정 ──────────────────────────────────────────────
genai.configure(api_key=st.secrets.get("GOOGLE_API_KEY", ""))
model = genai.GenerativeModel(
    model_name="gemini-2.0-pro",
    generation_config=GenerationConfig(
        max_output_tokens=800,
        temperature=0.7,
    )
)

# ── 페이지 설정 ──────────────────────────────────────────
st.set_page_config(
    page_title="수능특강 AI 학습",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
.passage-card {
    background: #f8f9ff;
    border-left: 4px solid #4f6ef7;
    border-radius: 8px;
    padding: 16px 20px;
    margin: 8px 0;
    line-height: 1.8;
    font-size: 0.97rem;
}
.score-badge {
    display: inline-block;
    background: linear-gradient(135deg, #4f6ef7, #7c4fff);
    color: white;
    border-radius: 20px;
    padding: 6px 18px;
    font-weight: 700;
    font-size: 1.1rem;
}
.correct-ans { color: #16a34a; font-weight: 600; }
.wrong-ans   { color: #dc2626; text-decoration: line-through; }
.feedback-box {
    background: linear-gradient(135deg, #eff6ff, #f0fdf4);
    border: 1px solid #bfdbfe;
    border-radius: 12px;
    padding: 20px;
    margin-top: 16px;
}
</style>
""", unsafe_allow_html=True)

# ── 1. 데이터 로드 ────────────────────────────────────────
@st.cache_data
def load_passages():
    passages = []
    pid = 1
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    csv_files = sorted(glob.glob(os.path.join(data_dir, "*.csv")))

    for file_path in csv_files:
        category = os.path.basename(file_path).replace(".csv", "")
        with open(file_path, "r", encoding="utf-8-sig") as f:
            sample = f.read(512)
        delimiter = "\t" if "\t" in sample else ","
        with open(file_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            for row in reader:
                if not row.get("지문", "").strip():
                    continue
                passages.append({
                    "id":         pid,
                    "category":   category,
                    "passage":    row.get("지문", "").strip(),
                    "vocabulary": row.get("어휘", "").strip(),
                    "question":   row.get("문제", "").strip(),
                    "grammar":    row.get("문법", "").strip(),
                })
                pid += 1
    return passages

# ── 2. 상태 초기화 ────────────────────────────────────────
def init_state():
    defaults = {
        'current_page': 'list',
        'selected_id': None,
        'completed': [],
        'selected_category': "전체",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ── 3. AI 퀴즈 생성 ───────────────────────────────────────
def generate_quiz(p, quiz_type):

    if quiz_type == "vocabulary":
        prompt = f"""다음 어휘 목록에서 3개를 골라 5지선다 단어 퀴즈 3문제를 만드세요.

어휘 목록:
{p['vocabulary'][:400]}

지시사항:
- 반드시 JSON만 출력하세요 (설명, 마크다운 없이)
- answer는 정답 보기 번호를 문자열로 ("1"~"5")

출력 형식:
{{
  "questions": [
    {{
      "id": 1,
      "word": "영어단어",
      "question": "다음 단어의 뜻으로 가장 적절한 것은?",
      "options": ["①가", "②나", "③다", "④라", "⑤마"],
      "answer": "2",
      "explanation": "이 단어는 ~라는 의미입니다."
    }}
  ]
}}"""

    elif quiz_type == "comprehension":
        prompt = f"""다음 영어 지문으로 수능형 독해 문제 2개를 만드세요.

지문:
{p['passage'][:500]}

지시사항:
- 반드시 JSON만 출력하세요 (설명, 마크다운 없이)
- 주제 파악 1문제, 요지 파악 1문제
- answer는 정답 보기 번호를 문자열로 ("1"~"5")
- options의 보기는 한국어로 작성

출력 형식:
{{
  "questions": [
    {{
      "id": 1,
      "type": "주제 파악",
      "question": "이 글의 주제로 가장 적절한 것은?",
      "options": ["①보기1", "②보기2", "③보기3", "④보기4", "⑤보기5"],
      "answer": "3",
      "explanation": "한국어 해설"
    }}
  ]
}}"""

    elif quiz_type == "grammar":
        prompt = f"""다음 영어 지문으로 수능형 문법 문제 2개를 만드세요.

지문:
{p['passage'][:500]}

문법 포인트:
{p['grammar'][:300]}

지시사항:
- 반드시 JSON만 출력하세요 (설명, 마크다운 없이)
- 어법상 올바른/틀린 것 고르기 유형
- answer는 정답 보기 번호를 문자열로 ("1"~"5")

출력 형식:
{{
  "questions": [
    {{
      "id": 1,
      "type": "어법 판단",
      "sentence": "지문에서 발췌한 문장 (밑줄 표시는 **단어** 형식)",
      "question": "밑줄 친 부분 중 어법상 틀린 것은?",
      "options": ["①보기1", "②보기2", "③보기3", "④보기4", "⑤보기5"],
      "answer": "2",
      "explanation": "한국어로 문법 설명 포함 해설"
    }}
  ]
}}"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        # JSON 블록 추출
        if "```" in text:
            text = text.split("```")[-2] if "```" in text else text
            text = text.replace("json", "", 1).strip()
        text = text.strip()
        # 중괄호 시작 위치부터 파싱
        start = text.find("{")
        end   = text.rfind("}") + 1
        if start == -1 or end == 0:
            raise ValueError(f"JSON을 찾을 수 없습니다.\n응답 내용: {text[:200]}")
        return json.loads(text[start:end])
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 파싱 실패: {e}\n응답 내용: {text[:300]}")

# ── 4. AI 피드백 ──────────────────────────────────────────
def get_feedback(questions, user_answers, quiz_label):
    results = []
    for q in questions:
        ua = user_answers.get(str(q['id']), "미응답")
        correct = ua == q['answer']
        results.append(
            f"문제{q['id']}: {'정답' if correct else '오답'} "
            f"(선택:{ua}, 정답:{q['answer']})\n해설: {q['explanation']}"
        )

    prompt = f"""학생이 '{quiz_label}' 퀴즈를 풀었습니다.

결과:
{chr(10).join(results)}

한국어로 3~4문장 피드백을 작성해주세요:
1. 점수 평가와 격려
2. 틀린 문제 핵심 포인트
3. 학습 조언"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"피드백 생성 중 오류가 발생했습니다: {e}"

# ── 5. 퀴즈 탭 렌더링 ─────────────────────────────────────
def render_quiz_tab(p, quiz_type, label):
    qkey = f"quiz_{p['id']}_{quiz_type}"
    akey = f"ans_{p['id']}_{quiz_type}"
    skey = f"sub_{p['id']}_{quiz_type}"
    fkey = f"fb_{p['id']}_{quiz_type}"

    for k, d in [(qkey, None), (akey, {}), (skey, False), (fkey, None)]:
        if k not in st.session_state:
            st.session_state[k] = d

    # ── 문제 생성 전 ──
    if st.session_state[qkey] is None:
        st.markdown("&nbsp;")
        if st.button(f"🤖 AI로 {label} 생성하기", key=f"gen_{p['id']}_{quiz_type}",
                     type="primary", use_container_width=True):
            with st.spinner("AI가 문제를 만들고 있습니다... (5~10초)"):
                try:
                    result = generate_quiz(p, quiz_type)
                    if not result.get("questions"):
                        st.error("문제가 생성되지 않았습니다. 다시 시도해주세요.")
                        return
                    st.session_state[qkey] = result
                    st.session_state[akey] = {}
                    st.session_state[skey] = False
                    st.session_state[fkey] = None
                    st.rerun()
                except Exception as e:
                    st.error(f"문제 생성 오류: {e}")
        return

    questions = st.session_state[qkey].get("questions", [])
    submitted = st.session_state[skey]
    answers   = st.session_state[akey]

    # ── 문제 출력 ──
    for q in questions:
        qid = str(q['id'])
        st.markdown(f"**Q{q['id']}. {q['question']}**")
        if q.get("word"):
            st.markdown(
                f"<span style='font-size:1.05rem;color:#4f6ef7;font-weight:700'>"
                f"🔤 {q['word']}</span>", unsafe_allow_html=True
            )
        if q.get("sentence"):
            st.markdown(f"> {q['sentence']}")

        if not submitted:
            sel = st.radio("", q['options'],
                           key=f"r_{p['id']}_{quiz_type}_{qid}",
                           index=None, label_visibility="collapsed")
            if sel is not None:
                answers[qid] = str(q['options'].index(sel) + 1)
        else:
            correct_idx = int(q['answer']) - 1
            user_idx    = int(answers.get(qid, 0)) - 1
            for i, opt in enumerate(q['options']):
                if i == correct_idx:
                    st.markdown(f"<span class='correct-ans'>✅ {opt}</span>",
                                unsafe_allow_html=True)
                elif i == user_idx:
                    st.markdown(f"<span class='wrong-ans'>❌ {opt}</span>",
                                unsafe_allow_html=True)
                else:
                    st.markdown(f"&nbsp;&nbsp;&nbsp;{opt}")
            with st.expander("📖 해설"):
                st.write(q['explanation'])

        st.markdown("---")

    # ── 하단 버튼 ──
    if not submitted:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ 제출", key=f"sub_{p['id']}_{quiz_type}_btn",
                         type="primary", use_container_width=True):
                st.session_state[skey] = True
                with st.spinner("피드백 생성 중..."):
                    st.session_state[fkey] = get_feedback(questions, answers, label)
                st.rerun()
        with c2:
            if st.button("🔄 새 문제", key=f"new_{p['id']}_{quiz_type}",
                         use_container_width=True):
                st.session_state[qkey] = None
                st.rerun()
    else:
        score = sum(1 for q in questions if answers.get(str(q['id'])) == q['answer'])
        total = len(questions)
        pct   = int(score / total * 100) if total else 0

        st.markdown(
            f"<div style='text-align:center;margin:12px 0'>"
            f"<span class='score-badge'>🎯 {score}/{total}문제 정답 ({pct}점)</span>"
            f"</div>", unsafe_allow_html=True
        )

        if st.session_state[fkey]:
            st.markdown(
                f"<div class='feedback-box'>💬 <b>AI 피드백</b><br><br>"
                f"{st.session_state[fkey]}</div>",
                unsafe_allow_html=True
            )

        st.markdown("&nbsp;")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔁 다시 풀기", key=f"retry_{p['id']}_{quiz_type}",
                         use_container_width=True):
                for k in [qkey, akey, skey, fkey]:
                    st.session_state[k] = None if k in [qkey, fkey] else ({} if k == akey else False)
                st.rerun()
        with c2:
            if st.button("🔄 새 문제", key=f"new2_{p['id']}_{quiz_type}",
                         use_container_width=True):
                st.session_state[qkey] = None
                st.rerun()

# ── 6. 상세 페이지 ────────────────────────────────────────
def show_detail(passages):
    p = next((x for x in passages if x["id"] == st.session_state.selected_id), None)
    if not p:
        st.session_state.current_page = 'list'
        st.rerun()

    if st.button("⬅️ 목록으로"):
        st.session_state.current_page = 'list'
        st.rerun()

    st.markdown(
        f"### 📄 지문 #{p['id']} "
        f"<span style='font-size:0.85rem;color:#666'>| {p['category']}</span>",
        unsafe_allow_html=True
    )
    st.markdown(f"<div class='passage-card'>{p['passage']}</div>",
                unsafe_allow_html=True)
    st.markdown("&nbsp;")

    tab1, tab2, tab3, tab4 = st.tabs(["📖 어휘", "🔤 단어 퀴즈", "📝 독해 문제", "🔍 문법 문제"])
    with tab1:
        if p.get('vocabulary'):
            for line in p['vocabulary'].strip().split('\n'):
                if ':' in line or '：' in line:
                    parts = line.replace('：', ':').split(':', 1)
                    st.markdown(
                        f"**{parts[0].strip()}** — {parts[1].strip()}"
                        if len(parts) == 2 else line
                    )
                else:
                    st.markdown(line)
        else:
            st.info("어휘 데이터가 없습니다.")
    with tab2:
        render_quiz_tab(p, "vocabulary", "단어 퀴즈")
    with tab3:
        render_quiz_tab(p, "comprehension", "독해 문제")
    with tab4:
        render_quiz_tab(p, "grammar", "문법 문제")

# ── 7. 목록 페이지 ────────────────────────────────────────
def show_list(passages):
    st.markdown("## 📚 수능특강 AI 학습")
    st.markdown("지문을 선택하면 AI가 맞춤 퀴즈와 피드백을 제공합니다.")
    st.markdown("---")

    categories = ["전체"] + sorted(set(p['category'] for p in passages))
    idx = categories.index(st.session_state.selected_category) \
          if st.session_state.selected_category in categories else 0
    selected = st.selectbox("🗂️ 소재 선택", categories, index=idx)
    st.session_state.selected_category = selected

    filtered = passages if selected == "전체" \
               else [p for p in passages if p['category'] == selected]

    st.caption(f"총 {len(filtered)}개 지문")
    st.markdown("&nbsp;")

    for p in filtered:
        done = p['id'] in st.session_state.completed
        col1, col2 = st.columns([5, 1])
        with col1:
            badge = "✅" if done else "📄"
            st.markdown(f"{badge} **[{p['category']}]** 지문 {p['id']}")
            st.caption(p['passage'][:70] + "...")
        with col2:
            if st.button("학습 →", key=f"go_{p['id']}", use_container_width=True):
                st.session_state.selected_id = p['id']
                st.session_state.current_page = 'detail'
                st.rerun()
        st.markdown("---")

# ── 8. 메인 ──────────────────────────────────────────────
def main():
    init_state()
    data = load_passages()

    if not data:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, "data")
        csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
        st.error("CSV 파일을 찾을 수 없습니다.")
        st.code(f"탐색 경로: {data_dir}\n찾은 파일: {csv_files}")
        return

    if st.session_state.current_page == 'list':
        show_list(data)
    else:
        show_detail(data)

if __name__ == "__main__":
    main()

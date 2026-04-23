import streamlit as st
import streamlit.components.v1 as components
import json
import os
import glob
import csv
import google.generativeai as genai

# ── AI 설정 ──────────────────────────────────────────────
genai.configure(api_key=st.secrets.get("GOOGLE_API_KEY", ""))
model = genai.GenerativeModel(model_name="gemini-2.5-flash")

# ── 페이지 설정 ──────────────────────────────────────────
st.set_page_config(
    page_title="맞춤형 AI 영어 학습",
    page_icon="🎧",
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

반드시 JSON만 출력하세요 (설명, 마크다운 코드블록 없이):
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
        prompt = f"""다음 영어 지문으로 수능형 독해 문제 2개를 만드세요. (주제 파악 1개, 요지 파악 1개)

지문:
{p['passage'][:500]}

반드시 JSON만 출력하세요 (설명, 마크다운 코드블록 없이):
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

반드시 JSON만 출력하세요 (설명, 마크다운 코드블록 없이):
{{
  "questions": [
    {{
      "id": 1,
      "type": "어법 판단",
      "sentence": "문제 문장 (**밑줄부분** 표시)",
      "question": "밑줄 친 부분 중 어법상 틀린 것은?",
      "options": ["①보기1", "②보기2", "③보기3", "④보기4", "⑤보기5"],
      "answer": "2",
      "explanation": "한국어로 문법 설명 포함 해설"
    }}
  ]
}}"""

    response = model.generate_content(prompt)
    text = response.text.strip()

    start = text.find("{")
    end   = text.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError(f"JSON을 찾을 수 없습니다.\n응답: {text[:200]}")
    return json.loads(text[start:end])

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
        return f"피드백 생성 중 오류: {e}"

# ── 5. TTS 플레이어 ───────────────────────────────────────
def render_tts_player(passage_text, player_id):
    """문장 단위 TTS + 현재 문장 하이라이트 (Web Speech API)"""
    # JSON 직렬화로 안전하게 JS에 전달 (이스케이프 자동 처리)
    passage_json = json.dumps(passage_text)

    html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Segoe UI', sans-serif;
    background: transparent;
    padding: 4px 0;
  }}
  #passage-box {{
    background: #f8f9ff;
    border-left: 4px solid #4f6ef7;
    border-radius: 8px;
    padding: 16px 20px;
    line-height: 1.95;
    font-size: 0.96rem;
    color: #1e293b;
    margin-bottom: 14px;
    word-break: break-word;
  }}
  .sent-span {{
    border-radius: 4px;
    padding: 1px 2px;
    transition: background 0.25s, color 0.25s;
    cursor: pointer;
  }}
  .sent-span:hover {{
    background: #e0e7ff;
  }}
  .sent-active {{
    background: #fde68a !important;
    color: #92400e;
    font-weight: 600;
    border-radius: 4px;
    box-shadow: 0 0 0 2px #f59e0b55;
  }}
  .sent-done {{
    color: #94a3b8;
  }}
  #controls {{
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
    background: #f1f5f9;
    border-radius: 10px;
    padding: 10px 14px;
  }}
  .ctrl-btn {{
    border: none;
    border-radius: 8px;
    padding: 7px 16px;
    font-size: 0.88rem;
    font-weight: 600;
    cursor: pointer;
    transition: opacity 0.15s, transform 0.1s;
  }}
  .ctrl-btn:hover {{ opacity: 0.85; transform: scale(1.03); }}
  .ctrl-btn:active {{ transform: scale(0.97); }}
  #btn-play  {{ background: #4f6ef7; color: #fff; }}
  #btn-pause {{ background: #f59e0b; color: #fff; }}
  #btn-stop  {{ background: #ef4444; color: #fff; }}
  #btn-prev  {{ background: #e2e8f0; color: #334155; }}
  #btn-next  {{ background: #e2e8f0; color: #334155; }}
  .speed-group {{
    display: flex;
    align-items: center;
    gap: 6px;
    margin-left: auto;
  }}
  .speed-group label {{ font-size: 0.82rem; color: #64748b; }}
  #speed-sel {{
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 0.84rem;
    background: #fff;
    color: #334155;
    cursor: pointer;
  }}
  #status-bar {{
    font-size: 0.8rem;
    color: #64748b;
    margin-top: 8px;
    min-height: 18px;
    padding-left: 2px;
  }}
  #progress {{
    font-size: 0.78rem;
    color: #94a3b8;
    margin-left: 4px;
  }}
</style>
</head>
<body>

<div id="passage-box">로딩 중...</div>

<div id="controls">
  <button class="ctrl-btn" id="btn-prev"  onclick="moveSent(-1)">⏮ 이전</button>
  <button class="ctrl-btn" id="btn-play"  onclick="startTTS()">▶ 읽기</button>
  <button class="ctrl-btn" id="btn-pause" onclick="togglePause()">⏸ 일시정지</button>
  <button class="ctrl-btn" id="btn-stop"  onclick="stopTTS()">⏹ 정지</button>
  <button class="ctrl-btn" id="btn-next"  onclick="moveSent(1)">⏭ 다음</button>
  <div class="speed-group">
    <label>속도</label>
    <select id="speed-sel">
      <option value="0.7">느리게 (0.7×)</option>
      <option value="0.85">보통보다 느리게 (0.85×)</option>
      <option value="1.0" selected>보통 (1.0×)</option>
      <option value="1.2">빠르게 (1.2×)</option>
      <option value="1.5">매우 빠르게 (1.5×)</option>
    </select>
  </div>
</div>
<div id="status-bar">
  <span id="status-text">재생 버튼을 눌러 듣기 시작</span>
  <span id="progress"></span>
</div>

<script>
// ── 지문 파싱 ──────────────────────────────────────────
const rawText = {passage_json};

// 영어 문장 분리: 약어(Mr. Dr. 등) 예외 처리 포함
function splitSentences(text) {{
  // 약어 보호: Mr. Mrs. Dr. St. vs. etc. 를 임시 토큰으로 대체
  let t = text
    .replace(/\\b(Mr|Mrs|Ms|Dr|St|Prof|Jr|Sr|vs|etc|e\\.g|i\\.e|Fig|No|Vol|pp|cf)\\./g, '$1<DOT>')
    .replace(/\\b([A-Z])\\.([A-Z])\\./g, '$1<DOT>$2<DOT>');  // 약자 (U.S.A.)

  // 문장 분리 정규식
  const raw = t.split(/(?<=[.!?]['"\\)\\]]?)\\s+(?=[A-Z"\\(\\[])/);

  return raw
    .map(s => s.replace(/<DOT>/g, '.').trim())
    .filter(s => s.length > 0);
}}

const sentences = splitSentences(rawText);
let currentIdx = 0;
let isPlaying  = false;
let isPaused   = false;

// ── DOM 구성 ──────────────────────────────────────────
const box = document.getElementById('passage-box');
box.innerHTML = '';

sentences.forEach((sent, i) => {{
  const span = document.createElement('span');
  span.className = 'sent-span';
  span.id = 'sent-{player_id}-' + i;
  span.textContent = sent + ' ';
  span.addEventListener('click', () => jumpTo(i));
  box.appendChild(span);
}});

// ── 상태 업데이트 ──────────────────────────────────────
function updateHighlight(idx, state) {{
  sentences.forEach((_, i) => {{
    const el = document.getElementById('sent-{player_id}-' + i);
    if (!el) return;
    el.classList.remove('sent-active', 'sent-done');
    if (i === idx && state === 'active') el.classList.add('sent-active');
    if (i < idx  && state === 'active') el.classList.add('sent-done');
  }});
}}

function setStatus(msg) {{
  document.getElementById('status-text').textContent = msg;
  document.getElementById('progress').textContent =
    sentences.length > 0 ? ' (' + (currentIdx + 1) + ' / ' + sentences.length + ')' : '';
}}

function scrollToSent(idx) {{
  const el = document.getElementById('sent-{player_id}-' + idx);
  if (el) el.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
}}

// ── TTS 핵심 ──────────────────────────────────────────
function speakFrom(idx) {{
  if (idx >= sentences.length) {{
    isPlaying = false;
    isPaused  = false;
    updateHighlight(-1, 'done');
    setStatus('재생 완료 ✅');
    document.getElementById('progress').textContent = '';
    return;
  }}

  currentIdx = idx;
  updateHighlight(idx, 'active');
  scrollToSent(idx);
  setStatus('읽는 중: "' + sentences[idx].slice(0, 40) + (sentences[idx].length > 40 ? '…' : '') + '"');

  const utter = new SpeechSynthesisUtterance(sentences[idx]);
  utter.lang  = 'en-US';
  utter.rate  = parseFloat(document.getElementById('speed-sel').value);
  utter.pitch = 1.0;

  // 영어 음성 우선 선택
  const voices = window.speechSynthesis.getVoices();
  const enVoice = voices.find(v => v.lang.startsWith('en') && v.name.includes('Google'))
               || voices.find(v => v.lang.startsWith('en-US'))
               || voices.find(v => v.lang.startsWith('en'));
  if (enVoice) utter.voice = enVoice;

  utter.onend = () => {{
    if (isPlaying && !isPaused) speakFrom(currentIdx + 1);
  }};
  utter.onerror = (e) => {{
    if (e.error !== 'interrupted') {{
      setStatus('오류 발생: ' + e.error);
    }}
  }};

  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utter);
}}

function startTTS() {{
  window.speechSynthesis.cancel();
  isPlaying = true;
  isPaused  = false;
  speakFrom(currentIdx);
}}

function togglePause() {{
  if (!isPlaying) {{ startTTS(); return; }}
  if (isPaused) {{
    isPaused = false;
    window.speechSynthesis.resume();
    setStatus('재생 재개');
  }} else {{
    isPaused = true;
    window.speechSynthesis.pause();
    setStatus('일시 정지됨 ⏸');
  }}
}}

function stopTTS() {{
  isPlaying = false;
  isPaused  = false;
  window.speechSynthesis.cancel();
  updateHighlight(-1, 'done');
  currentIdx = 0;
  setStatus('정지됨. 재생 버튼으로 처음부터 시작');
  document.getElementById('progress').textContent = '';
}}

function jumpTo(idx) {{
  window.speechSynthesis.cancel();
  currentIdx = idx;
  if (isPlaying) {{
    speakFrom(idx);
  }} else {{
    updateHighlight(idx, 'active');
    setStatus('문장 ' + (idx + 1) + '번 선택됨 — 재생 버튼을 누르세요');
    document.getElementById('progress').textContent =
      ' (' + (idx + 1) + ' / ' + sentences.length + ')';
  }}
}}

function moveSent(delta) {{
  const next = Math.max(0, Math.min(sentences.length - 1, currentIdx + delta));
  jumpTo(next);
  if (isPlaying) speakFrom(next);
}}

// 속도 변경 시 현재 재생 중이면 재시작
document.getElementById('speed-sel').addEventListener('change', () => {{
  if (isPlaying && !isPaused) {{
    window.speechSynthesis.cancel();
    speakFrom(currentIdx);
  }}
}});

// 음성 목록 로드 후 초기화
if (window.speechSynthesis.onvoiceschanged !== undefined) {{
  window.speechSynthesis.onvoiceschanged = () => {{}};
}}
window.speechSynthesis.getVoices();

setStatus('재생 버튼을 눌러 듣기 시작 | 문장을 직접 클릭해도 됩니다');
</script>
</body>
</html>
"""
    components.html(html_code, height=430, scrolling=False)


# ── 5-1. AI 튜터 ──────────────────────────────────────────
def render_ai_tutor(p, quiz_type):
    """지문 기반 AI 튜터 채팅 (왼쪽 하단)"""
    hkey = f"tutor_history_{p['id']}_{quiz_type}"
    ikey = f"tutor_input_{p['id']}_{quiz_type}"

    if hkey not in st.session_state:
        st.session_state[hkey] = []

    st.markdown("""
<div style="
    background:linear-gradient(135deg,#4f6ef7,#7c4fff);
    border-radius:10px 10px 0 0;
    padding:10px 16px;
    margin-top:16px;
">
  <span style="color:white;font-weight:700;font-size:0.95rem;">🤖 AI 튜터</span>
  <span style="color:#c7d2fe;font-size:0.78rem;margin-left:8px;">지문이나 문제에 대해 무엇이든 물어보세요</span>
</div>
""", unsafe_allow_html=True)

    # 채팅 기록 표시
    chat_html = """
<div id="tutor-chat" style="
    background:#fff;
    border:1px solid #e0e7ff;
    border-top:none;
    padding:12px 14px;
    height:220px;
    overflow-y:auto;
    display:flex;
    flex-direction:column;
    gap:8px;
    font-size:0.87rem;
">"""

    history = st.session_state[hkey]
    if not history:
        chat_html += """
<div style="color:#94a3b8;text-align:center;margin:auto;font-size:0.85rem;">
  💬 질문을 입력하면 AI 튜터가 답변해드립니다.<br>
  <span style="font-size:0.78rem;">예: "이 지문의 핵심 주제가 뭐야?", "3번 문장 해석해줘"</span>
</div>"""
    else:
        for msg in history:
            if msg["role"] == "user":
                chat_html += f"""
<div style="align-self:flex-end;background:#4f6ef7;color:white;
    border-radius:16px 16px 4px 16px;padding:8px 13px;max-width:85%;
    word-break:break-word;line-height:1.5;">
  {msg["content"]}
</div>"""
            else:
                chat_html += f"""
<div style="align-self:flex-start;background:#f1f5f9;color:#1e293b;
    border-radius:16px 16px 16px 4px;padding:8px 13px;max-width:90%;
    word-break:break-word;line-height:1.6;">
  🤖 {msg["content"]}
</div>"""

    chat_html += "</div>"
    st.markdown(chat_html, unsafe_allow_html=True)

    # 입력창 + 버튼
    col_inp, col_btn = st.columns([5, 1])
    with col_inp:
        user_input = st.text_input(
            "질문 입력",
            key=ikey,
            placeholder="질문을 입력하세요...",
            label_visibility="collapsed"
        )
    with col_btn:
        send = st.button("전송", key=f"tutor_send_{p['id']}_{quiz_type}",
                         use_container_width=True, type="primary")

    col_c1, col_c2 = st.columns([3, 1])
    with col_c2:
        if st.button("대화 초기화", key=f"tutor_clear_{p['id']}_{quiz_type}",
                     use_container_width=True):
            st.session_state[hkey] = []
            st.rerun()

    if send and user_input.strip():
        st.session_state[hkey].append({"role": "user", "content": user_input.strip()})

        # 대화 이력 → Gemini 멀티턴 포맷
        gemini_history = []
        for m in st.session_state[hkey][:-1]:
            role = "user" if m["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [m["content"]]})

        system_ctx = f"""너는 친절한 영어 학습 AI 튜터야. 학생이 아래 영어 지문을 공부하고 있어.
지문을 바탕으로 질문에 한국어로 답해줘. 어휘, 문법, 해석, 독해 전략 모두 도움을 줄 수 있어.
답변은 간결하고 명확하게 3~5문장 이내로 해줘.

[지문]
{p['passage']}

[어휘 정보]
{p.get('vocabulary', '')[:300]}
"""
        full_question = system_ctx + "\n\n[학생 질문]\n" + user_input.strip()

        with st.spinner("AI 튜터가 답변 중..."):
            try:
                chat = model.start_chat(history=gemini_history)
                response = chat.send_message(full_question)
                answer = response.text.strip()
            except Exception as e:
                answer = f"오류가 발생했습니다: {e}"

        st.session_state[hkey].append({"role": "assistant", "content": answer})
        st.rerun()


# ── 6. 퀴즈 탭 렌더링 ─────────────────────────────────────
def render_quiz_tab(p, quiz_type, label):
    qkey = f"quiz_{p['id']}_{quiz_type}"
    akey = f"ans_{p['id']}_{quiz_type}"
    skey = f"sub_{p['id']}_{quiz_type}"
    fkey = f"fb_{p['id']}_{quiz_type}"

    for k, d in [(qkey, None), (akey, {}), (skey, False), (fkey, None)]:
        if k not in st.session_state:
            st.session_state[k] = d

    if st.session_state[qkey] is None:
        st.markdown("&nbsp;")
        if st.button(f"🤖 AI로 {label} 생성하기", key=f"gen_{p['id']}_{quiz_type}",
                     type="primary", use_container_width=True):
            with st.spinner("AI가 문제를 만들고 있습니다..."):
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
                st.session_state[qkey] = None
                st.session_state[akey] = {}
                st.session_state[skey] = False
                st.session_state[fkey] = None
                st.rerun()
        with c2:
            if st.button("🔄 새 문제", key=f"new2_{p['id']}_{quiz_type}",
                         use_container_width=True):
                st.session_state[qkey] = None
                st.rerun()

# ── 7. 상세 페이지 ────────────────────────────────────────
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

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎧 듣기 (TTS)", "📖 어휘", "🔤 단어 퀴즈", "📝 독해 문제", "🔍 문법 문제"
    ])

    with tab1:
        st.markdown("#### 🎧 문장 단위 듣기")
        st.caption("▶ 재생 버튼으로 전체 읽기 | 문장을 직접 클릭하면 해당 문장부터 재생 | ⏮⏭ 버튼으로 문장 이동")
        render_tts_player(p['passage'], player_id=p['id'])

    with tab2:
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

    # 퀴즈 탭 공통: 왼쪽 지문 고정 | 오른쪽 퀴즈
    _style = (
        "background:#f8f9ff;"
        "border-left:4px solid #4f6ef7;"
        "border-radius:8px;"
        "padding:16px 20px;"
        "line-height:1.9;"
        "font-size:0.93rem;"
        "color:#1e293b;"
        "max-height:72vh;"
        "overflow-y:auto;"
    )
    passage_panel = (
        "<div style=\"" + _style + "\">"
        + p["passage"]
        + "</div>"
    )

    with tab3:
        left, right = st.columns([1, 1], gap="large")
        with left:
            st.markdown("##### 📄 지문")
            st.markdown(passage_panel, unsafe_allow_html=True)
            render_ai_tutor(p, "vocabulary")
        with right:
            st.markdown("##### 🔤 단어 퀴즈")
            render_quiz_tab(p, "vocabulary", "단어 퀴즈")

    with tab4:
        left, right = st.columns([1, 1], gap="large")
        with left:
            st.markdown("##### 📄 지문")
            st.markdown(passage_panel, unsafe_allow_html=True)
            render_ai_tutor(p, "comprehension")
        with right:
            st.markdown("##### 📝 독해 문제")
            render_quiz_tab(p, "comprehension", "독해 문제")

    with tab5:
        left, right = st.columns([1, 1], gap="large")
        with left:
            st.markdown("##### 📄 지문")
            st.markdown(passage_panel, unsafe_allow_html=True)
            render_ai_tutor(p, "grammar")
        with right:
            st.markdown("##### 🔍 문법 문제")
            render_quiz_tab(p, "grammar", "문법 문제")

# ── 8. 목록 페이지 ────────────────────────────────────────
def show_list(passages):
    st.markdown("## 🎧 맞춤형 AI 영어 학습")
    st.markdown("지문을 선택하면 TTS 듣기, AI 퀴즈, 맞춤 피드백을 이용할 수 있습니다.")
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

# ── 9. 메인 ──────────────────────────────────────────────
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

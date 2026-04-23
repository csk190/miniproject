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

# ── 5. TTS 플레이어 (좌: 지문+TTS+단어클릭 / 우: 단어정보+단어장) ──────
def render_tts_player(passage_text, player_id):
    # `</script>` 문자열이 지문 안에 있으면 HTML 파서가 script 블록을 강제 종료함
    # → json.dumps 후 반드시 이스케이프 처리 필요
    passage_json = json.dumps(passage_text or "").replace("</", r"<\/")
    pid = str(player_id)

    html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ font-family:'Segoe UI',sans-serif; background:transparent; overflow:hidden; }}

.layout {{ display:flex; gap:14px; height:630px; }}

/* ── 왼쪽 패널 ─────────────────────── */
.left-panel {{
  flex:1.3; display:flex; flex-direction:column; gap:8px; min-width:0;
}}
.tts-controls {{
  background:#f1f5f9; border-radius:10px; padding:8px 12px;
  display:flex; align-items:center; gap:7px; flex-wrap:wrap; flex-shrink:0;
}}
.ctrl-btn {{
  border:none; border-radius:7px; padding:6px 12px;
  font-size:0.81rem; font-weight:700; cursor:pointer;
  transition:opacity .15s, transform .1s;
}}
.ctrl-btn:hover {{ opacity:.85; transform:scale(1.03); }}
#btn-play  {{ background:#4f6ef7; color:#fff; }}
#btn-pause {{ background:#f59e0b; color:#fff; }}
#btn-stop  {{ background:#ef4444; color:#fff; }}
#btn-prev, #btn-next {{ background:#e2e8f0; color:#334155; }}
.speed-group {{ margin-left:auto; display:flex; align-items:center; gap:5px; }}
.speed-group label {{ font-size:0.76rem; color:#64748b; }}
#speed-sel {{
  border:1px solid #cbd5e1; border-radius:5px;
  padding:3px 6px; font-size:0.78rem; background:#fff; color:#334155;
}}
#passage-box {{
  flex:1; background:#f8f9ff; border-left:4px solid #4f6ef7;
  border-radius:8px; padding:14px 16px; line-height:2.05;
  font-size:0.91rem; color:#1e293b; overflow-y:auto; word-break:break-word;
}}
.word-span {{
  cursor:pointer; border-radius:3px; padding:1px 1px;
  transition:background .12s;
}}
.word-span:hover {{ background:#dbeafe; }}
.word-selected {{ background:#bfdbfe !important; font-weight:700; border-radius:3px; }}
.sent-active {{
  background:#fde68a !important; border-radius:3px;
  box-shadow:0 0 0 2px #f59e0b44;
}}
.sent-done {{ color:#94a3b8; }}
#status-bar {{
  font-size:0.74rem; color:#64748b; flex-shrink:0; padding:0 2px;
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
}}

/* ── 오른쪽 패널 ────────────────────── */
.right-panel {{
  width:272px; display:flex; flex-direction:column; gap:10px; flex-shrink:0;
}}

/* 단어 정보 */
.word-panel {{
  background:#fff; border:1px solid #e0e7ff; border-radius:12px;
  padding:14px; flex-shrink:0;
}}
.panel-label {{
  font-size:0.72rem; font-weight:800; color:#94a3b8;
  text-transform:uppercase; letter-spacing:.06em; margin-bottom:9px;
}}
.word-heading {{ font-size:1.25rem; font-weight:800; color:#1e293b; }}
.word-phonetic {{
  font-size:0.84rem; color:#7c4fff; margin:2px 0 7px;
  display:flex; align-items:center; gap:6px;
}}
.audio-btn {{
  background:none; border:1px solid #c7d2fe; border-radius:5px;
  color:#4f6ef7; font-size:0.72rem; padding:1px 7px; cursor:pointer;
}}
.pos-badge {{
  display:inline-block; background:#ede9fe; color:#5b21b6;
  border-radius:10px; padding:2px 10px; font-size:0.73rem;
  font-weight:700; margin-bottom:7px;
}}
.definition {{ font-size:0.83rem; color:#374151; line-height:1.65; }}
.example {{
  font-size:0.78rem; color:#6b7280; font-style:italic;
  margin-top:5px; padding-top:5px; border-top:1px solid #f1f5f9;
}}
.add-btn {{
  width:100%; margin-top:10px; border:none; border-radius:8px;
  padding:8px; font-size:0.82rem; font-weight:700; cursor:pointer;
  background:#4f6ef7; color:#fff; transition:background .15s;
}}
.add-btn:hover {{ background:#3b55d9; }}
.add-btn:disabled {{ background:#a5b4fc; cursor:default; }}
.placeholder {{
  color:#94a3b8; font-size:0.82rem; text-align:center;
  padding:28px 8px; line-height:1.7;
}}

/* 단어장 */
.vocab-panel {{
  background:#fff; border:1px solid #e0e7ff; border-radius:12px;
  padding:12px 14px; flex:1; display:flex; flex-direction:column; min-height:0;
}}
.vocab-header {{
  display:flex; align-items:center; gap:6px; margin-bottom:8px; flex-shrink:0;
}}
.vocab-title {{ font-size:0.72rem; font-weight:800; color:#94a3b8; text-transform:uppercase; letter-spacing:.06em; }}
.vocab-badge {{
  background:#4f6ef7; color:#fff; border-radius:10px;
  padding:1px 8px; font-size:0.72rem; font-weight:700; margin-left:2px;
}}
.clear-btn {{
  margin-left:auto; background:none; border:1px solid #fca5a5;
  border-radius:5px; color:#ef4444; font-size:0.7rem; padding:2px 7px; cursor:pointer;
}}
.vocab-list {{ flex:1; overflow-y:auto; }}
.vocab-item {{
  display:flex; justify-content:space-between; align-items:flex-start;
  padding:7px 0; border-bottom:1px solid #f8fafc; gap:5px;
}}
.vocab-item:last-child {{ border-bottom:none; }}
.vocab-word {{ font-weight:700; font-size:0.86rem; color:#1e293b; }}
.vocab-pos {{ font-size:0.7rem; color:#7c4fff; font-weight:700; margin-left:4px; }}
.vocab-ph {{ font-size:0.7rem; color:#7c4fff; }}
.vocab-def {{ font-size:0.76rem; color:#475569; line-height:1.4; margin-top:1px; }}
.del-btn {{
  background:none; border:none; cursor:pointer;
  color:#cbd5e1; font-size:0.88rem; padding:0 2px; flex-shrink:0;
  transition:color .12s;
}}
.del-btn:hover {{ color:#ef4444; }}
.empty-vocab {{
  color:#94a3b8; font-size:0.8rem; text-align:center; padding:24px 0; line-height:1.8;
}}
</style>
</head>
<body>
<div class="layout">

<!-- ── 왼쪽: 지문 + TTS ────────────────────── -->
<div class="left-panel">
  <div class="tts-controls">
    <button class="ctrl-btn" id="btn-prev"  onclick="moveSent(-1)">⏮</button>
    <button class="ctrl-btn" id="btn-play"  onclick="startTTS()">▶ 읽기</button>
    <button class="ctrl-btn" id="btn-pause" onclick="togglePause()">⏸</button>
    <button class="ctrl-btn" id="btn-stop"  onclick="stopTTS()">⏹</button>
    <button class="ctrl-btn" id="btn-next"  onclick="moveSent(1)">⏭</button>
    <div class="speed-group">
      <label>속도</label>
      <select id="speed-sel">
        <option value="0.7">0.7×</option>
        <option value="0.85">0.85×</option>
        <option value="1.0" selected>1.0×</option>
        <option value="1.2">1.2×</option>
        <option value="1.5">1.5×</option>
      </select>
    </div>
  </div>
  <div id="passage-box">로딩 중...</div>
  <div id="status-bar">단어를 클릭하면 의미를 확인할 수 있어요 | 문장 클릭 → 해당 문장부터 재생</div>
</div>

<!-- ── 오른쪽: 단어 정보 + 단어장 ─────────── -->
<div class="right-panel">

  <!-- 단어 정보 -->
  <div class="word-panel">
    <div class="panel-label">📖 단어 정보</div>
    <div id="word-content">
      <div class="placeholder">
        단어를 클릭하면<br>의미 · 품사 · 발음을<br>확인할 수 있어요 👆
      </div>
    </div>
  </div>

  <!-- 단어장 -->
  <div class="vocab-panel">
    <div class="vocab-header">
      <span class="vocab-title">📚 단어장</span>
      <span class="vocab-badge" id="vocab-count">0</span>
      <button class="clear-btn" id="clear-btn" onclick="clearVocab()">전체 삭제</button>
    </div>
    <div class="vocab-list" id="vocab-list">
      <div class="empty-vocab">아직 추가된 단어가 없어요.<br>단어를 클릭해 추가해 보세요!</div>
    </div>
  </div>

</div>
</div>

<script>
const SKEY = 'ai_vocab_{pid}';
const rawText = {passage_json};
let vocab = [];
try {{ vocab = JSON.parse(localStorage.getItem(SKEY) || '[]'); }} catch(e) {{}}
let currentWord = null;
let currentAudio = null;
let currentIdx = 0, isPlaying = false, isPaused = false;

// ── 문장 분리 (lookbehind 미사용 — 브라우저 호환) ────
function splitSentences(text) {{
  // 약어 보호
  var abbr = text
    .replace(/\\b(Mr|Mrs|Ms|Dr|St|Prof|Jr|Sr|vs|etc)\\./g, '$1<DOT>')
    .replace(/\\b([A-Z])\\.([A-Z])\\./g, '$1<DOT>$2<DOT>');

  // 단어 단위로 분리해서 문장 경계 탐지 (lookbehind 없이)
  var words = abbr.split(' ');
  var sentences = [];
  var cur = [];

  for (var i = 0; i < words.length; i++) {{
    cur.push(words[i]);
    var w = words[i];
    // 문장 종결 조건: 단어가 .!? 로 끝나고 다음 단어가 대문자로 시작
    if (/[.!?]["'\\)]*$/.test(w)) {{
      var next = words[i + 1] || '';
      if (next === '' || /^[A-Z"'\\(]/.test(next)) {{
        sentences.push(cur.join(' ').replace(/<DOT>/g, '.').trim());
        cur = [];
      }}
    }}
  }}
  if (cur.length) sentences.push(cur.join(' ').replace(/<DOT>/g, '.').trim());
  return sentences.filter(function(s) {{ return s.length > 0; }});
}}

var sentences;
try {{
  sentences = splitSentences(rawText);
  if (!sentences || sentences.length === 0) sentences = [rawText];
}} catch(e) {{
  sentences = [rawText];
}}

// ── 지문 렌더링 (문장 > 단어 span) ──────────
var box = document.getElementById('passage-box');
try {{
  box.innerHTML = '';

  sentences.forEach(function(sent, sIdx) {{
    var sentEl = document.createElement('span');
    sentEl.id = 'sent-{pid}-' + sIdx;
    sentEl.className = 'sent-span';

    // 단어 토큰화
    var tokens = sent.split(/( +)/);
    tokens.forEach(function(tok) {{
      if (/^ +$/.test(tok)) {{
        sentEl.appendChild(document.createTextNode(tok));
      }} else if (tok) {{
        var clean = tok.replace(/[^a-zA-Z'-]/g, '').toLowerCase();
        if (clean.length > 1) {{
          var w = document.createElement('span');
          w.className = 'word-span';
          w.textContent = tok;
          (function(word, el) {{
            el.addEventListener('click', function(e) {{
              e.stopPropagation();
              document.querySelectorAll('.word-selected').forEach(function(x) {{
                x.classList.remove('word-selected');
              }});
              el.classList.add('word-selected');
              lookupWord(word);
            }});
          }})(clean, w);
          sentEl.appendChild(w);
        }} else {{
          sentEl.appendChild(document.createTextNode(tok));
        }}
      }}
    }});

    (function(idx) {{
      sentEl.addEventListener('click', function() {{ jumpTo(idx); }});
    }})(sIdx);
    box.appendChild(sentEl);
    box.appendChild(document.createTextNode(' '));
  }});
}} catch(e) {{
  box.innerHTML = '<div style="color:#ef4444;padding:12px">렌더링 오류: ' + e.message + '</div>';
}}

// ── 단어 사전 검색 (dictionaryapi.dev) ───────
function lookupWord(word) {{
  currentWord = null; currentAudio = null;
  document.getElementById('word-content').innerHTML =
    '<div class="placeholder">🔍 검색 중...</div>';

  fetch('https://api.dictionaryapi.dev/api/v2/entries/en/' + word)
    .then(r => r.json())
    .then(data => {{
      if (!Array.isArray(data) || !data[0]) {{
        document.getElementById('word-content').innerHTML =
          '<div class="placeholder">❌ 단어를 찾을 수 없습니다.<br><small style="color:#cbd5e1">' + word + '</small></div>';
        return;
      }}
      const entry   = data[0];
      const phonetic = entry.phonetic || entry.phonetics?.find(p => p.text)?.text || '';
      const audioUrl = entry.phonetics?.find(p => p.audio?.startsWith('http'))?.audio || null;
      const meaning  = entry.meanings?.[0];
      const pos      = meaning?.partOfSpeech || '';
      const defObj   = meaning?.definitions?.[0];
      const definition = defObj?.definition || '';
      const example    = defObj?.example   || '';

      currentWord  = {{ word, phonetic, pos, definition }};
      currentAudio = audioUrl;

      const already = vocab.some(v => v.word === word);
      let html = '<div class="word-heading">' + entry.word + '</div>';
      if (phonetic) {{
        html += '<div class="word-phonetic">' + phonetic;
        if (audioUrl) html += '<button class="audio-btn" onclick="playAudio()">🔊 듣기</button>';
        html += '</div>';
      }}
      if (pos)        html += '<div><span class="pos-badge">' + pos + '</span></div>';
      if (definition) html += '<div class="definition">' + definition + '</div>';
      if (example)    html += '<div class="example">"' + example + '"</div>';
      html += '<button class="add-btn" id="add-btn" onclick="addToVocab()"'
           + (already ? ' disabled' : '') + '>'
           + (already ? '✅ 단어장에 있음' : '+ 단어장에 추가') + '</button>';

      document.getElementById('word-content').innerHTML = html;
    }})
    .catch(() => {{
      document.getElementById('word-content').innerHTML =
        '<div class="placeholder">⚠️ 네트워크 오류가 발생했습니다.</div>';
    }});
}}

function playAudio() {{
  if (currentAudio) new Audio(currentAudio).play().catch(()=>{{}});
}}

// ── 단어장 ────────────────────────────────
function saveVocab() {{
  try {{ localStorage.setItem(SKEY, JSON.stringify(vocab)); }} catch(e) {{}}
}}

function addToVocab() {{
  if (!currentWord || vocab.some(v => v.word === currentWord.word)) return;
  vocab.unshift(currentWord);
  saveVocab(); renderVocab();
  const btn = document.getElementById('add-btn');
  if (btn) {{ btn.textContent = '✅ 단어장에 있음'; btn.disabled = true; }}
}}

function deleteVocab(word) {{
  vocab = vocab.filter(v => v.word !== word);
  saveVocab(); renderVocab();
  if (currentWord?.word === word) {{
    const btn = document.getElementById('add-btn');
    if (btn) {{ btn.textContent = '+ 단어장에 추가'; btn.disabled = false; }}
  }}
}}

function clearVocab() {{
  const btn = document.getElementById('clear-btn');
  if (btn.dataset.confirm !== '1') {{
    btn.textContent = '정말 삭제?'; btn.dataset.confirm = '1';
    setTimeout(() => {{ btn.textContent = '전체 삭제'; btn.dataset.confirm = ''; }}, 3000);
    return;
  }}
  vocab = []; saveVocab(); renderVocab();
  btn.textContent = '전체 삭제'; btn.dataset.confirm = '';
}}

function renderVocab() {{
  document.getElementById('vocab-count').textContent = vocab.length;
  const list = document.getElementById('vocab-list');
  if (vocab.length === 0) {{
    list.innerHTML = '<div class="empty-vocab">아직 추가된 단어가 없어요.<br>단어를 클릭해 추가해 보세요!</div>';
    return;
  }}
  list.innerHTML = vocab.map(v =>
    '<div class="vocab-item">' +
      '<div style="flex:1;min-width:0">' +
        '<div><span class="vocab-word">' + v.word + '</span>' +
          (v.pos ? '<span class="vocab-pos">' + v.pos + '</span>' : '') + '</div>' +
        (v.phonetic ? '<div class="vocab-ph">' + v.phonetic + '</div>' : '') +
        (v.definition ? '<div class="vocab-def">' + v.definition.slice(0,55) + (v.definition.length>55?'…':'') + '</div>' : '') +
      '</div>' +
      '<button class="del-btn" onclick="deleteVocab(\'' + v.word + '\')">✕</button>' +
    '</div>'
  ).join('');
}}

renderVocab();

// ── TTS ───────────────────────────────────
function updateHighlight(idx, state) {{
  sentences.forEach((_, i) => {{
    const el = document.getElementById('sent-{pid}-' + i);
    if (!el) return;
    el.classList.remove('sent-active','sent-done');
    if (i === idx && state === 'active') el.classList.add('sent-active');
    if (i < idx  && state === 'active') el.classList.add('sent-done');
  }});
}}

function setStatus(msg) {{
  document.getElementById('status-bar').textContent =
    msg + (sentences.length > 0 ? '  (' + (currentIdx+1) + ' / ' + sentences.length + ')' : '');
}}

function scrollToSent(idx) {{
  const el = document.getElementById('sent-{pid}-' + idx);
  if (el) el.scrollIntoView({{behavior:'smooth',block:'nearest'}});
}}

function speakFrom(idx) {{
  if (idx >= sentences.length) {{
    isPlaying = false; isPaused = false;
    updateHighlight(-1,'done');
    document.getElementById('status-bar').textContent = '재생 완료 ✅  단어를 클릭해 의미를 확인해 보세요';
    return;
  }}
  currentIdx = idx;
  updateHighlight(idx,'active');
  scrollToSent(idx);
  setStatus('읽는 중');

  const utter = new SpeechSynthesisUtterance(sentences[idx]);
  utter.lang = 'en-US';
  utter.rate = parseFloat(document.getElementById('speed-sel').value);
  const voices = window.speechSynthesis.getVoices();
  const voice  = voices.find(v => v.lang.startsWith('en') && v.name.includes('Google'))
              || voices.find(v => v.lang.startsWith('en-US'))
              || voices.find(v => v.lang.startsWith('en'));
  if (voice) utter.voice = voice;
  utter.onend  = () => {{ if (isPlaying && !isPaused) speakFrom(currentIdx+1); }};
  utter.onerror= e  => {{ if (e.error !== 'interrupted') setStatus('오류: ' + e.error); }};
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utter);
}}

function startTTS()    {{ window.speechSynthesis.cancel(); isPlaying=true; isPaused=false; speakFrom(currentIdx); }}
function togglePause() {{
  if (!isPlaying) {{ startTTS(); return; }}
  if (isPaused) {{ isPaused=false; window.speechSynthesis.resume(); setStatus('재생 재개'); }}
  else          {{ isPaused=true;  window.speechSynthesis.pause();  setStatus('일시 정지 ⏸'); }}
}}
function stopTTS() {{
  isPlaying=false; isPaused=false;
  window.speechSynthesis.cancel();
  updateHighlight(-1,'done'); currentIdx=0;
  document.getElementById('status-bar').textContent = '정지됨 | 단어를 클릭하면 의미를 확인할 수 있어요';
}}
function jumpTo(idx) {{
  window.speechSynthesis.cancel(); currentIdx=idx;
  if (isPlaying) speakFrom(idx);
  else {{ updateHighlight(idx,'active'); setStatus('문장 선택됨 — 재생 버튼을 누르세요'); }}
}}
function moveSent(delta) {{
  const next = Math.max(0, Math.min(sentences.length-1, currentIdx+delta));
  jumpTo(next); if (isPlaying) speakFrom(next);
}}

document.getElementById('speed-sel').addEventListener('change', () => {{
  if (isPlaying && !isPaused) {{ window.speechSynthesis.cancel(); speakFrom(currentIdx); }}
}});
if (window.speechSynthesis.onvoiceschanged !== undefined) window.speechSynthesis.onvoiceschanged = ()=>{{}};
window.speechSynthesis.getVoices();
</script>
</body>
</html>
"""
    components.html(html_code, height=660, scrolling=False)


# ── 5-2. 유튜브 영상 추천 ─────────────────────────────────
def render_youtube_tab(p):
    """AI가 지문 주제 분석 후 관련 유튜브 영상 추천"""
    ykey = f"yt_recs_{p['id']}"

    if ykey not in st.session_state:
        st.session_state[ykey] = None

    st.markdown("#### 🎬 관련 유튜브 영상 추천")
    st.caption("AI가 지문 주제를 분석해 학습에 도움이 되는 영상을 추천합니다.")
    st.markdown("---")

    col_btn, col_reset = st.columns([3, 1])
    with col_btn:
        if st.button("🔍 AI 영상 추천 받기", type="primary",
                     key=f"yt_gen_{p['id']}", use_container_width=True):
            with st.spinner("AI가 지문을 분석하고 관련 영상을 추천하는 중..."):
                prompt = f"""다음 영어 지문의 주제와 핵심 내용을 분석해서,
수능 영어 학습에 도움이 되는 유튜브 검색어 4개를 추천해줘.

지문:
{p["passage"][:600]}

영상 유형은 다음을 골고루 섞어줘:
- 지문 주제 관련 배경지식 영상 (영어 or 한국어)
- 수능 영어 지문 유형 학습 영상
- 핵심 어휘/표현 관련 영상

반드시 JSON만 출력해 (설명, 코드블록 없이):
{{
  "topic": "지문 핵심 주제 (한국어, 15자 이내)",
  "videos": [
    {{
      "title": "추천 영상 제목 (한국어, 25자 이내)",
      "search_query": "YouTube 검색어 (영어 or 한국어, 구체적으로)",
      "description": "이 영상을 추천하는 이유 (한국어, 2문장)",
      "type": "배경지식|어휘학습|독해전략|수능영어",
      "lang": "한국어|영어"
    }}
  ]
}}"""
                try:
                    response = model.generate_content(prompt)
                    text = response.text.strip()
                    start = text.find("{")
                    end   = text.rfind("}") + 1
                    result = json.loads(text[start:end])
                    st.session_state[ykey] = result
                except Exception as e:
                    st.error(f"추천 생성 오류: {e}")

    with col_reset:
        if st.session_state[ykey] and st.button("🔄 다시 추천", key=f"yt_reset_{p['id']}",
                                                  use_container_width=True):
            st.session_state[ykey] = None
            st.rerun()

    recs = st.session_state[ykey]
    if not recs:
        # 초기 안내 화면
        st.markdown("""
<div style="
    background:#f8f9ff;
    border:2px dashed #c7d2fe;
    border-radius:12px;
    padding:48px 24px;
    text-align:center;
    margin-top:16px;
">
  <div style="font-size:3rem;margin-bottom:12px;">🎬</div>
  <div style="font-size:1.05rem;font-weight:600;color:#4f6ef7;">AI 영상 추천을 받아보세요</div>
  <div style="font-size:0.88rem;color:#64748b;margin-top:8px;">
    위 버튼을 클릭하면 AI가 지문 주제를 분석해<br>
    학습에 도움되는 유튜브 영상 4개를 추천해드립니다.
  </div>
</div>
""", unsafe_allow_html=True)
        return

    # 주제 배지
    topic = recs.get("topic", "")
    if topic:
        st.markdown(
            f"<div style='margin:12px 0 20px;'>"
            f"<span style='background:#4f6ef7;color:white;border-radius:20px;"
            f"padding:5px 16px;font-size:0.88rem;font-weight:600;'>📌 지문 주제: {topic}</span>"
            f"</div>",
            unsafe_allow_html=True
        )

    # 타입별 색상
    type_colors = {
        "배경지식": ("#fef3c7", "#92400e", "🌍"),
        "어휘학습":  ("#dcfce7", "#166534", "📝"),
        "독해전략": ("#ede9fe", "#5b21b6", "🔍"),
        "수능영어": ("#fee2e2", "#991b1b", "🎯"),
    }

    videos = recs.get("videos", [])
    cols = st.columns(2)
    for i, vid in enumerate(videos):
        vtype  = vid.get("type", "배경지식")
        bg, fg, icon = type_colors.get(vtype, ("#f1f5f9", "#334155", "▶"))
        lang_badge = "🇰🇷" if vid.get("lang") == "한국어" else "🇺🇸"
        query = vid.get("search_query", "")
        yt_url = "https://www.youtube.com/results?search_query=" + query.replace(" ", "+")

        card_html = f"""
<div style="
    background:{bg};
    border-radius:12px;
    padding:18px;
    margin-bottom:4px;
    height:100%;
    border:1px solid {bg};
    transition:box-shadow 0.2s;
">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
    <span style="background:{fg};color:white;border-radius:12px;
        padding:2px 10px;font-size:0.75rem;font-weight:600;">
      {icon} {vtype}
    </span>
    <span style="font-size:1rem;">{lang_badge}</span>
  </div>
  <div style="font-weight:700;font-size:0.95rem;color:#1e293b;margin-bottom:8px;line-height:1.4;">
    {vid.get("title", "")}
  </div>
  <div style="font-size:0.82rem;color:#475569;line-height:1.6;margin-bottom:12px;">
    {vid.get("description", "")}
  </div>
  <div style="font-size:0.78rem;color:#94a3b8;margin-bottom:10px;">
    🔎 검색어: <code style="background:white;padding:2px 6px;border-radius:4px;">{query}</code>
  </div>
  <a href="{yt_url}" target="_blank" style="
    display:block;text-align:center;
    background:#ff0000;color:white;
    border-radius:8px;padding:8px;
    text-decoration:none;font-size:0.85rem;font-weight:700;
  ">▶ YouTube에서 보기</a>
</div>"""

        with cols[i % 2]:
            st.markdown(card_html, unsafe_allow_html=True)
            st.markdown("&nbsp;")

    # 전체 주제 YouTube 검색 링크
    if topic:
        full_query = (topic + " 영어 공부").replace(" ", "+")
        st.markdown(
            f"<div style='text-align:center;margin-top:8px;'>"
            f"<a href='https://www.youtube.com/results?search_query={full_query}' "
            f"target='_blank' style='color:#4f6ef7;font-size:0.85rem;text-decoration:none;'>"
            f"🔗 '{topic}' 관련 영상 더 보기 →</a></div>",
            unsafe_allow_html=True
        )


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
        "🎧 듣기 (TTS)", "🎬 유튜브 추천", "🔤 단어 퀴즈", "📝 독해 문제", "🔍 문법 문제"
    ])

    with tab1:
        render_tts_player(p['passage'], player_id=p['id'])

    with tab2:
        render_youtube_tab(p)

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

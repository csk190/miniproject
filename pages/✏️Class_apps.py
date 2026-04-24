import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

# ✅ 메인 앱의 사이드바를 완전히 숨기는 CSS
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 Integrated App Dashboard")

tab1, tab2 = st.tabs(["📂 Mini Project", "🌟 Try Best"])

# (이후 iframe 코드는 동일)

# 1. 페이지 설정 (화면을 넓게 사용)
st.set_page_config(page_title="App Hub", layout="wide")

# 2. 메인 타이틀 (필요 없다면 주석 처리 가능)
st.title("🚀 Integrated App Dashboard")

# 3. 탭 구성 (Mini Project와 Try Best 두 가지만 유지)
tab1, tab2 = st.tabs(["📂 Mini Project", "🌟 Try Best"])

# --- Tab 1: Mini Project ---
with tab1:
    # iframe을 통해 외부 앱 임베드 (?embed=true 추가로 리디렉션 최적화)
    components.html(
        f"""
        <iframe src="https://miniproject-djyhkowbsqtoov8yham3m9.streamlit.app/?embed=true" 
                width="100%" height="900px" frameborder="0" scrolling="yes"></iframe>
        """,
        height=900,
    )

# --- Tab 2: Try Best ---
with tab2:
    components.html(
        f"""
        <iframe src="https://trybest.streamlit.app/?embed=true" 
                width="100%" height="900px" frameborder="0" scrolling="yes"></iframe>
        """,
        height=900,
    )

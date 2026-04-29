import streamlit as st
import streamlit.components.v1 as components

# 1. 페이지 설정: 화면을 최대한 넓게 사용
st.set_page_config(layout="wide")

# 2. CSS를 사용하여 메인 앱의 제목 공간과 여백을 강제로 제거
st.markdown("""
    <style>
        /* 메인 앱 상단의 기본 헤더와 여백 숨기기 */
        header {visibility: hidden;}
        .block-container {
            padding-top: 0rem;
            padding-bottom: 0rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        /* 탭 디자인 간격 조정 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# 3. 타이틀 없이 바로 탭 구성 (중복 제목 방지)
tab1, tab2 = st.tabs(["📂 교육자료생성기", "🌟 마음여행학교마블"])

# --- Tab 1: 교육자료생성기 ---
with tab1:
    components.html(
        f"""
        <iframe src="https://ai-32567807273.us-west1.run.app/" 
                width="100%" height="1000px" frameborder="0" scrolling="yes"></iframe>
        """,
        height=1000,
    )

# --- Tab 2: 마음여행학교마블 ---
with tab2:
    components.html(
        f"""
        <iframe src="https://joo.is/%EB%A7%88%EC%9D%8C%EC%97%AC%ED%96%89%EB%A7%88%EB%B8%94" 
                width="100%" height="1000px" frameborder="0" scrolling="yes"></iframe>
        """,
        height=1000,
    )

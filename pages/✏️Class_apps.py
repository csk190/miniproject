import streamlit as st
import streamlit.components.v1 as components

# 1. 페이지 설정 (넓은 화면 모드)
st.set_page_config(page_title="App Hub", layout="wide")

st.title("🚀 External App Hub")
st.info("상단 탭을 클릭하여 두 앱 사이를 전환할 수 있습니다.")

# 2. 탭 구성 (두 개의 앱만 유지)
tab1, tab2 = st.tabs(["📂 Mini Project", "🌟 Try Best"])

# --- Tab 1: Mini Project ---
with tab1:
    st.subheader("🔗 Mini Project App")
    # iframe을 통해 외부 앱 임베드
    components.html(
        f"""
        <iframe src="https://miniproject-djyhkowbsqtoov8yham3m9.streamlit.app/?embed=true" 
                width="100%" height="850px" frameborder="0" scrolling="yes"></iframe>
        """,
        height=850,
    )

# --- Tab 2: Try Best ---
with tab2:
    st.subheader("🔗 Try Best App")
    components.html(
        f"""
        <iframe src="https://trybest.streamlit.app/?embed=true" 
                width="100%" height="850px" frameborder="0" scrolling="yes"></iframe>
        """,
        height=850,
    )

# 사이드바 (선택 사항: 안내 문구)
st.sidebar.markdown("### 💡 안내")
st.sidebar.write("이 페이지는 외부에서 호스팅 중인 두 개의 Streamlit 앱을 하나로 통합한 대시보드입니다.")

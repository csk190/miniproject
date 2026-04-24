import streamlit as st
import streamlit.components.v1 as components

# 페이지 설정
st.set_page_config(page_title="App Hub", layout="wide")

st.title("🚀 외부 앱 통합 대시보드")
st.write("아래 탭을 클릭하여 각 앱을 바로 확인할 수 있습니다.")

# 탭 구성
tab1, tab2 = st.tabs(["Mini Project App", "Try Best App"])

with tab1:
    st.subheader("🔗 Mini Project")
    # iframe을 사용하여 앱 삽입 (높이는 필요에 따라 조절하세요)
    components.iframe("https://miniproject-djyhkowbsqtoov8yham3m9.streamlit.app/", height=800, scrolling=True)

with tab2:
    st.subheader("🔗 Try Best")
    components.iframe("https://trybest.streamlit.app/", height=800, scrolling=True)

# 사이드바 추가 정보 (선택 사항)
with st.sidebar:
    st.info("이 앱은 외부 Streamlit 앱을 iframe으로 연결한 통합 허브입니다.")

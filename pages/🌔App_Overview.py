import streamlit as st
from pathlib import Path

# md 파일이 같은 pages/ 폴더 안에 있는 경우
md_path = Path(__file__).parent / "App_Overview.md"

# md 파일이 루트(miniproject/)에 있는 경우
# md_path = Path(__file__).parent.parent / "App_Overview.md"

st.markdown(md_path.read_text(encoding="utf-8"), unsafe_allow_html=True)

import streamlit as st
from pathlib import Path

# 현재 파일 기준으로 경로 계산 (가장 안전)
ROOT = Path(__file__).parent.parent  # pages/ → 루트로 이동
md_path = ROOT / "App_Overview.md"

st.markdown(md_path.read_text(encoding="utf-8"), unsafe_allow_html=True)

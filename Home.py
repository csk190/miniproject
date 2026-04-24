mport streamlit as st

# url = "https://github.com/MK316/Applied-linguistics/blob/main/images/AL-bg1.png"

st.markdown("#### Spring 2026")
st.caption("This page is continuously updated.")

IMAGE_URL = "https://raw.githubusercontent.com/MK316/Applied-linguistics/main/images/AL-bg1.png"

st.image(
    IMAGE_URL,
    use_container_width=True
)

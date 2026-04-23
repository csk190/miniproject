import streamlit as st
import json
import re
import os

# 1. 데이터 로드 (@st.cache_data를 쓰면 앱이 빨라집니다)
@st.cache_data
def load_passages():
    file_path = "data/passages.json"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# 2. 세션 상태(Session State) 초기화 - 화면 이동을 위해 필수!
def init_session_state():
    if 'completed' not in st.session_state:
        st.session_state.completed = [] # 처음엔 완료된 지문 없음
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'list' # 시작 화면은 'list'
    if 'selected_id' not in st.session_state:
        st.session_state.selected_id = None # 선택된 지문 ID

# 3. [상세 화면] 지문 학습 페이지
def show_detail_page(passages):
    passage_id = st.session_state.selected_id
    # 선택된 ID에 해당하는 지문 데이터 찾기
    passage = next((p for p in passages if p["id"] == passage_id), None)
    
    if not passage:
        st.error("지문을 찾을 수 없습니다.")
        if st.button("목록으로 돌아가기"):
            st.session_state.current_page = 'list'
            st.rerun()
        return

    # 상단 헤더
    st.caption(f"EBS 수능특강 · {passage.get('category', '카테고리 없음')}")
    st.subheader(f"지문 #{passage['id']}")
    st.divider()
    
    # 지문 내용 출력
    st.markdown("### 📖 지문")
    # 원본 텍스트의 줄바꿈을 유지하기 위해 st.info 대신 st.markdown 창 사용
    st.markdown(f"```text\n{passage.get('passage', '내용이 없습니다.')}\n```")
    
    st.write("") # 여백
    
    # 탭(Tab)을 사용하여 어휘, 문제, 문법을 깔끔하게 분리해서 보여주기
    tab1, tab2, tab3 = st.tabs(["📝 어휘", "🎯 문제", "🔍 문법"])
    
    with tab1:
        st.markdown(f"```text\n{passage.get('vocabulary', '어휘 정보가 없습니다.')}\n```")
    with tab2:
        st.markdown(f"```text\n{passage.get('question', '문제 정보가 없습니다.')}\n```")
    with tab3:
        st.markdown(f"```text\n{passage.get('grammar', '문법 정보가 없습니다.')}\n```")

    st.divider()
    
    # 하단 내비게이션 버튼
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ 목록으로", use_container_width=True):
            st.session_state.current_page = 'list'
            st.rerun() # 화면 새로고침
            
    with col2:
        is_completed = passage_id in st.session_state.completed
        if is_completed:
            # 이미 완료한 경우 취소 버튼
            if st.button("✅ 학습 완료됨 (취소하기)", use_container_width=True):
                st.session_state.completed.remove(passage_id)
                st.session_state.current_page = 'list'
                st.rerun()
        else:
            # 학습 완료 버튼
            if st.button("🎉 학습 완료!", type="primary", use_container_width=True):
                st.session_state.completed.append(passage_id)
                st.session_state.current_page = 'list'
                st.rerun()

# 4. [메인 화면] 지문 목록 페이지
def show_list_page(passages):
    completed = st.session_state.completed
    total_passages = len(passages)
    done_passages = len(completed)

    with st.container():
        st.caption("EBS 수능특강 · 소재편")
        st.header("오늘은 어떤 지문을 읽어볼까요?")
        st.write(f"완료 {done_passages} / {total_passages} · 한 번에 한 지문씩 천천히")
    
    st.divider()

    for p in passages:
        p_id = p["id"]
        is_done = p_id in completed
        
        # 미리보기는 정규식으로 줄바꿈 제거 후 90자까지만
        preview_text = p.get("passage", "")
        preview = re.sub(r'\s+', ' ', preview_text).strip()[:90]

        col1, col2, col3 = st.columns([1, 8, 2])
        
        with col1:
            if is_done:
                st.success("✔")
            else:
                st.info(str(p_id))
                
        with col2:
            st.markdown(f"**{p.get('category', '카테고리 없음')}**")
            st.caption(f"{preview}…")
            
        with col3:
            # 버튼 클릭 시 현재 페이지를 'detail'로 바꾸고 선택된 ID를 저장
            if st.button("학습하기", key=f"btn_{p_id}", use_container_width=True):
                st.session_state.current_page = 'detail'
                st.session_state.selected_id = p_id
                st.rerun() # 화면 새로고침하여 상세 페이지 렌더링
        
        st.write("")

# 메인 실행 함수
def main():
    st.set_page_config(page_title="수능특강 영어 소재편 학습", page_icon="📚")
    
    init_session_state()
    passages = load_passages()

    # 현재 상태(current_page)에 따라 다른 화면을 그려줍니다.
    if st.session_state.current_page == 'list':
        show_list_page(passages)
    elif st.session_state.current_page == 'detail':
        show_detail_page(passages)

if __name__ == "__main__":
    main()

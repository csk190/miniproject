import streamlit as st
import json
import re
import os

# 1. 데이터 로드 (passages.json 모방)
def load_passages():
    # 실제 환경에서는 file path를 'data/passages.json'으로 설정하세요.
    file_path = "data/passages.json"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # 파일이 없을 경우를 대비한 더미 데이터
        return [
            {"id": 1, "category": "인문", "passage": "This is the first passage about humanities..."},
            {"id": 2, "category": "과학", "passage": "Science is a rigorous, systematic endeavor that builds..."},
        ]

# 2. 로컬 스토리지 모방 (Streamlit 세션 상태 사용)
def get_completed():
    # React의 getCompleted() 역할을 세션 상태로 대체
    if 'completed' not in st.session_state:
        st.session_state.completed = [1] # 예시로 1번은 완료된 상태로 설정
    return st.session_state.completed

def main():
    # React의 document.title = "..." 부분
    st.set_page_config(page_title="수능특강 영어 소재편 학습", page_icon="📚")

    passages = load_passages()
    completed = get_completed()

    # useMemo로 계산하던 stats
    total_passages = len(passages)
    done_passages = len(completed)

    # 헤더 섹션 렌더링 (Section -> Container)
    with st.container():
        st.caption("EBS 수능특강 · 소재편")
        st.header("오늘은 어떤 지문을 읽어볼까요?")
        st.write(f"완료 {done_passages} / {total_passages} · 한 번에 한 지문씩 천천히")
    
    st.divider()

    # 리스트 렌더링 (ul > li -> Loop)
    for p in passages:
        p_id = p["id"]
        is_done = p_id in completed
        
        # 정규식을 이용해 연속된 공백 제거 및 90자 자르기 (React 코드와 동일)
        preview = re.sub(r'\s+', ' ', p["passage"]).strip()[:90]

        # UI 카드 레이아웃 구성
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
            # React의 <Link> 컴포넌트를 버튼으로 대체
            if st.button("학습하기", key=f"btn_{p_id}", use_container_width=True):
                # 실제 라우팅이 필요하다면 st.query_params 등을 활용해야 합니다.
                st.toast(f"{p_id}번 지문 학습 페이지로 이동합니다!")
        
        st.write("") # 간격 띄우기

if __name__ == "__main__":
    main()

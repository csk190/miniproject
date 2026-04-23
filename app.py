import streamlit as st
import json
import re
import os

# 1. 데이터 로드 (캐싱 적용)
@st.cache_data
def load_passages():
    import glob
    import csv

    passages = []
    pid = 1

    # data/ 폴더의 모든 CSV 파일 읽기
    csv_files = sorted(glob.glob("data/*.csv"))

    for file_path in csv_files:
        # 파일명에서 카테고리 추출 (확장자 제거)
        category = os.path.basename(file_path).replace(".csv", "")

        with open(file_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter="\t")  # 탭 구분자
            for row in reader:
                if not row.get("지문", "").strip():
                    continue  # 빈 행 건너뜀
                passages.append({
                    "id": pid,
                    "category": category,
                    "passage":    row.get("지문", "").strip(),
                    "vocabulary": row.get("어휘", "").strip(),
                    "question":   row.get("문제", "").strip(),
                    "grammar":    row.get("문법", "").strip(),
                })
                pid += 1

    return passages

# 2. 상태 관리 초기화
def init_state():
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'list'
    if 'selected_id' not in st.session_state:
        st.session_state.selected_id = None
    if 'completed' not in st.session_state:
        st.session_state.completed = []
    # 선택된 카테고리 상태 추가
    if 'selected_category' not in st.session_state:
        st.session_state.selected_category = "전체"

# 3. 상세 페이지 (지문 학습)
def show_detail(passages):
    p = next((x for x in passages if x["id"] == st.session_state.selected_id), None)
    if not p:
        st.session_state.current_page = 'list'
        st.rerun()

    st.button("⬅️ 목록으로 돌아가기", on_click=lambda: setattr(st.session_state, 'current_page', 'list'))
    
    st.title(f"지문 #{p['id']}")
    st.caption(f"카테고리: {p['category']}")
    
    st.info(p['passage'])
    
    t1, t2, t3 = st.tabs(["단어장", "문제 확인", "구문 분석"])
    with t1: st.text(p.get('vocabulary', '데이터 없음'))
    with t2: st.text(p.get('question', '데이터 없음'))
    with t3: st.text(p.get('grammar', '데이터 없음'))

# 4. 목록 페이지 (필터 기능 포함)
def show_list(passages):
    st.title("📚 수능특강 소재편 학습")
    
    # 카테고리 선택 필터 (사이드바 또는 상단)
    categories = ["전체"] + sorted(list(set(p['category'] for p in passages)))
    selected = st.selectbox("공부하고 싶은 소재를 선택하세요:", categories, index=categories.index(st.session_state.selected_category))
    st.session_state.selected_category = selected

    # 데이터 필터링
    filtered = passages if selected == "전체" else [p for p in passages if p['category'] == selected]
    
    st.write(f"총 {len(filtered)}개의 지문이 있습니다.")
    st.divider()

    for p in filtered:
        col1, col2 = st.columns([4, 1])
        with col1:
            done = "✅" if p['id'] in st.session_state.completed else "📄"
            st.markdown(f"**[{p['category']}]** 지문 {p['id']}")
            preview = p['passage'][:60] + "..."
            st.caption(preview)
        with col2:
            # 버튼 클릭 시 상태 변경 및 리런
            if st.button("학습하기", key=f"go_{p['id']}", use_container_width=True):
                st.session_state.selected_id = p['id']
                st.session_state.current_page = 'detail'
                st.rerun()
        st.divider()

def main():
    init_state()
    data = load_passages()

    if not data:
        st.error("data/ 폴더에서 CSV 파일을 찾을 수 없습니다.")  # ← 메시지 수정
        return
    ...

    if st.session_state.current_page == 'list':
        show_list(data)
    else:
        show_detail(data)

if __name__ == "__main__":
    main()

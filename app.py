import streamlit as st
import pandas as pd
from sqlalchemy import text
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="Library Pro Dashboard", page_icon="✨", layout="wide")

# 디자인 보정 CSS
st.markdown("""
    <style>
    /* 모든 메트릭 카드의 컨테이너 선택 */
    [data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.8) !important;
        border-radius: 12px !important;
        padding: 15px 20px !important;
        border: 1px solid #e0e0e0 !important;
        
        /* 높이 고정 및 중앙 정렬 핵심 설정 */
        min-height: 150px !important; 
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
    }
    
    /* 메트릭 내부의 라벨(제목) 스타일 */
    [data-testid="stMetricLabel"] {
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: #555 !important;
    }

    /* 메트릭 내부의 값(숫자) 스타일 */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. DB 연결 함수
conn = st.connection("supabase", type="sql")

def get_data():
    return conn.query("SELECT * FROM books ORDER BY id DESC", ttl=0)

def run_query(query, params=None):
    with conn.session as s:
        s.execute(text(query), params)
        s.commit()

# --- 도서 수정 팝업 함수 (Streamlit 최신 기능: dialog) ---
@st.dialog("도서 정보 수정")
def edit_book_dialog(book):
    st.write(f"ID: {book['id']}번 도서를 수정합니다.")
    new_title = st.text_input("도서명", value=book['title'])
    new_author = st.text_input("저자", value=book['author'])
    new_status = st.selectbox("상태", ["대출가능", "대출중", "분실"], 
                               index=["대출가능", "대출중", "분실"].index(book['status']))
    
    if st.button("수정 내용 저장", use_container_width=True):
        query = "UPDATE books SET title = :t, author = :a, status = :s, updated_at = NOW() WHERE id = :id"
        run_query(query, {"t": new_title, "a": new_author, "s": new_status, "id": book['id']})
        st.success("수정되었습니다!")
        st.rerun()

# --- 데이터 로드 ---
df = get_data()

# --- 사이드바 네비게이션 ---
with st.sidebar:
    st.title("📚 Library Admin")
    menu = st.radio("Menu", ["📊 Dashboard", "📚 Inventory Management", "➕ Quick Register"])
    st.divider()
    st.caption(f"Last Sync: {datetime.now().strftime('%H:%M:%S')}")

# --- 1. Dashboard (상단 카드 높이 통일 버전) ---
if menu == "📊 Dashboard":
    st.title("BOOK Dashboard")
    
    # 상단 4개 카드 (CSS로 min-height를 설정하여 높이 통일)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Books", f"{len(df)}권")
    m2.metric("On Loan", f"{len(df[df['status'] == '대출중'])}권", delta="Checking...")
    m3.metric("Available", f"{len(df[df['status'] == '대출가능'])}권")
    m4.metric("Issues", f"{len(df[df['status'] == '분실'])}건", delta="- Critical", delta_color="inverse")

    st.divider()
    
    col_chart, col_recent = st.columns([2, 1])
    with col_chart:
        st.subheader("Rental Status Distribution")
        st.bar_chart(df['status'].value_counts(), color="#4A90E2")
    with col_recent:
        st.subheader("Latest Arrivals")
        st.table(df[['title', 'author']].head(5))

# --- 2. Inventory Management (전체 수정 기능 추가) ---
elif menu == "📚 Inventory Management":
    st.title("Inventory Management")
    
    search = st.text_input("🔍 도서명 또는 저자로 검색", placeholder="검색어를 입력하고 엔터를 누르세요.")
    
    filtered_df = df.copy()
    if search:
        filtered_df = filtered_df[filtered_df['title'].str.contains(search, case=False) | 
                                  filtered_df['author'].str.contains(search, case=False)]

    for _, row in filtered_df.iterrows():
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                st.markdown(f"**{row['title']}**")
                st.caption(f"Author: {row['author']} | Status: {row['status']}")
            with c2:
                # 수정 버튼: 클릭 시 다이얼로그(팝업) 실행
                if st.button("📝 수정", key=f"edit_{row['id']}", use_container_width=True):
                    edit_book_dialog(row)
            with c3:
                # 삭제 버튼
                if st.button("🗑️ 삭제", key=f"del_{row['id']}", use_container_width=True):
                    run_query("DELETE FROM books WHERE id = :id", {"id": row['id']})
                    st.rerun()

# --- 3. Quick Register ---
elif menu == "➕ Quick Register":
    st.title("Add New Resource")
    with st.form("reg_form", clear_on_submit=True):
        t = st.text_input("Title *")
        a = st.text_input("Author")
        s = st.selectbox("Status", ["대출가능", "대출중"])
        if st.form_submit_button("Register Book", use_container_width=True):
            if t:
                run_query("INSERT INTO books (title, author, status) VALUES (:t, :a, :s)", 
                          {"t": t, "a": a, "s": s})
                st.success("새 도서가 등록되었습니다.")
            else:
                st.error("도서 제목은 필수입니다.")

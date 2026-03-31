import streamlit as st
import pandas as pd
from sqlalchemy import text

st.set_page_config(page_title="도서 관리 시스템", layout="wide")
st.title("📚 도서 대여 관리 시스템 (CRUD)")

# 1. DB 연결
conn = st.connection("supabase", type="sql")

# --- 헬퍼 함수 정의 ---
def get_all_books():
    """R: 모든 도서 조회"""
    return conn.query("SELECT * FROM books ORDER BY id DESC;", ttl=0)

def add_book(title, author):
    """C: 도서 추가"""
    with conn.session as s:
        s.execute(
            text("INSERT INTO books (title, author) VALUES (:t, :a);"),
            {"t": title, "a": author}
        )
        s.commit()

def update_status(book_id, new_status):
    """U: 대출 상태 변경"""
    with conn.session as s:
        s.execute(
            text("UPDATE books SET status = :s, updated_at = NOW() WHERE id = :id;"),
            {"s": new_status, "id": book_id}
        )
        s.commit()

def delete_book(book_id):
    """D: 도서 삭제"""
    with conn.session as s:
        s.execute(text("DELETE FROM books WHERE id = :id;"), {"id": book_id})
        s.commit()

# --- 화면 구성 ---

# 사이드바: 도서 추가 (Create)
with st.sidebar:
    st.header("➕ 새 도서 등록")
    with st.form("add_form", clear_on_submit=True):
        new_title = st.text_input("도서 제목")
        new_author = st.text_input("저자")
        if st.form_submit_button("등록하기"):
            if new_title:
                add_book(new_title, new_author)
                st.success(f"'{new_title}' 등록 완료!")
                st.rerun()
            else:
                st.error("제목을 입력해주세요.")

# 메인 화면: 도서 목록 조회 (Read)
books_df = get_all_books()

if not books_df.empty:
    st.subheader("📖 전체 도서 목록")
    
    # 가독성을 위해 컬럼 배치
    for index, row in books_df.iterrows():
        with st.expander(f"[{row['status']}] {row['title']} - {row['author']}"):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**ID:** {row['id']}")
                st.write(f"**마지막 업데이트:** {row['updated_at']}")
            
            with col2:
                # 상태 수정 (Update)
                new_stat = st.selectbox(
                    "상태 변경", 
                    ["대출가능", "대출중", "분실"], 
                    index=["대출가능", "대출중", "분실"].index(row['status']),
                    key=f"stat_{row['id']}"
                )
                if st.button("상태 저장", key=f"btn_u_{row['id']}"):
                    update_status(row['id'], new_stat)
                    st.rerun()
            
            with col3:
                # 삭제 (Delete)
                st.write("---")
                if st.button("🗑️ 삭제", key=f"btn_d_{row['id']}", help="삭제 시 복구 불가"):
                    delete_book(row['id'])
                    st.warning("도서가 삭제되었습니다.")
                    st.rerun()
else:
    st.info("등록된 도서가 없습니다. 사이드바에서 등록해 주세요.")

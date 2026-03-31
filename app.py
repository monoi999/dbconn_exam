import streamlit as st
import pandas as pd
from sqlalchemy import text
from datetime import datetime

# 1. 페이지 설정 및 디자인 테마 적용
st.set_page_config(page_title="Library Dashboard", page_icon="✨", layout="wide")

# 고해상도 디자인을 위한 커스텀 CSS (최신 트렌드 반영)
st.markdown("""
    <style>
    /* 전체 배경 및 폰트 */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        font-family: 'Pretendard', -apple-system, sans-serif;
    }
    
    /* 카드 스타일 (글래스모피즘 느낌) */
    div[data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.8);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }

    /* 버튼 스타일 커스텀 */
    .stButton>button {
        border-radius: 8px;
        transition: all 0.3s ease;
        border: none;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }

    /* 상태별 배지 스타일 */
    .status-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .status-available { background-color: #e1f5fe; color: #01579b; }
    .status-rented { background-color: #fff3e0; color: #e65100; }
    .status-lost { background-color: #ffebee; color: #b71c1c; }
    </style>
    """, unsafe_allow_html=True)

# 2. DB 연결 및 데이터 함수
conn = st.connection("supabase", type="sql")

def get_data():
    return conn.query("SELECT * FROM books ORDER BY id DESC", ttl=0)

def run_query(query, params=None):
    with conn.session as s:
        s.execute(text(query), params)
        s.commit()

# --- 사이드바 네비게이션 ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3389/3389081.png", width=100)
    st.title("Library Admin")
    st.markdown("---")
    menu = st.radio("Menu", ["📊 Dashboard", "📚 Book Inventory", "➕ Register New"])
    st.markdown("---")
    st.caption("v2.1.0 Beta - Updated 2026")

df = get_data()

# --- 1. Dashboard (메인 지표 및 통계) ---
if menu == "📊 Dashboard":
    st.title("System Overview")
    
    # 상단 지표 카드
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Books", len(df))
    m2.metric("Rented", len(df[df['status'] == '대출중']), delta="Check-out")
    m3.metric("Available", len(df[df['status'] == '대출가능']), delta_color="normal")
    m4.metric("Issues", len(df[df['status'] == '분실']), delta="- Alert")

    st.markdown("### 📈 Rental Insights")
    c1, c2 = st.columns([2, 1])
    with c1:
        # 간단한 막대 그래프 (상태별)
        st.bar_chart(df['status'].value_counts(), color="#4A90E2")
    with c2:
        # 도넛 차트 느낌의 원형 그래프
        st.write("Status Proportion")
        st.scatter_chart(df['status'].value_counts()) # 최신 Streamlit은 scatter_chart로도 시각화 가능

# --- 2. Book Inventory (목록 및 관리) ---
elif menu == "📚 Book Inventory":
    st.title("Book Inventory")
    
    # 상단 검색 및 필터 바
    search_col, filter_col = st.columns([3, 1])
    with search_col:
        search = st.text_input("", placeholder="Search by title or author...", label_visibility="collapsed")
    with filter_col:
        f_status = st.selectbox("Status Filter", ["All", "대출가능", "대출중", "분실"], label_visibility="collapsed")

    filtered_df = df.copy()
    if search:
        filtered_df = filtered_df[filtered_df['title'].str.contains(search, case=False) | filtered_df['author'].str.contains(search, case=False)]
    if f_status != "All":
        filtered_df = filtered_df[filtered_df['status'] == f_status]

    # 목록 UI (Clean Card Style)
    for _, row in filtered_df.iterrows():
        # 상태에 따른 색상 클래스 결정
        status_class = "status-available" if row['status'] == '대출가능' else "status-rented" if row['status'] == '대출중' else "status-lost"
        
        with st.container(border=True):
            col_info, col_action = st.columns([4, 1])
            with col_info:
                st.markdown(f"""
                    <span class="status-badge {status_class}">{row['status']}</span>
                    <h3 style='margin-top: 10px;'>{row['title']}</h3>
                    <p style='color: #666;'>저자: {row['author']} | 등록 ID: {row['id']}</p>
                """, unsafe_allow_html=True)
            
            with col_action:
                new_s = st.selectbox("Update Status", ["대출가능", "대출중", "분실"], 
                                   index=["대출가능", "대출중", "분실"].index(row['status']), 
                                   key=f"s_{row['id']}")
                if new_s != row['status']:
                    run_query("UPDATE books SET status = :s WHERE id = :id", {"s": new_s, "id": row['id']})
                    st.rerun()
                
                if st.button("Delete", key=f"d_{row['id']}", use_container_width=True):
                    run_query("DELETE FROM books WHERE id = :id", {"id": row['id']})
                    st.rerun()

# --- 3. Register New (등록 양식) ---
elif menu == "➕ Register New":
    st.title("Register New Book")
    with st.container(border=True):
        st.subheader("Book Details")
        with st.form("add_form", border=False):
            t = st.text_input("Title", placeholder="Enter book title")
            a = st.text_input("Author", placeholder="Enter author name")
            col_l, col_r = st.columns(2)
            with col_l:
                s = st.selectbox("Initial Status", ["대출가능", "대출중"])
            with col_r:
                st.write("") # 간격 맞춤용
            
            submitted = st.form_submit_button("Confirm Registration", use_container_width=True)
            if submitted:
                if t:
                    run_query("INSERT INTO books (title, author, status) VALUES (:t, :a, :s)", 
                              {"t": t, "a": a, "s": s})
                    st.success(f"Successfully registered: {t}")
                else:
                    st.error("Title is required.")

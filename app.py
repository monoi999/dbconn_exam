import streamlit as st

# 페이지 설정
st.set_page_config(page_title="SQL DB 대시보드", page_icon="💾")

st.title("💾 실시간 SQL 데이터베이스 연동")
st.markdown("Supabase(PostgreSQL)와 직접 통신하는 배포용 앱입니다.")

# 1. DB 연결 (SQLAlchemy 기반 st.connection)
conn = st.connection("supabase", type="sql")

# --- 데이터 입력 섹션 ---
with st.form("log_form", clear_on_submit=True):
    st.subheader("📝 새 로그 기록하기")
    name = st.text_input("작성자")
    content = st.text_area("내용")
    submit = st.form_submit_button("DB에 저장")

    if submit:
        if name and content:
            with conn.session as session:
                # SQLAlchemy 문법을 사용하여 데이터 삽입
                session.execute(
                    "INSERT INTO user_logs (user_name, note) VALUES (:name, :note);",
                    params=dict(name=name, note=content)
                )
                session.commit()
            st.success("데이터가 성공적으로 저장되었습니다!")
            st.cache_data.clear() # 새 데이터를 보여주기 위해 캐시 삭제
        else:
            st.error("모든 항목을 입력해주세요.")

st.divider()

# --- 데이터 조회 섹션 ---
st.subheader("📋 전체 로그 현황")

# ttl=0으로 설정하면 매번 최신 데이터를 가져옵니다. 
# 배포 시 성능을 위해 ttl=60 (1분) 정도로 설정하는 것을 추천합니다.
df = conn.query("SELECT created_at, user_name, note FROM user_logs ORDER BY created_at DESC;", ttl=10)

if not df.empty:
    st.dataframe(
        df, 
        use_container_width=True,
        column_config={
            "created_at": "작성 시간",
            "user_name": "작성자",
            "note": "메모 내용"
        }
    )
else:
    st.info("아직 기록된 데이터가 없습니다.")

# 새로고침 버튼
if st.button("🔄 새로고침"):
    st.rerun()

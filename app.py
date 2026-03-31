import streamlit as st
from sqlalchemy import text

# 페이지 설정
st.set_page_config(page_title="SQL DB 대시보드", page_icon="🗄️")

st.title("🗄️ Supabase SQL 연동 실전 앱")
st.markdown("SQLAlchemy와 st.connection을 이용한 실시간 DB 연동입니다.")

# 1. DB 연결 (Secrets에 설정된 'supabase' 설정을 가져옴)
# 배포 시 Streamlit Cloud Secrets에 [connections.supabase] 항목이 있어야 합니다.
conn = st.connection("supabase", type="sql")

# 2. 테이블 생성 및 초기 데이터 (테이블이 없을 경우 대비)
with conn.session as session:
    session.execute(text("""
        CREATE TABLE IF NOT EXISTS inventory (
            id SERIAL PRIMARY KEY,
            item_name TEXT NOT NULL,
            quantity INTEGER,
            category TEXT
        );
    """))
    session.commit()

# 3. 데이터 입력 기능 (Sidebar)
with st.sidebar:
    st.header("➕ 새 항목 추가")
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("품목명")
        qty = st.number_input("수량", min_value=0, step=1)
        cat = st.selectbox("카테고리", ["전자제품", "가구", "생필품", "기타"])
        submit = st.form_submit_button("DB에 저장")
        
        if submit and name:
            with conn.session as session:
                session.execute(
                    text("INSERT INTO inventory (item_name, quantity, category) VALUES (:name, :qty, :cat)"),
                    {"name": name, "qty": qty, "cat": cat}
                )
                session.commit()
            st.success(f"'{name}' 추가 완료!")
            st.cache_data.clear() # 데이터 갱신을 위해 캐시 삭제

# 4. 데이터 조회 및 출력
st.subheader("📦 현재 재고 현황")

# 쿼리 실행 (ttl=0으로 설정하면 매번 실시간으로 가져옵니다)
df = conn.query("SELECT * FROM inventory ORDER BY id DESC", ttl=0)

if not df.empty:
    # 데이터프레임 시각화
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # 간단한 분석 지표
    col1, col2 = st.columns(2)
    col1.metric("총 품목 종류", len(df))
    col2.metric("총 재고 수량", int(df['quantity'].sum()))
else:
    st.info("현재 등록된 재고가 없습니다. 사이드바에서 추가해 보세요!")

# 5. 데이터 삭제 기능 (선택 사항)
if st.checkbox("데이터 삭제 모드 활성화"):
    target_id = st.number_input("삭제할 ID 입력", min_value=1, step=1)아하, **Supabase(PostgreSQL)** 연결에 드디어 성공하셨군요! 고생하신 만큼 보람이 크실 것 같습니다. 구글 시트보다 훨씬 강력하고 전문적인 DB를 갖게 되신 걸 축하드려요.

이제 배포 환경(Streamlit Cloud)에서 실제 데이터셋을 활용해 데이터를 **조회(Select)**하고 **추가(Insert)**하는 실전 코드를 짜보겠습니다. 이번에는 "방문자 방명록" 또는 "업무 로그" 형태의 데이터셋을 가정해 볼게요.

---

### 1. 전제 조건: Supabase 테이블 만들기
배포 전에 Supabase 대시보드의 **SQL Editor**에서 아래 코드를 실행해 테이블을 먼저 만들어주세요.

```sql
CREATE TABLE IF NOT EXISTS user_logs (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_name TEXT,
    note TEXT
);

-- 샘플 데이터 삽입
INSERT INTO user_logs (user_name, note) VALUES ('관리자', 'DB 연동 테스트 성공!');

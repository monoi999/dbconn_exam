import streamlit as st

# 1. DB 연결 (Secrets에 설정된 정보를 자동으로 가져옴)
conn = st.connection("supabase", type="sql")

st.title("Supabase 연동 앱")

# 2. 데이터 입력 (테이블이 없다면 생성하고 데이터 삽입)
if st.button("사용자 추가하기"):
    with conn.session as session:
        session.execute("CREATE TABLE IF NOT EXISTS users (name text, age int);")
        session.execute("INSERT INTO users (name, age) VALUES ('홍길동', 30);")
        session.commit()
    st.success("데이터가 Supabase에 저장되었습니다!")

# 3. 데이터 조회 (쿼리 실행)
# ttl은 캐시 시간입니다 (10분 동안 동일 쿼리는 DB에 다시 묻지 않음)
df = conn.query("SELECT * FROM users;", ttl=600)

st.write("실시간 DB 데이터:")
st.dataframe(df)
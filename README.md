# 도서 대여 관리 프로젝트
### Streamlit에서 DB(Supabase)와 SQLAlchemy를 이용해 연동

### 로컬에서 연동 테스트 위한 단계
1. Supabase에서 DB 만들기
- 회원가입하고 비번을 자동생성으로 받아 백업해 둘것, 지역(Region)은 가급적 Seoul (ap-northeast-2)을 선택
- DB 만들기 : 여러번 에러 중엣 Transaction pooler로 바꿔 연결 시도해보니 정상적으로 연결 
    - new project / 상단 connection 클릭 / Direct 탭 / Transaction pooler 선택 / URI 선택 / 
    - Connection string 복사 : postgresql://postgres.eqstebepyquzezdqbxbt:[YOUR-PASSWORD]@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres

2. Streamlit Cloud에 비밀번호 설정하기 (중요!) ==> 추후 cloud에 배포할 경우 필요 지금은 스킵
- DB 주소와 비밀번호를 코드에 직접 쓰면 해킹 위험이 있습니다. 그래서 Streamlit의 Secrets 기능을 사용

    <pre>
    [connections.supabase]
    url = "postgresql://postgres.eqstebepyquzezdqbxbt:HhwDpRmL3IPOJhef@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres"
    type = "sql"   
    </pre>

3. vscode에서 다음과 같은 폴더와 파일에 app.py와 secrets.toml 파일 작성 
    <pre>
    내_프로젝트_폴더/
    ├── .streamlit/          <-- 폴더 이름 앞에 마침표(.)가 있어야 함
    │   └── secrets.toml     <-- 파일 이름 확인
    └── app.py
    </pre>     

4. streamlit run app.py 실행

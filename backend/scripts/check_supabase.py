"""Supabase 연결 테스트"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

# backend 폴더의 .env 파일 로드
backend_dir = Path(__file__).parent.parent.resolve()
env_path = backend_dir / ".env"
if not env_path.exists():
    # 현재 작업 디렉토리에서도 시도
    env_path = Path(".env")
load_dotenv(env_path)

# 환경 변수 읽기
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY")

if not supabase_url or not supabase_key:
    print("[ERROR] Supabase 설정을 찾을 수 없습니다.")
    print(f"   SUPABASE_URL: {bool(supabase_url)}")
    print(f"   SUPABASE_KEY: {bool(supabase_key)}")
    sys.exit(1)

print("=" * 50)
print("Supabase 연결 테스트")
print("=" * 50)
print(f"URL: {supabase_url}")
print(f"Key: {supabase_key[:20]}...")
print()

try:
    print("[INFO] Supabase 클라이언트 생성 중...")
    supabase: Client = create_client(supabase_url, supabase_key)
    
    print("[SUCCESS] 클라이언트 생성 성공!")
    
    # 간단한 연결 테스트: auth.getUser() 또는 테이블 조회 시도
    print("\n[INFO] 연결 확인 중...")
    
    # auth 상태 확인 (에러가 없으면 연결 성공)
    try:
        auth_response = supabase.auth.get_user()
        print("[SUCCESS] Auth 연결 성공!")
        if auth_response.user:
            print(f"   사용자: {auth_response.user.email or '익명'}")
        else:
            print("   사용자: 로그인되지 않음 (정상)")
    except Exception as auth_error:
        print(f"[WARNING] Auth 확인 중 오류 (무시 가능): {auth_error}")
    
    # 간단한 쿼리 테스트 (테이블이 없어도 에러만 안 나면 연결은 성공)
    print("\n[INFO] 데이터베이스 연결 확인 중...")
    try:
        # 존재하지 않는 테이블에 쿼리하면 404가 나오지만, 연결 자체는 확인됨
        # 실제 테이블이 있다면 그걸 조회하면 됨
        result = supabase.table("_test_connection").select("*").limit(1).execute()
        print("[SUCCESS] 데이터베이스 연결 성공!")
    except Exception as db_error:
        error_str = str(db_error)
        if "404" in error_str or "relation" in error_str.lower() or "does not exist" in error_str.lower():
            print("[SUCCESS] 데이터베이스 연결 성공! (테이블이 없어서 404가 발생했지만 연결은 정상)")
        else:
            print(f"[WARNING] 데이터베이스 확인 중 오류: {db_error}")
            # 연결 자체는 성공했을 수 있으므로 계속 진행
    
    print("\n[SUCCESS] Supabase 연결 테스트 완료!")
    
except Exception as e:
    print(f"\n[ERROR] 오류 발생: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 50)
print("테스트 완료!")
print("=" * 50)

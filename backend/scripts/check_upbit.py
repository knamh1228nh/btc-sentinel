"""업비트 계정 KRW 잔고 조회 테스트"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import ccxt

# backend 폴더의 .env 파일 로드
backend_dir = Path(__file__).parent.parent.resolve()
env_path = backend_dir / ".env"
if not env_path.exists():
    # 현재 작업 디렉토리에서도 시도
    env_path = Path(".env")
load_dotenv(env_path)

# 환경 변수 읽기 (UPBIT_OPEN_API_ACCESS_KEY 또는 UPBIT_ACCESS_KEY)
access_key = os.getenv("UPBIT_OPEN_API_ACCESS_KEY") or os.getenv("UPBIT_ACCESS_KEY")
secret_key = os.getenv("UPBIT_OPEN_API_SECRET_KEY") or os.getenv("UPBIT_SECRET_KEY")

if not access_key or not secret_key:
    print("[ERROR] 업비트 API 키를 찾을 수 없습니다.")
    print(f"   확인된 키: UPBIT_OPEN_API_ACCESS_KEY={bool(os.getenv('UPBIT_OPEN_API_ACCESS_KEY'))}")
    print(f"   확인된 키: UPBIT_ACCESS_KEY={bool(os.getenv('UPBIT_ACCESS_KEY'))}")
    sys.exit(1)

print("=" * 50)
print("업비트 계정 KRW 잔고 조회 테스트")
print("=" * 50)
print(f"Access Key: {access_key[:10]}...")
print(f"Secret Key: {'*' * 20}")
print()

try:
    # ccxt를 사용한 업비트 연결
    exchange = ccxt.upbit({
        'apiKey': access_key,
        'secret': secret_key,
        'enableRateLimit': True,
    })
    
    print("[INFO] 업비트 API 연결 중...")
    
    # 잔고 조회
    balance = exchange.fetch_balance()
    
    print("\n[SUCCESS] 연결 성공!")
    print("\n[KRW 잔고]")
    if 'KRW' in balance:
        krw_balance = balance['KRW']
        print(f"   총 잔고: {krw_balance.get('total', 0):,.0f} KRW")
        print(f"   사용 가능: {krw_balance.get('free', 0):,.0f} KRW")
        print(f"   사용 중: {krw_balance.get('used', 0):,.0f} KRW")
    else:
        print("   KRW 잔고 정보를 찾을 수 없습니다.")
    
    print("\n[전체 잔고 요약]")
    for currency, amounts in balance.items():
        if isinstance(amounts, dict) and amounts.get('total', 0) > 0:
            print(f"   {currency}: {amounts.get('total', 0):,.8f}")
    
except ccxt.AuthenticationError as e:
    print(f"\n[ERROR] 인증 오류: {e}")
    print("   API 키가 올바른지 확인해주세요.")
    sys.exit(1)
except ccxt.NetworkError as e:
    print(f"\n[ERROR] 네트워크 오류: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n[ERROR] 오류 발생: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 50)
print("테스트 완료!")
print("=" * 50)

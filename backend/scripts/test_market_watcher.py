"""Market Watcher 테스트 스크립트"""
import time
import sys
from pathlib import Path
from dotenv import load_dotenv

# backend 폴더의 .env 파일 로드
backend_dir = Path(__file__).parent.parent.resolve()
env_path = backend_dir / ".env"
if not env_path.exists():
    env_path = Path(".env")
load_dotenv(env_path)

# Python 경로에 backend 폴더 추가
sys.path.insert(0, str(backend_dir))

from app.core.detection.detector import MarketWatcher
from app.utils.logger import logger

def test_market_watcher():
    """Market Watcher 테스트"""
    print("=" * 50)
    print("Market Watcher 테스트")
    print("=" * 50)
    
    watcher = MarketWatcher("KRW-BTC")
    
    try:
        print("[INFO] Market Watcher 시작...")
        watcher.start()
        
        # 30초간 실행
        print("[INFO] 30초간 실행 중... (Ctrl+C로 중지 가능)")
        time.sleep(30)
        
    except KeyboardInterrupt:
        print("\n[INFO] 사용자에 의해 중지됨")
    except Exception as e:
        print(f"\n[ERROR] 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("[INFO] Market Watcher 종료 중...")
        watcher.stop()
        print("[INFO] 테스트 완료!")

if __name__ == "__main__":
    test_market_watcher()

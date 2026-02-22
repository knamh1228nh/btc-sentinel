"""의존성 설치 확인 및 설치 스크립트"""
import subprocess
import sys

def install_package(package):
    """패키지 설치"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"[SUCCESS] {package} 설치 완료")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {package} 설치 실패: {e}")
        return False

def main():
    """필요한 패키지 설치"""
    packages = [
        "pydantic-settings==2.1.0",
        "websocket-client==1.6.4",
        "python-dotenv==1.0.0",
        "supabase==2.0.0",
    ]
    
    print("=" * 50)
    print("의존성 패키지 설치")
    print("=" * 50)
    
    for package in packages:
        print(f"\n[INFO] {package} 설치 중...")
        install_package(package)
    
    print("\n" + "=" * 50)
    print("설치 완료!")
    print("=" * 50)

if __name__ == "__main__":
    main()

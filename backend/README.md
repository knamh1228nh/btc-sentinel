# Mini-Sentinel Backend

FastAPI + System 1(감지) + System 2(Gemini 분석) + Supabase.

## 설치

### 1) 권장: pip·setuptools·wheel 업그레이드 후 설치

`pydantic-core` 메타데이터 생성 실패는 보통 다음 때문에 발생합니다.

- **근본 원인**
  - `pydantic-core`는 **Rust**로 작성되어, 소스에서 설치할 때 Rust/Cargo 빌드가 필요함.
  - 사용 중인 **Python 버전**(예: 3.13)에 맞는 **pre-built wheel**이 없으면 pip가 소스 빌드를 시도하고, 이때 메타데이터 생성 단계에서 실패함.
  - **pip·setuptools·wheel**이 오래되면 최신 wheel을 제대로 선택하지 못할 수 있음.

**해결 순서:**

```bash
# 1. pip, setuptools, wheel 최신으로 업그레이드
python -m pip install --upgrade pip setuptools wheel

# 2. 의존성 설치
pip install -r requirements.txt
```

### 2) 계속 실패할 때: binary만 설치

소스 빌드를 피하고 **wheel만** 쓰고 싶을 때:

```bash
python -m pip install --upgrade pip setuptools wheel

# pydantic 계열만 wheel로 강제 설치 후 나머지 설치
pip install --only-binary :all: pydantic pydantic-core
pip install -r requirements.txt
```

### 3) Python 버전

- **Python 3.9 ~ 3.13** 사용 가능.
- `requirements.txt`는 Python 3.9+에 맞춰져 있으며, Pydantic 2.6+ 구간으로 두어 3.12/3.13용 wheel이 있는 버전이 선택되도록 했습니다.
- Python 3.13에서만 문제가 있다면, 3.11 또는 3.12 가상환경을 쓰는 것도 방법입니다.

## 환경 변수 설정

`.env.example`을 `.env`로 복사 후 값 설정:
- Upbit API 키
- Supabase URL/Key
- Gemini API Key

## 실행

### FastAPI 서버 실행 (Market Watcher 자동 시작)
```bash
# 프로젝트 루트에서
uvicorn app.main:app --reload --app-dir backend

# 또는 backend 폴더에서
cd backend
uvicorn app.main:app --reload
```

### Market Watcher 테스트 스크립트
```bash
cd backend
python scripts/test_market_watcher.py
```

## API 엔드포인트

- `GET /health` - 헬스체크
- `POST /api/v1/detection/start` - Market Watcher 시작
- `POST /api/v1/detection/stop` - Market Watcher 중지
- `GET /api/v1/detection/status` - Market Watcher 상태 조회

## Market Watcher

실시간으로 BTC-KRW 시세를 감시하고 이상 징후를 감지합니다:
- 가격 변동률 감지 (1분 전 대비 1% 이상)
- 거래량 급변 감지
- 감지된 이벤트는 `anomaly_alerts` 테이블에 저장

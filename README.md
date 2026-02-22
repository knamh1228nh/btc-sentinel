# BTC Sentinel (AI Market Analyst)

업비트 실시간 시세 감시 및 Gemini AI 기반 시장 분석 도구.

## 기술 스택

- **Python**
- **Supabase**
- **Google Gemini API**
- **Streamlit**

## 실행 방법

```bash
pip install -r requirements.txt
python -m app.main
```

> 위 명령은 `backend` 폴더에서 실행하세요.  
> 대시보드는 `frontend` 폴더에서 `pip install -r requirements-dashboard.txt` 후 `streamlit run dashboard.py` 로 실행할 수 있습니다.

## 프로젝트 구조

- `backend/` — FastAPI 서버, 업비트 WebSocket 감지, Gemini 분석
- `frontend/` — Next.js 웹 앱 + Streamlit 대시보드 (`dashboard.py`)
- `supabase/` — DB 마이그레이션
- `docs/` — 아키텍처/API 문서

## 환경 변수

`backend/.env` 에 다음을 설정합니다.

- Upbit API (Access Key, Secret Key)
- Supabase URL, Key
- Gemini API Key

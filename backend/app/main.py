import json
import urllib.request
from typing import Optional
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.v1.routes import api_router
from app.config import settings
from app.core.detection.detector import start_market_watcher, stop_market_watcher


def _fetch_current_btc_price_krw() -> Optional[float]:
    """Upbit 공개 API로 현재 BTC/KRW 가격 조회 (인증 불필요)"""
    try:
        req = urllib.request.Request(
            "https://api.upbit.com/v1/ticker?markets=KRW-BTC",
            headers={"Accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            if data and isinstance(data, list) and len(data) > 0:
                return float(data[0].get("trade_price", 0))
    except Exception:
        pass
    return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # 서버 시작 시 메시지 및 현재 비트코인 가격 즉시 출력
    print("[START] 서버가 정상적으로 시작되었습니다.")
    btc_price = _fetch_current_btc_price_krw()
    if btc_price is not None:
        print(f"[START] 현재 비트코인 가격: {btc_price:,.0f} KRW")
    else:
        print("[START] 현재 비트코인 가격: 조회 실패 (WebSocket 연결 후 표시됩니다)")
    # Market Watcher 실행
    print("[INFO] Market Watcher 시작 중...")
    start_market_watcher("KRW-BTC")

    yield

    # 종료 시 Market Watcher 중지
    print("[INFO] Market Watcher 종료 중...")
    stop_market_watcher()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/api/v1/present-price")
def get_present_price():
    """현재 비트코인(KRW-BTC) 시세를 present_price로 반환"""
    price = _fetch_current_btc_price_krw()
    return {"present_price": price}


@app.get("/health")
def health():
    return {"status": "ok", "service": "mini-sentinel"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=getattr(settings, "API_HOST", "0.0.0.0"),
        port=getattr(settings, "API_PORT", 8000),
        reload=True,
        log_level="info",
    )

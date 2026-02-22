from fastapi import APIRouter
from app.schemas.detection import DetectionRequest, DetectionResponse
from app.core.detection.detector import start_market_watcher, stop_market_watcher, _watcher

router = APIRouter()

@router.post("/", response_model=DetectionResponse)
def run_detection(request: DetectionRequest):
    """System 1: 감지 API (수동 트리거)"""
    return DetectionResponse(detected=False, message="Detection placeholder")

@router.post("/start")
def start_watcher():
    """Market Watcher 시작"""
    try:
        watcher = start_market_watcher("KRW-BTC")
        return {"status": "started", "symbol": "KRW-BTC", "message": "Market Watcher가 시작되었습니다."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/stop")
def stop_watcher():
    """Market Watcher 중지"""
    try:
        stop_market_watcher()
        return {"status": "stopped", "message": "Market Watcher가 중지되었습니다."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/status")
def get_watcher_status():
    """Market Watcher 상태 조회"""
    if _watcher and _watcher.is_running:
        return {
            "status": "running",
            "symbol": _watcher.symbol,
            "is_running": _watcher.is_running
        }
    return {"status": "stopped", "is_running": False}

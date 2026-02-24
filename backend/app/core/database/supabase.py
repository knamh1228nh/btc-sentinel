from supabase import create_client
from datetime import datetime
from app.config import settings
from app.core.detection.models import MarketData, DetectionResult

_supabase_client = None

def get_supabase_client():
    """Supabase 클라이언트 싱글톤. SERVICE_ROLE_KEY가 있으면 사용 (RLS 우회, comment UPDATE 등 가능)."""
    global _supabase_client
    if _supabase_client is None:
        key = getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", None) or settings.SUPABASE_KEY
        _supabase_client = create_client(settings.SUPABASE_URL, key)
    return _supabase_client

def save_anomaly_event(market_data: MarketData, detection_result: DetectionResult):
    """이상 징후 이벤트를 anomaly_alerts 테이블에 저장"""
    try:
        supabase = get_supabase_client()
        
        anomaly_type = detection_result.details.get("anomaly_type", "unknown")
        # reason: details.reason 또는 anomaly_type 기반 한 줄 설명
        reason = detection_result.details.get("reason") or f"가격 변동률 {market_data.change_rate:.2f}% ({anomaly_type})"
        # anomaly_alerts 테이블에 저장할 데이터 구성
        anomaly_data = {
            "timestamp": market_data.timestamp.isoformat(),
            "symbol": market_data.symbol,
            "anomaly_type": anomaly_type,
            "reason": reason,
            "current_price": market_data.price,
            "previous_price": detection_result.details.get("previous_price"),
            "price_change_rate": detection_result.details.get("price_change_rate") or market_data.change_rate,
            "volume": market_data.volume,
            "previous_volume": detection_result.details.get("previous_volume"),
            "volume_change_rate": detection_result.details.get("volume_change_rate"),
            "confidence": detection_result.confidence,
            "details": detection_result.details,
            "high_price": market_data.high_price,
            "low_price": market_data.low_price,
            "trade_price": market_data.trade_price,
        }
        
        # Supabase에 삽입
        result = supabase.table("anomaly_alerts").insert(anomaly_data).execute()
        from app.utils.logger import logger
        logger.info(f"Anomaly 이벤트 저장 완료: {market_data.symbol} - {anomaly_type}")
        # 삽입된 행의 id 반환 (AI Analyst 백그라운드 분석용)
        inserted_id = None
        if result.data and len(result.data) > 0:
            row = result.data[0]
            inserted_id = row.get("id") if isinstance(row, dict) else getattr(row, "id", None)
            if inserted_id is not None:
                logger.info(f"INSERT 반환 id (Gemini 분석용): {inserted_id}")
            else:
                logger.warning("INSERT 응답에 id가 없음. result.data[0]=%s", type(row))
        else:
            logger.warning("INSERT 응답 data가 비어 있음. result.data=%s", getattr(result, "data", None))
        return result, inserted_id

    except Exception as e:
        from app.utils.logger import logger
        logger.error(f"Anomaly 이벤트 저장 실패: {e}")
        raise

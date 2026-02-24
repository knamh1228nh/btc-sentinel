"""감지 규칙 정의 및 이상 징후 감지 로직"""
from datetime import datetime, timedelta
from typing import Optional
from app.core.detection.models import MarketData, DetectionResult


# 가격 변동률 임계값 (%)
PRICE_CHANGE_THRESHOLD = 0.95  # 1분 전 대비 0.95% 이상 변동

# 거래량 급변 임계값 (%)
VOLUME_SURGE_THRESHOLD = 50.0  # 50% 이상 증가

# 가격 데이터 히스토리 (1분간)
price_history: dict[str, list[tuple[datetime, float]]] = {}


def check_anomalies(
    current_data: MarketData,
    previous_ticker_data: Optional[dict] = None
) -> DetectionResult:
    """
    이상 징후 감지
    
    규칙:
    1. 가격이 1분 전 대비 0.95% 이상 변동
    2. 거래량이 급변 (50% 이상 증가)
    """
    detected = False
    confidence = 0.0
    details = {}
    
    symbol = current_data.symbol
    
    # 가격 히스토리 관리 (1분 이전 데이터만 유지)
    now = current_data.timestamp
    cutoff_time = now - timedelta(minutes=1)
    
    if symbol not in price_history:
        price_history[symbol] = []
    
    # 오래된 데이터 제거
    price_history[symbol] = [
        (ts, price) for ts, price in price_history[symbol]
        if ts > cutoff_time
    ]
    
    # 현재 가격 추가
    price_history[symbol].append((current_data.timestamp, current_data.price))
    
    # 규칙 1: 가격 변동률 체크 (1분 전 대비)
    if len(price_history[symbol]) > 1:
        # 가장 오래된 데이터 (약 1분 전)
        oldest_timestamp, oldest_price = price_history[symbol][0]
        time_diff = (now - oldest_timestamp).total_seconds()
        
        # 1분 전후 데이터 사용 (30초 ~ 90초 범위)
        if 30 <= time_diff <= 90:
            price_change_rate = abs((current_data.price - oldest_price) / oldest_price * 100)
            
            if price_change_rate >= PRICE_CHANGE_THRESHOLD:
                detected = True
                confidence = min(price_change_rate / PRICE_CHANGE_THRESHOLD, 1.0)
                details["anomaly_type"] = "price_spike"
                details["price_change_rate"] = price_change_rate
                details["previous_price"] = oldest_price
                details["current_price"] = current_data.price
                details["time_diff_seconds"] = time_diff
    
    # 규칙 2: 거래량 급변 체크
    # ticker의 acc_trade_volume_24h는 누적 거래량이므로
    # 단기 거래량 급변은 trade 이벤트 빈도나 trade_price * trade_volume으로 계산
    # 현재는 ticker의 변동률로 간접 감지
    if previous_ticker_data:
        prev_volume = previous_ticker_data.get("acc_trade_volume_24h", 0)
        current_volume = current_data.volume
        
        if prev_volume > 0:
            volume_change_rate = abs((current_volume - prev_volume) / prev_volume * 100)
            
            # 24시간 누적 거래량은 급변하기 어려우므로, 
            # 대신 signed_change_rate의 절대값이 크면 거래량 급변으로 간주
            if abs(current_data.change_rate) >= PRICE_CHANGE_THRESHOLD * 2:
                if not detected:
                    detected = True
                    confidence = 0.7
                else:
                    confidence = min(confidence + 0.2, 1.0)
                
                details["anomaly_type"] = details.get("anomaly_type", "unknown") + "_volume_surge"
                details["volume_change_rate"] = volume_change_rate
                details["previous_volume"] = prev_volume
                details["current_volume"] = current_volume
    
    # 규칙 3: 변동률 자체가 임계값 초과
    if abs(current_data.change_rate) >= PRICE_CHANGE_THRESHOLD:
        if not detected:
            detected = True
            confidence = min(abs(current_data.change_rate) / PRICE_CHANGE_THRESHOLD, 1.0)
            details["anomaly_type"] = "price_change_rate_exceeded"
            details["change_rate"] = current_data.change_rate
    
    return DetectionResult(
        detected=detected,
        confidence=confidence,
        details=details
    )

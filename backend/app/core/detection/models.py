from pydantic import BaseModel
from typing import Any, Optional
from datetime import datetime

class DetectionResult(BaseModel):
    detected: bool
    confidence: float
    details: dict[str, Any]

class MarketData(BaseModel):
    """시장 데이터 모델"""
    timestamp: datetime
    symbol: str  # BTC-KRW
    price: float
    volume: float
    change_rate: float  # 변동률 (%)
    high_price: float
    low_price: float
    trade_price: float  # 체결가

class AnomalyEvent(BaseModel):
    """이상 징후 이벤트 모델"""
    timestamp: datetime
    symbol: str
    anomaly_type: str  # "price_spike", "volume_surge", etc.
    current_price: float
    previous_price: Optional[float] = None
    price_change_rate: float
    volume: float
    previous_volume: Optional[float] = None
    volume_change_rate: Optional[float] = None
    confidence: float
    details: dict[str, Any] = {}

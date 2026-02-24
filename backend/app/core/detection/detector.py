"""감지 엔진 - System 1: 실시간 시세 데이터 파이프라인"""
import json
import time
import threading
try:
    import websocket
except ImportError:
    try:
        import websocket_client as websocket
    except ImportError:
        raise ImportError("websocket-client 패키지가 설치되지 않았습니다. pip install websocket-client를 실행하세요.")
from datetime import datetime
from typing import Callable, Optional
from app.core.detection.models import MarketData
from app.core.detection.rules import check_anomalies
from app.core.database.supabase import save_anomaly_event
from app.utils.logger import logger


def _run_analysis_background(
    anomaly_log_id: str,
    symbol: str,
    current_price: float,
    volume: float,
    price_change_rate: float,
    anomaly_type: str,
):
    """백그라운드: Gemini 분석 후 anomaly_alerts.comment 업데이트"""
    logger.info("[AI Analyst] 백그라운드 분석 시작 id=%s symbol=%s", anomaly_log_id, symbol)
    try:
        from app.core.analysis.analyzer import run_analysis_and_save_comment
        summary = run_analysis_and_save_comment(
            anomaly_log_id=anomaly_log_id,
            symbol=symbol,
            current_price=current_price,
            volume=volume,
            price_change_rate=price_change_rate,
            anomaly_type=anomaly_type,
        )
        if summary:
            logger.info("[AI Analyst] 분석 완료 및 comment 업데이트 성공 id=%s (길이=%d)", anomaly_log_id, len(summary or ""))
        else:
            logger.warning("[AI Analyst] 분석 완료했으나 요약 없음 id=%s", anomaly_log_id)
    except Exception as e:
        logger.exception("AI Analyst 백그라운드 분석 실패: %s", e)


# 10초에 한 번만 anomaly 저장 (throttle)
LAST_ANOMALY_SAVE_TIME: float = 0
ANOMALY_SAVE_INTERVAL_SEC = 10


class MarketWatcher:
    """Upbit WebSocket을 통한 실시간 시세 감시"""
    
    def __init__(self, symbol: str = "KRW-BTC"):
        self.symbol = symbol
        self.ws_url = "wss://api.upbit.com/websocket/v1"
        self.ws: Optional[websocket.WebSocketApp] = None
        self.is_running = False
        self.reconnect_delay = 1  # 초기 재연결 지연 (초)
        self.max_reconnect_delay = 60  # 최대 재연결 지연 (초)
        self.last_ticker_data: Optional[dict] = None
        self.last_trade_data: Optional[dict] = None
        
    def _on_message(self, ws, message):
        """WebSocket 메시지 수신 핸들러"""
        try:
            data = json.loads(message)
            
            # ticker 데이터 처리
            if "type" in data and data["type"] == "ticker":
                self._process_ticker(data)
            # trade 데이터 처리
            elif "type" in data and data["type"] == "trade":
                self._process_trade(data)
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON 디코딩 오류: {e}")
        except Exception as e:
            logger.error(f"메시지 처리 오류: {e}")
    
    def _process_ticker(self, ticker_data: dict):
        """Ticker 데이터 처리 및 이상 징후 감지"""
        try:
            # 마지막 데이터와 비교를 위해 저장
            self.last_ticker_data = ticker_data
            
            # MarketData 모델로 변환
            market_data = MarketData(
                timestamp=datetime.fromtimestamp(ticker_data.get("timestamp", time.time()) / 1000),
                symbol=ticker_data.get("code", self.symbol),
                price=float(ticker_data.get("trade_price", 0)),
                volume=float(ticker_data.get("acc_trade_volume_24h", 0)),
                change_rate=float(ticker_data.get("signed_change_rate", 0)) * 100,
                high_price=float(ticker_data.get("high_price", 0)),
                low_price=float(ticker_data.get("low_price", 0)),
                trade_price=float(ticker_data.get("trade_price", 0))
            )
            
            logger.info(f"[Ticker] {market_data.symbol} - 가격: {market_data.price:,.0f} KRW, 변동률: {market_data.change_rate:.2f}%")
            
            # 이상 징후 감지
            anomaly_result = check_anomalies(market_data, self.last_ticker_data)
            
            if anomaly_result.detected:
                # 10초에 한 번만 저장 (throttle)
                now_ts = time.time()
                global LAST_ANOMALY_SAVE_TIME
                if now_ts - LAST_ANOMALY_SAVE_TIME < ANOMALY_SAVE_INTERVAL_SEC:
                    return
                LAST_ANOMALY_SAVE_TIME = now_ts

                logger.warning("[ANOMALY DETECTED] detected=True -> save_anomaly_event 호출 직전")
                # Supabase에 저장
                _, inserted_id = save_anomaly_event(market_data, anomaly_result)
                logger.info("[ANOMALY DETECTED] save_anomaly_event 반환 inserted_id=%s", inserted_id)
                # 비동기: Gemini로 분석 후 comment 업데이트
                if inserted_id:
                    price_change_for_ai = anomaly_result.details.get("price_change_rate") or anomaly_result.details.get("change_rate") or market_data.change_rate
                    t = threading.Thread(
                        target=_run_analysis_background,
                        args=(
                            str(inserted_id),
                            market_data.symbol,
                            market_data.price,
                            market_data.volume,
                            price_change_for_ai,
                            anomaly_result.details.get("anomaly_type", "unknown"),
                        ),
                        daemon=True,
                    )
                    t.start()
                    logger.info("[ANOMALY DETECTED] run_analysis_and_save_comment 스레드 시작 id=%s", inserted_id)
                else:
                    logger.warning("[ANOMALY DETECTED] inserted_id가 None이라 Gemini 분석 스레드 미실행")
                
        except Exception as e:
            logger.error(f"Ticker 처리 오류: {e}")
    
    def _process_trade(self, trade_data: dict):
        """Trade 데이터 처리"""
        try:
            self.last_trade_data = trade_data
            # 거래량 급변 감지를 위해 trade 데이터도 활용 가능
            # 현재는 ticker의 acc_trade_volume_24h를 주로 사용
        except Exception as e:
            logger.error(f"Trade 처리 오류: {e}")
    
    def _on_error(self, ws, error):
        """WebSocket 에러 핸들러"""
        logger.error(f"WebSocket 에러: {error}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        """WebSocket 연결 종료 핸들러"""
        logger.warning(f"WebSocket 연결 종료: {close_status_code} - {close_msg}")
        self.ws = None
        
        # 재연결 시도
        if self.is_running:
            self._reconnect()
    
    def _on_open(self, ws):
        """WebSocket 연결 시작 핸들러"""
        logger.info(f"WebSocket 연결 성공: {self.symbol}")
        print(f"[Market Watcher] WebSocket 연결 성공: {self.symbol} (실시간 시세 수신 중)")
        self.reconnect_delay = 1  # 재연결 성공 시 지연 시간 초기화

        # 구독 메시지 전송
        subscribe_msg = [
            {"ticket": "mini-sentinel"},
            {
                "type": "ticker",
                "codes": [self.symbol]
            },
            {
                "type": "trade",
                "codes": [self.symbol]
            }
        ]
        ws.send(json.dumps(subscribe_msg))
        logger.info(f"구독 요청 전송: {self.symbol}")
    
    def _reconnect(self):
        """지수 백오프를 사용한 재연결"""
        if not self.is_running:
            return
            
        logger.info(f"{self.reconnect_delay}초 후 재연결 시도...")
        time.sleep(self.reconnect_delay)
        
        # 지수 백오프: 최대 60초까지 증가
        self.reconnect_delay = min(self.reconnect_delay * 2, self.max_reconnect_delay)
        
        self.start()
    
    def start(self):
        """WebSocket 연결 시작"""
        if self.is_running and self.ws:
            logger.warning("이미 실행 중입니다.")
            return
        
        self.is_running = True
        
        try:
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
                on_open=self._on_open
            )
            
            # 별도 스레드에서 실행
            ws_thread = threading.Thread(target=self.ws.run_forever, daemon=True)
            ws_thread.start()
            
        except Exception as e:
            logger.error(f"WebSocket 시작 오류: {e}")
            if self.is_running:
                self._reconnect()
    
    def stop(self):
        """WebSocket 연결 종료"""
        self.is_running = False
        if self.ws:
            self.ws.close()
            self.ws = None
        logger.info("Market Watcher 종료")


# 전역 watcher 인스턴스
_watcher: Optional[MarketWatcher] = None


def start_market_watcher(symbol: str = "KRW-BTC"):
    """Market Watcher 시작"""
    global _watcher
    if _watcher is None:
        _watcher = MarketWatcher(symbol)
    _watcher.start()
    return _watcher


def stop_market_watcher():
    """Market Watcher 종료"""
    global _watcher
    if _watcher:
        _watcher.stop()
        _watcher = None

"""AI Analyst: Gemini API 연동으로 시장 상황 기술적 분석"""
from typing import Optional

from app.config import settings
from app.core.analysis.models import AnalysisResult
from app.core.analysis.prompts import MARKET_ANALYSIS_PROMPT
from app.utils.logger import logger


def analyze_with_gemini(
    symbol: str,
    current_price: float,
    volume: float,
    price_change_rate: float,
    anomaly_type: str = "unknown",
) -> AnalysisResult:
    """
    감지된 시세(가격, 거래량, 변동률)를 Gemini에 전달하고
    '현재 시장 상황이 기술적으로 어떤 의미인지 3줄 이내로' 분석 요청.
    """
    logger.info("[Gemini] 분석 요청 시작 symbol=%s price=%s", symbol, current_price)
    try:
        import google.generativeai as genai

        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = MARKET_ANALYSIS_PROMPT.format(
            symbol=symbol,
            current_price=current_price,
            volume=volume,
            price_change_rate=price_change_rate,
            anomaly_type=anomaly_type,
        )
        response = model.generate_content(prompt)
        # 응답 텍스트 추출 (구조 다양성 대응)
        text = ""
        if hasattr(response, "text") and response.text:
            text = (response.text or "").strip()
        if not text and getattr(response, "candidates", None):
            for c in response.candidates:
                if getattr(c, "content", None) and getattr(c.content, "parts", None):
                    for p in c.content.parts:
                        if getattr(p, "text", None):
                            text = (text + " " + p.text).strip()
        logger.info("[Gemini] 분석 응답 수신 길이=%d", len(text))
        return AnalysisResult(summary=text, risk_level="", raw_response=text)
    except Exception as e:
        logger.exception("Gemini 분석 실패: %s", e)
        return AnalysisResult(
            summary="",
            risk_level="error",
            raw_response=str(e),
        )


def run_analysis_and_save_comment(
    anomaly_log_id: str,
    symbol: str,
    current_price: float,
    volume: float,
    price_change_rate: float,
    anomaly_type: str,
) -> Optional[str]:
    """
    Gemini 분석 실행 후 Supabase anomaly_alerts.comment에 저장.
    Returns 분석 요약 문자열, 실패 시 None.
    """
    logger.info("[AI Analyst] run_analysis_and_save_comment 시작 id=%s", anomaly_log_id)
    result = analyze_with_gemini(
        symbol=symbol,
        current_price=current_price,
        volume=volume,
        price_change_rate=price_change_rate,
        anomaly_type=anomaly_type,
    )
    if not result.summary and result.risk_level == "error":
        logger.warning("[AI Analyst] Gemini 분석 결과 없음 또는 에러. comment 업데이트 스킵 id=%s", anomaly_log_id)
        return None
    summary = result.summary or result.raw_response
    if not summary:
        logger.warning("[AI Analyst] summary 비어 있음. raw_response만 사용 id=%s", anomaly_log_id)
        return None
    from app.core.database.supabase import get_supabase_client

    supabase = get_supabase_client()
    try:
        supabase.table("anomaly_alerts").update({"comment": summary}).eq("id", anomaly_log_id).execute()
        logger.info("[AI Analyst] DB 업데이트 성공 id=%s comment 길이=%d", anomaly_log_id, len(summary))
    except Exception as e:
        logger.exception("[AI Analyst] DB update 실패 id=%s: %s", anomaly_log_id, e)
        raise
    return summary

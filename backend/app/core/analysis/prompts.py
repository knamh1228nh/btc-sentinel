"""Gemini 분석용 프롬프트 템플릿"""

MARKET_ANALYSIS_PROMPT = """다음은 암호화폐 시장 이상 징후 감지 로그입니다.

- 심볼: {symbol}
- 현재 가격: {current_price:,.0f} KRW
- 거래량: {volume}
- 가격 변동률: {price_change_rate:.2f}%
- 이상 유형: {anomaly_type}

현재 시장 상황이 기술적으로 어떤 의미인지 3줄 이내로 분석해줘. 한국어로 답변해줘."""

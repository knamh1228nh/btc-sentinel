# anomaly_alerts 테이블 컬럼 (코드 기준 추출)

## INSERT 시 사용하는 키 (supabase.py save_anomaly_event)

| 키 | 코드 소스 | Python 타입 | SQL 타입 |
|----|-----------|-------------|----------|
| timestamp | market_data.timestamp.isoformat() | str (ISO 8601) | TIMESTAMPTZ |
| symbol | market_data.symbol | str | TEXT |
| anomaly_type | detection_result.details.get("anomaly_type") | str | TEXT |
| current_price | market_data.price | float | NUMERIC / DOUBLE PRECISION |
| previous_price | detection_result.details.get("previous_price") | float \| None | NUMERIC |
| price_change_rate | ... or market_data.change_rate | float \| None | NUMERIC |
| volume | market_data.volume | float | NUMERIC |
| previous_volume | detection_result.details.get("previous_volume") | float \| None | NUMERIC |
| volume_change_rate | detection_result.details.get("volume_change_rate") | float \| None | NUMERIC |
| confidence | detection_result.confidence | float | NUMERIC |
| details | detection_result.details | dict | JSONB |
| high_price | market_data.high_price | float | NUMERIC |
| low_price | market_data.low_price | float | NUMERIC |
| trade_price | market_data.trade_price | float | NUMERIC |

## UPDATE 시 사용하는 키 (analyzer.py)

| 키 | 용도 | Python 타입 | SQL 타입 |
|----|------|-------------|----------|
| comment | Gemini 분석 요약 저장 | str | TEXT |

## 기타 (main.py 테스트, test_ai_analyst.py)

- INSERT 시 위와 동일한 키 사용 (timestamp, symbol, anomaly_type, current_price, volume, confidence, details 등).
- id: Supabase/PostgreSQL 기본 키(UUID)로 자동 생성 가정.

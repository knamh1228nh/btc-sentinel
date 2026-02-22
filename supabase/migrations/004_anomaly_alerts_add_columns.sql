-- =============================================================================
-- anomaly_alerts 테이블에 코드에서 사용하는 컬럼 추가 (한 번에 실행)
-- Supabase SQL Editor에서 실행 가능
-- 코드 기준: supabase.py save_anomaly_event, main.py, test_ai_analyst.py, analyzer.py
-- =============================================================================

-- 시각/식별
ALTER TABLE anomaly_alerts ADD COLUMN IF NOT EXISTS timestamp TIMESTAMPTZ;
ALTER TABLE anomaly_alerts ADD COLUMN IF NOT EXISTS symbol TEXT;
ALTER TABLE anomaly_alerts ADD COLUMN IF NOT EXISTS anomaly_type TEXT;

-- 가격 (NUMERIC: 금융 수치 정확도)
ALTER TABLE anomaly_alerts ADD COLUMN IF NOT EXISTS current_price NUMERIC;
ALTER TABLE anomaly_alerts ADD COLUMN IF NOT EXISTS previous_price NUMERIC;
ALTER TABLE anomaly_alerts ADD COLUMN IF NOT EXISTS price_change_rate NUMERIC;
ALTER TABLE anomaly_alerts ADD COLUMN IF NOT EXISTS high_price NUMERIC;
ALTER TABLE anomaly_alerts ADD COLUMN IF NOT EXISTS low_price NUMERIC;
ALTER TABLE anomaly_alerts ADD COLUMN IF NOT EXISTS trade_price NUMERIC;

-- 거래량·비율
ALTER TABLE anomaly_alerts ADD COLUMN IF NOT EXISTS volume NUMERIC;
ALTER TABLE anomaly_alerts ADD COLUMN IF NOT EXISTS previous_volume NUMERIC;
ALTER TABLE anomaly_alerts ADD COLUMN IF NOT EXISTS volume_change_rate NUMERIC;

-- 감지 메타
ALTER TABLE anomaly_alerts ADD COLUMN IF NOT EXISTS reason TEXT;
ALTER TABLE anomaly_alerts ADD COLUMN IF NOT EXISTS confidence NUMERIC;
ALTER TABLE anomaly_alerts ADD COLUMN IF NOT EXISTS details JSONB DEFAULT '{}';

-- AI 분석 결과 (analyzer.py update)
ALTER TABLE anomaly_alerts ADD COLUMN IF NOT EXISTS comment TEXT;
ALTER TABLE anomaly_alerts ADD COLUMN IF NOT EXISTS ai_comment TEXT;

-- 생성 시각 (선택, 있으면 유지)
ALTER TABLE anomaly_alerts ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT now();

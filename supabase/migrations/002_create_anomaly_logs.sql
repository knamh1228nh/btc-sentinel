-- anomaly_logs 테이블 생성
CREATE TABLE IF NOT EXISTS anomaly_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL,
    symbol TEXT NOT NULL,
    anomaly_type TEXT NOT NULL,
    current_price NUMERIC NOT NULL,
    previous_price NUMERIC,
    price_change_rate NUMERIC,
    volume NUMERIC NOT NULL,
    previous_volume NUMERIC,
    volume_change_rate NUMERIC,
    confidence NUMERIC NOT NULL,
    details JSONB DEFAULT '{}',
    high_price NUMERIC,
    low_price NUMERIC,
    trade_price NUMERIC,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 인덱스 생성 (조회 성능 향상)
CREATE INDEX IF NOT EXISTS idx_anomaly_logs_timestamp ON anomaly_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_anomaly_logs_symbol ON anomaly_logs(symbol);
CREATE INDEX IF NOT EXISTS idx_anomaly_logs_anomaly_type ON anomaly_logs(anomaly_type);
CREATE INDEX IF NOT EXISTS idx_anomaly_logs_created_at ON anomaly_logs(created_at DESC);

-- RLS (Row Level Security) 정책 설정 (선택사항)
ALTER TABLE anomaly_logs ENABLE ROW LEVEL SECURITY;

-- 모든 사용자가 읽기 가능하도록 정책 설정 (필요에 따라 수정)
CREATE POLICY "Allow read access to anomaly_logs" ON anomaly_logs
    FOR SELECT USING (true);

-- 서비스 역할만 삽입 가능하도록 정책 설정
CREATE POLICY "Allow insert access to anomaly_logs" ON anomaly_logs
    FOR INSERT WITH CHECK (true);

-- anomaly_logs에 AI 분석 결과용 comment 컬럼 추가
ALTER TABLE anomaly_logs
ADD COLUMN IF NOT EXISTS comment TEXT;

COMMENT ON COLUMN anomaly_logs.comment IS 'Gemini AI 분석 요약 (3줄 이내)';

-- comment 업데이트를 위한 RLS 정책
CREATE POLICY "Allow update anomaly_logs" ON anomaly_logs
    FOR UPDATE USING (true) WITH CHECK (true);

"""
AI Analyst 테스트: anomaly_alerts에 샘플 행 INSERT 후
해당 id로 Gemini 분석을 호출하고 comment 컬럼 업데이트를 터미널 로그로 확인.

사전 요청: Supabase에 anomaly_alerts 테이블에 comment 컬럼이 있어야 함.
실행: backend 폴더에서 python scripts/test_ai_analyst.py
"""
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

backend_dir = Path(__file__).parent.parent.resolve()
env_path = backend_dir / ".env"
if not env_path.exists():
    env_path = Path(".env")
load_dotenv(env_path)
sys.path.insert(0, str(backend_dir))

# 샘플 데이터: 가격 1.5% 변동 가정
SAMPLE_ROW = {
    "timestamp": datetime.now(tz=timezone.utc).isoformat(),
    "symbol": "KRW-BTC",
    "anomaly_type": "price_spike",
    "current_price": 100_000_000,
    "previous_price": 98_522_167,
    "price_change_rate": 1.5,
    "volume": 1500.5,
    "previous_volume": 1400.0,
    "volume_change_rate": 7.18,
    "confidence": 0.85,
    "details": {"reason": "test_ai_analyst", "price_change_rate": 1.5},
    "high_price": 100_500_000,
    "low_price": 99_800_000,
    "trade_price": 100_000_000,
}


def main():
    print("=" * 60)
    print("AI Analyst 테스트 (analyze_with_gemini / run_analysis_and_save_comment)")
    print("=" * 60)

    from app.core.database.supabase import get_supabase_client
    from app.core.analysis.analyzer import run_analysis_and_save_comment

    supabase = get_supabase_client()

    # 1) anomaly_alerts에 샘플 행 INSERT
    print("\n[1] anomaly_alerts에 샘플 데이터 INSERT 중...")
    print(f"    샘플: 가격 {SAMPLE_ROW['current_price']:,.0f} KRW, 변동률 {SAMPLE_ROW['price_change_rate']}%")
    result = supabase.table("anomaly_alerts").insert(SAMPLE_ROW).execute()
    if not result.data or len(result.data) == 0:
        print("[ERROR] INSERT 실패 또는 반환 데이터 없음.")
        sys.exit(1)
    inserted = result.data[0]
    anomaly_log_id = inserted.get("id") if isinstance(inserted, dict) else getattr(inserted, "id", None)
    if not anomaly_log_id:
        print("[ERROR] INSERT 응답에서 id를 찾을 수 없음.")
        sys.exit(1)
    print(f"    [OK] INSERT 성공. id = {anomaly_log_id}")

    # 2) Gemini 분석 호출 및 comment 업데이트
    print("\n[2] Gemini 분석 호출 (run_analysis_and_save_comment)...")
    summary = run_analysis_and_save_comment(
        anomaly_log_id=str(anomaly_log_id),
        symbol=SAMPLE_ROW["symbol"],
        current_price=float(SAMPLE_ROW["current_price"]),
        volume=float(SAMPLE_ROW["volume"]),
        price_change_rate=float(SAMPLE_ROW["price_change_rate"]),
        anomaly_type=SAMPLE_ROW["anomaly_type"],
    )
    if summary:
        print("    [OK] Gemini 분석 완료. comment 업데이트됨.")
        print("\n    --- Gemini 분석 요약 (comment에 저장된 내용) ---")
        print(summary)
        print("    ---")
    else:
        print("    [WARN] 분석 요약 없음 (에러 시 로거에 상세 로그 출력됨).")

    # 3) DB에서 해당 행 조회하여 comment 확인
    print("\n[3] anomaly_alerts에서 해당 행 조회 (comment 컬럼 확인)...")
    row = supabase.table("anomaly_alerts").select("id, comment, current_price, price_change_rate").eq("id", anomaly_log_id).single().execute()
    if row.data:
        d = row.data
        print(f"    id: {d.get('id')}")
        print(f"    current_price: {d.get('current_price')}, price_change_rate: {d.get('price_change_rate')}%")
        print(f"    comment: {d.get('comment') or '(비어 있음)'}")
    else:
        print("    [WARN] 조회 결과 없음.")

    print("\n" + "=" * 60)
    print("테스트 완료.")
    print("=" * 60)


if __name__ == "__main__":
    main()

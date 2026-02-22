"""
Step 3. Dashboard - Mini Sentinel 이상 징후 모니터링
실행: streamlit run dashboard.py (frontend 폴더에서)
"""
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

# 프로젝트 루트/backend .env 로드
root = Path(__file__).resolve().parent.parent
env_path = root / "backend" / ".env"
if not env_path.exists():
    env_path = root / ".env"
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client

# 페이지 설정: 다크 모드, 넓은 레이아웃
st.set_page_config(
    page_title="Mini Sentinel Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 다크 테마용 커스텀 CSS
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.25rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .metric-card h3 { color: #94a3b8; font-size: 0.85rem; margin-bottom: 0.25rem; }
    .metric-card .value { color: #f1f5f9; font-size: 1.75rem; font-weight: 700; }
    div[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }
    .stDataFrame { border: 1px solid #334155 !important; }
    .refresh-hint { color: #64748b; font-size: 0.8rem; margin-top: 0.5rem; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_supabase():
    url = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
    if not url or not key:
        st.error("SUPABASE_URL, SUPABASE_KEY(또는 NEXT_PUBLIC_*)를 설정해주세요. (backend/.env 또는 .env)")
        return None
    return create_client(url, key)


@st.cache_data(ttl=10)
def fetch_anomaly_alerts():
    """anomaly_alerts 테이블 최신순 조회 (10초 캐시). select(*) 로 comment 포함 전체 컬럼."""
    supabase = get_supabase()
    if supabase is None:
        return None
    try:
        res = supabase.table("anomaly_alerts").select("*").order("timestamp", desc=True).execute()
        if res.data is None:
            return pd.DataFrame()
        df = pd.DataFrame(res.data)
        if "comment" not in df.columns and "ai_comment" not in df.columns:
            df["comment"] = ""
        return df
    except Exception as e:
        st.error(f"데이터 조회 실패: {e}")
        return None


def main():
    # 10초마다 자동 새로고침 (streamlit-autorefresh 설치 시 동작)
    try:
        from streamlit_autorefresh import st_autorefresh
        st_autorefresh(interval=10_000, limit=None, key="dashboard_refresh")
    except ImportError:
        pass  # 패키지 없으면 수동 새로고침만 사용
    if st.button("🔄 수동 새로고침"):
        if getattr(st, "cache_data", None) and hasattr(st.cache_data, "clear"):
            st.cache_data.clear()
        st.rerun()

    st.title("📊 Mini Sentinel Dashboard")
    st.caption("이상 징후 실시간 모니터링 · 10초마다 새로고침 버튼을 눌러 최신화하세요.")

    df = fetch_anomaly_alerts()
    if df is None:
        return
    if df.empty:
        st.info("아직 anomaly_alerts 데이터가 없습니다. 백엔드에서 이상 징후가 감지되면 여기에 표시됩니다.")
        return

    # 최근 이상 징후 메트릭 카드 (상단)
    st.subheader("최근 이상 징후")
    n_total = len(df)
    n_24h = 0
    if "timestamp" in df.columns:
        try:
            df["_ts"] = pd.to_datetime(df["timestamp"], utc=True)
            cutoff = datetime.now(timezone.utc) - pd.Timedelta(hours=24)
            n_24h = (df["_ts"] >= cutoff).sum()
        except Exception:
            n_24h = n_total
    else:
        n_24h = n_total

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("전체 로그 수", n_total, help="anomaly_alerts 전체 건수")
    with col2:
        st.metric("최근 24시간", n_24h, help="최근 24시간 내 발생 건수")
    with col3:
        latest_price = df["current_price"].iloc[0] if "current_price" in df.columns and len(df) else None
        st.metric("최신 감지 가격 (KRW)", f"{latest_price:,.0f}" if latest_price is not None else "-", help="가장 최근 행의 current_price")
    with col4:
        latest_type = df["anomaly_type"].iloc[0] if "anomaly_type" in df.columns and len(df) else "-"
        st.metric("최신 유형", str(latest_type), help="가장 최근 행의 anomaly_type")

    # 가격 변동 추이 (Plotly 꺾은선)
    st.subheader("가격 변동 추이 (current_price)")
    if "current_price" in df.columns and "timestamp" in df.columns and len(df) > 0:
        try:
            plot_df = df.copy()
            plot_df["timestamp"] = pd.to_datetime(plot_df["timestamp"], utc=True)
            plot_df = plot_df.sort_values("timestamp").reset_index(drop=True)
            fig = px.line(
                plot_df,
                x="timestamp",
                y="current_price",
                title="",
                labels={"timestamp": "시각", "current_price": "가격 (KRW)"},
            )
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(30,41,59,0.5)",
                font=dict(color="#e2e8f0"),
                margin=dict(l=60, r=40, t=40, b=60),
                height=360,
                xaxis=dict(gridcolor="#334155"),
                yaxis=dict(gridcolor="#334155"),
            )
            fig.update_traces(line=dict(color="#38bdf8", width=2))
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"차트 생성 중 오류: {e}")
    else:
        st.caption("timestamp 또는 current_price 컬럼이 없어 차트를 그리지 않습니다.")

    # 전체 로그 테이블 (간소화: 시각 하나로 통합, reason·comment 강조)
    st.subheader("전체 로그 (최신순)")
    # 시각: timestamp > created_at > detected_at 순으로 하나만 사용
    time_col = None
    for c in ("timestamp", "created_at", "detected_at"):
        if c in df.columns:
            time_col = c
            break
    cols_show = ["시각", "symbol", "anomaly_type", "current_price", "price_change_rate", "reason", "AI 분석"]
    show_df = pd.DataFrame()
    if time_col:
        show_df["시각"] = pd.to_datetime(df[time_col], utc=True)
    else:
        show_df["시각"] = pd.NaT
    show_df["symbol"] = df["symbol"] if "symbol" in df.columns else ""
    show_df["anomaly_type"] = df["anomaly_type"] if "anomaly_type" in df.columns else ""
    show_df["current_price"] = df["current_price"] if "current_price" in df.columns else None
    show_df["price_change_rate"] = df["price_change_rate"] if "price_change_rate" in df.columns else None
    # reason: reason 컬럼 또는 details.reason
    if "reason" in df.columns:
        show_df["reason"] = df["reason"].fillna("").astype(str).replace("nan", "")
    elif "details" in df.columns:
        show_df["reason"] = df["details"].apply(lambda x: x.get("reason", "") if isinstance(x, dict) else "").fillna("").astype(str)
    else:
        show_df["reason"] = [""] * len(df)
    # AI 분석: comment 또는 ai_comment
    ai_text = None
    if "comment" in df.columns:
        ai_text = df["comment"].fillna("")
    elif "ai_comment" in df.columns:
        ai_text = df["ai_comment"].fillna("")
    else:
        ai_text = pd.Series([""] * len(df))
    show_df["AI 분석"] = ai_text.astype(str).replace("nan", "")
    column_config = {
        "시각": st.column_config.DatetimeColumn("시각", format="YYYY-MM-DD HH:mm:ss"),
        "symbol": st.column_config.TextColumn("심볼"),
        "anomaly_type": st.column_config.TextColumn("유형"),
        "current_price": st.column_config.NumberColumn("가격 (KRW)", format="%.0f"),
        "price_change_rate": st.column_config.NumberColumn("변동률 (%)", format="%.2f"),
        "reason": st.column_config.TextColumn("사유", width="medium"),
        "AI 분석": st.column_config.TextColumn("Gemini 분석", width="large"),
    }
    st.dataframe(show_df, use_container_width=True, column_config=column_config, height=400)

    st.markdown('<p class="refresh-hint">💡 10초마다 위쪽 새로고침 버튼을 누르면 최신 데이터로 갱신됩니다.</p>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()

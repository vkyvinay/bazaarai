import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import pytz

st.set_page_config(
    page_title="BazaarAI — Indian Market Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── THEME ────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Mono:wght@400;500&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
.stApp { background: #0a0f1e; color: #e8eaf0; }
.block-container { padding: 1.5rem 2rem; max-width: 1400px; }
/* Metric cards */
div[data-testid="metric-container"] {
    background: #12192e;
    border: 1px solid rgba(99,132,199,0.15);
    border-radius: 12px;
    padding: 16px;
}
div[data-testid="metric-container"] label { color: #8b93b3 !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 1px; }
div[data-testid="metric-container"] div[data-testid="stMetricValue"] { font-family: 'DM Mono', monospace !important; font-size: 22px !important; }
div[data-testid="metric-container"] div[data-testid="stMetricDelta"] svg { display: none; }
/* Sidebar */
section[data-testid="stSidebar"] { background: #0f1729 !important; border-right: 1px solid rgba(99,132,199,0.15); }
section[data-testid="stSidebar"] * { color: #e8eaf0 !important; }
/* Tabs */
div[data-testid="stTabs"] button { font-family: 'Plus Jakarta Sans', sans-serif !important; font-size: 13px !important; }
div[data-testid="stTabs"] button[aria-selected="true"] { color: #4e8cff !important; border-bottom-color: #4e8cff !important; }
/* Dataframe */
div[data-testid="stDataFrame"] { border: 1px solid rgba(99,132,199,0.15); border-radius: 8px; }
/* Select/inputs */
div[data-baseweb="select"] > div { background: #12192e !important; border-color: rgba(99,132,199,0.25) !important; }
.stSelectbox label, .stMultiSelect label { font-size: 12px !important; color: #8b93b3 !important; text-transform: uppercase; letter-spacing: .5px; }
h1,h2,h3 { font-family: 'DM Serif Display', serif !important; color: #e8eaf0 !important; }
.logo-text { font-family: 'DM Serif Display', serif; font-size: 28px; color: #e8eaf0; }
.logo-text span { color: #4e8cff; }
.subtitle { font-size: 12px; color: #5a6285; letter-spacing: 2px; text-transform: uppercase; }
.section-title { font-size: 11px; letter-spacing: 1px; text-transform: uppercase; color: #5a6285; margin-bottom: 8px; font-weight: 600; }
.tag-green { background: rgba(34,200,122,.15); color: #22c87a; padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; }
.tag-red   { background: rgba(240,82,82,.15);  color: #f05252; padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; }
.tag-amber { background: rgba(245,166,35,.15); color: #f5a623; padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; }
.sug-card { background: #12192e; border: 1px solid rgba(99,132,199,0.15); border-radius: 12px; padding: 16px; margin-bottom: 12px; }
.ist-time { font-family: 'DM Mono', monospace; font-size: 13px; color: #1dd9b2; }
hr { border-color: rgba(99,132,199,0.1) !important; }
</style>
""", unsafe_allow_html=True)

# ─── CONSTANTS ────────────────────────────────────
IST = pytz.timezone("Asia/Kolkata")

INDICES = {
    "NIFTY 50":   "^NSEI",
    "SENSEX":     "^BSESN",
    "BANK NIFTY": "^NSEBANK",
    "NIFTY IT":   "^CNXIT",
    "NIFTY MIDCAP": "^NSEMDCP50",
}

NIFTY50_STOCKS = {
    "RELIANCE": "RELIANCE.NS", "TCS": "TCS.NS", "INFY": "INFY.NS",
    "HDFCBANK": "HDFCBANK.NS", "ICICIBANK": "ICICIBANK.NS",
    "HINDUNILVR": "HINDUNILVR.NS", "SBIN": "SBIN.NS",
    "BAJFINANCE": "BAJFINANCE.NS", "KOTAKBANK": "KOTAKBANK.NS",
    "BHARTIARTL": "BHARTIARTL.NS", "WIPRO": "WIPRO.NS",
    "SUNPHARMA": "SUNPHARMA.NS", "AXISBANK": "AXISBANK.NS",
    "MARUTI": "MARUTI.NS", "NESTLEIND": "NESTLEIND.NS",
    "LTIM": "LTIM.NS", "TITAN": "TITAN.NS", "TECHM": "TECHM.NS",
    "HCLTECH": "HCLTECH.NS", "DRREDDY": "DRREDDY.NS",
    "DIVISLAB": "DIVISLAB.NS", "TATASTEEL": "TATASTEEL.NS",
    "JSWSTEEL": "JSWSTEEL.NS", "ONGC": "ONGC.NS",
    "COALINDIA": "COALINDIA.NS", "ASIANPAINT": "ASIANPAINT.NS",
    "M&M": "M&M.NS", "BAJAJFINSV": "BAJAJFINSV.NS",
    "ITC": "ITC.NS", "CIPLA": "CIPLA.NS",
    "ADANIENT": "ADANIENT.NS", "ADANIPORTS": "ADANIPORTS.NS",
    "GRASIM": "GRASIM.NS", "NTPC": "NTPC.NS",
    "POWERGRID": "POWERGRID.NS", "ULTRACEMCO": "ULTRACEMCO.NS",
}

SECTORS = {
    "IT": ["TCS", "INFY", "WIPRO", "HCLTECH", "TECHM", "LTIM"],
    "Banking": ["HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK", "KOTAKBANK"],
    "Pharma": ["SUNPHARMA", "DRREDDY", "DIVISLAB", "CIPLA"],
    "Auto": ["MARUTI", "M&M"],
    "FMCG": ["HINDUNILVR", "NESTLEIND", "ITC"],
    "Metal": ["TATASTEEL", "JSWSTEEL", "COALINDIA"],
    "Energy": ["RELIANCE", "ONGC", "NTPC", "POWERGRID"],
}

PLOTLY_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#8b93b3", family="DM Mono, monospace", size=11),
    xaxis=dict(gridcolor="rgba(99,132,199,0.08)", linecolor="rgba(99,132,199,0.15)", tickcolor="rgba(99,132,199,0.15)"),
    yaxis=dict(gridcolor="rgba(99,132,199,0.08)", linecolor="rgba(99,132,199,0.15)", tickcolor="rgba(99,132,199,0.15)"),
    margin=dict(l=50, r=20, t=30, b=40),
)

# ─── DATA FETCHING ────────────────────────────────
@st.cache_data(ttl=300)  # 5-minute cache
def fetch_index_data(symbol, period="1d", interval="5m"):
    try:
        t = yf.Ticker(symbol)
        df = t.history(period=period, interval=interval)
        return df
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def fetch_stock_quote(symbol):
    try:
        t = yf.Ticker(symbol)
        info = t.fast_info
        hist = t.history(period="2d", interval="1d")
        if len(hist) >= 2:
            prev = hist["Close"].iloc[-2]
            curr = hist["Close"].iloc[-1]
            chg = curr - prev
            pct = (chg / prev) * 100
        else:
            curr = getattr(info, "last_price", 0)
            chg = 0; pct = 0
        return {"price": curr, "chg": chg, "pct": pct, "vol": getattr(info, "three_month_average_volume", 0)}
    except Exception:
        return {"price": 0, "chg": 0, "pct": 0, "vol": 0}

@st.cache_data(ttl=300)
def fetch_multiple_quotes(symbols_dict):
    results = {}
    tickers = list(symbols_dict.values())
    try:
        data = yf.download(tickers, period="2d", interval="1d", progress=False, group_by="ticker")
        for sym, ticker in symbols_dict.items():
            try:
                if len(tickers) == 1:
                    close = data["Close"]
                else:
                    close = data[ticker]["Close"]
                close = close.dropna()
                if len(close) >= 2:
                    prev, curr = close.iloc[-2], close.iloc[-1]
                    chg = curr - prev
                    pct = (chg / prev) * 100
                    results[sym] = {"price": round(curr, 2), "chg": round(chg, 2), "pct": round(pct, 2)}
                else:
                    results[sym] = {"price": 0, "chg": 0, "pct": 0}
            except Exception:
                results[sym] = {"price": 0, "chg": 0, "pct": 0}
    except Exception:
        for sym in symbols_dict:
            results[sym] = {"price": 0, "chg": 0, "pct": 0}
    return results

@st.cache_data(ttl=600)
def fetch_fundamentals(symbol):
    try:
        t = yf.Ticker(symbol)
        info = t.info
        return {
            "pe": info.get("trailingPE", "N/A"),
            "pb": info.get("priceToBook", "N/A"),
            "roe": info.get("returnOnEquity", "N/A"),
            "eps": info.get("trailingEps", "N/A"),
            "mktcap": info.get("marketCap", 0),
            "52wH": info.get("fiftyTwoWeekHigh", 0),
            "52wL": info.get("fiftyTwoWeekLow", 0),
            "div": info.get("dividendYield", 0),
            "beta": info.get("beta", "N/A"),
            "name": info.get("longName", symbol),
            "sector": info.get("sector", "N/A"),
        }
    except Exception:
        return {}

# ─── TECHNICAL INDICATORS ─────────────────────────
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def compute_macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast).mean()
    ema_slow = series.ewm(span=slow).mean()
    macd = ema_fast - ema_slow
    sig  = macd.ewm(span=signal).mean()
    hist = macd - sig
    return macd, sig, hist

def compute_bollinger(series, period=20, std=2):
    sma  = series.rolling(period).mean()
    stdv = series.rolling(period).std()
    return sma + std*stdv, sma, sma - std*stdv

def compute_indicators(df):
    if df.empty or "Close" not in df.columns:
        return {}
    close = df["Close"]
    rsi  = compute_rsi(close).iloc[-1]
    sma20 = close.rolling(20).mean().iloc[-1]
    sma50 = close.rolling(50).mean().iloc[-1]
    sma200 = close.rolling(200).mean().iloc[-1]
    macd, sig, _ = compute_macd(close)
    curr = close.iloc[-1]
    atr = (df["High"] - df["Low"]).rolling(14).mean().iloc[-1] if "High" in df.columns else 0
    return {
        "RSI (14)":   (round(rsi, 1),   "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Neutral"),
        "SMA 20":     (round(sma20, 1), "Buy" if curr > sma20 else "Sell"),
        "SMA 50":     (round(sma50, 1), "Buy" if curr > sma50 else "Sell"),
        "SMA 200":    (round(sma200, 1),"Buy" if curr > sma200 else "Sell"),
        "MACD":       (round(macd.iloc[-1], 2), "Buy" if macd.iloc[-1] > sig.iloc[-1] else "Sell"),
        "ATR (14)":   (round(atr, 2),   "—"),
    }

def generate_suggestions(quotes, hist_data):
    suggestions = []
    for sym, q in quotes.items():
        ticker = NIFTY50_STOCKS.get(sym)
        if not ticker or q["price"] == 0:
            continue
        df = hist_data.get(sym, pd.DataFrame())
        if df.empty or len(df) < 20:
            continue
        close = df["Close"]
        rsi = compute_rsi(close).iloc[-1]
        macd, sig, _ = compute_macd(close)
        sma20 = close.rolling(20).mean().iloc[-1]
        vol_avg = df["Volume"].rolling(20).mean().iloc[-1] if "Volume" in df.columns else 0
        vol_curr = df["Volume"].iloc[-1] if "Volume" in df.columns else 0
        vol_ratio = vol_curr / vol_avg if vol_avg > 0 else 1
        reasons = []
        score = 0
        if 45 < rsi < 65:
            reasons.append(f"RSI at {rsi:.1f} — healthy momentum zone")
            score += 2
        if macd.iloc[-1] > sig.iloc[-1] and macd.iloc[-2] <= sig.iloc[-2]:
            reasons.append("Fresh MACD bullish crossover")
            score += 3
        if q["price"] > sma20:
            reasons.append("Trading above 20-day SMA")
            score += 1
        if vol_ratio > 1.5:
            reasons.append(f"Volume surge {vol_ratio:.1f}x average")
            score += 2
        if q["pct"] > 1.5:
            reasons.append(f"Up {q['pct']:.2f}% today — momentum play")
            score += 1
        if score >= 3 and len(reasons) >= 2:
            risk = round(q["price"] * 0.015, 1)
            target = round(q["price"] * 1.025, 1)
            sl = round(q["price"] * 0.985, 1)
            suggestions.append({
                "sym": sym, "price": q["price"], "pct": q["pct"],
                "target": target, "sl": sl,
                "reasons": reasons[:3], "score": min(score * 12, 95),
                "risk": "Low" if score >= 5 else "Medium",
            })
    suggestions.sort(key=lambda x: x["score"], reverse=True)
    return suggestions[:5]

# ─── SIDEBAR ──────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="logo-text">Bazaar<span>AI</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Market Intelligence</div>', unsafe_allow_html=True)
    st.markdown("---")

    now_ist = datetime.now(IST)
    market_open = now_ist.weekday() < 5 and (
        (now_ist.hour == 9 and now_ist.minute >= 15) or
        (9 < now_ist.hour < 15) or
        (now_ist.hour == 15 and now_ist.minute <= 30)
    )
    status_color = "🟢" if market_open else "🔴"
    st.markdown(f"{status_color} **{'NSE Open' if market_open else 'Market Closed'}**")
    st.markdown(f'<span class="ist-time">{now_ist.strftime("%I:%M %p IST")}</span>', unsafe_allow_html=True)
    st.caption(f"{now_ist.strftime('%A, %d %B %Y')}")
    st.markdown("---")

    page = st.radio("Navigate", [
        "📊 Dashboard",
        "📈 Indices",
        "🗺 Market Heatmap",
        "⭐ AI Suggestions",
        "🔬 Technical Analysis",
        "💬 News & Sentiment",
        "🎯 Watchlist",
        "🛡 Paper Trading",
        "🔁 Backtesting",
        "📚 Learn",
    ], label_visibility="collapsed")

    st.markdown("---")
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.caption("Data refreshes every 5 minutes automatically")

# ─── HELPERS ──────────────────────────────────────
def color_pct(val):
    if val > 0: return f'<span class="tag-green">▲ {val:+.2f}%</span>'
    if val < 0: return f'<span class="tag-red">▼ {val:.2f}%</span>'
    return f'<span class="tag-amber">— {val:.2f}%</span>'

def fmt_price(p): return f"₹{p:,.2f}"

def signal_badge(s):
    if s in ("Buy",):     return f'<span class="tag-green">BUY</span>'
    if s in ("Sell",):    return f'<span class="tag-red">SELL</span>'
    return f'<span class="tag-amber">{s}</span>'

# ══════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.markdown("## Market Overview")
    st.caption(f"Last updated: {datetime.now(IST).strftime('%I:%M:%S %p IST')}")

    # Index cards
    cols = st.columns(len(INDICES))
    for col, (name, sym) in zip(cols, INDICES.items()):
        df = fetch_index_data(sym, "2d", "1d")
        if not df.empty and len(df) >= 2:
            curr = df["Close"].iloc[-1]
            prev = df["Close"].iloc[-2]
            chg = curr - prev
            pct = (chg / prev) * 100
            col.metric(name, f"{curr:,.2f}", f"{chg:+.2f} ({pct:+.2f}%)",
                      delta_color="normal" if pct >= 0 else "inverse")
        else:
            col.metric(name, "—", "Loading...")

    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("#### Nifty 50 — Intraday Chart")
        period_sel = st.select_slider("Period", ["1d", "5d", "1mo", "3mo", "6mo", "1y"],
                                       value="1d", label_visibility="collapsed")
        interval = "5m" if period_sel == "1d" else "15m" if period_sel == "5d" else "1d"
        df_nifty = fetch_index_data("^NSEI", period_sel, interval)
        if not df_nifty.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_nifty.index, y=df_nifty["Close"],
                mode="lines", line=dict(color="#4e8cff", width=2),
                fill="tozeroy", fillcolor="rgba(78,140,255,0.08)",
                name="Nifty 50"
            ))
            fig.update_layout(**PLOTLY_THEME, height=320, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Chart data loading...")

    with col2:
        st.markdown("#### Sector Performance")
        sector_quotes = {}
        for sector, stocks in SECTORS.items():
            syms = {s: NIFTY50_STOCKS[s] for s in stocks if s in NIFTY50_STOCKS}
            qs = fetch_multiple_quotes(syms)
            avg_pct = np.mean([v["pct"] for v in qs.values() if v["pct"] != 0]) if qs else 0
            sector_quotes[sector] = round(avg_pct, 2)

        df_sec = pd.DataFrame({"Sector": list(sector_quotes.keys()),
                                "Change%": list(sector_quotes.values())}).sort_values("Change%", ascending=True)
        fig_sec = go.Figure(go.Bar(
            x=df_sec["Change%"], y=df_sec["Sector"], orientation="h",
            marker_color=["#22c87a" if v >= 0 else "#f05252" for v in df_sec["Change%"]],
            text=[f"{v:+.2f}%" for v in df_sec["Change%"]], textposition="outside",
        ))
        fig_sec.update_layout(**PLOTLY_THEME, height=320, showlegend=False,
                              xaxis_title="", yaxis_title="")
        st.plotly_chart(fig_sec, use_container_width=True)

    st.markdown("---")
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("#### Top Gainers & Losers")
        quotes = fetch_multiple_quotes(NIFTY50_STOCKS)
        df_q = pd.DataFrame([{"Symbol": k, "Price": f"₹{v['price']:,.2f}",
                               "Change": v["chg"], "Change%": v["pct"]}
                              for k, v in quotes.items() if v["price"] > 0])
        if not df_q.empty:
            df_q = df_q.sort_values("Change%", ascending=False)
            tab1, tab2 = st.tabs(["🟢 Top Gainers", "🔴 Top Losers"])
            with tab1:
                top5 = df_q.head(5)[["Symbol","Price","Change%"]]
                top5["Change%"] = top5["Change%"].apply(lambda x: f"+{x:.2f}%")
                st.dataframe(top5, hide_index=True, use_container_width=True)
            with tab2:
                bot5 = df_q.tail(5)[["Symbol","Price","Change%"]].sort_values("Change%")
                bot5["Change%"] = bot5["Change%"].apply(lambda x: f"{x:.2f}%")
                st.dataframe(bot5, hide_index=True, use_container_width=True)

    with col4:
        st.markdown("#### Market Breadth")
        if not df_q.empty:
            adv = (df_q["Change%"] > 0).sum()
            dec = (df_q["Change%"] < 0).sum()
            unch = (df_q["Change%"] == 0).sum()
            fig_pie = go.Figure(go.Pie(
                labels=["Advances", "Declines", "Unchanged"],
                values=[adv, dec, unch],
                marker_colors=["#22c87a", "#f05252", "#8b93b3"],
                hole=0.6, textinfo="label+value",
            ))
            fig_pie.update_layout(**PLOTLY_THEME, height=280, showlegend=False,
                                  annotations=[dict(text=f"{adv}/{len(df_q)}", x=0.5, y=0.5,
                                                    font_size=16, showarrow=False, font_color="#e8eaf0")])
            st.plotly_chart(fig_pie, use_container_width=True)

# ══════════════════════════════════════════════════
# PAGE: INDICES
# ══════════════════════════════════════════════════
elif page == "📈 Indices":
    st.markdown("## Index Analysis")
    idx_sel = st.selectbox("Select Index", list(INDICES.keys()))
    sym = INDICES[idx_sel]

    c1, c2, c3 = st.columns(3)
    period_map = {"1 Day": ("1d","5m"), "1 Week": ("5d","15m"), "1 Month": ("1mo","1d"),
                  "3 Months": ("3mo","1d"), "1 Year": ("1y","1wk")}
    period_choice = c1.selectbox("Period", list(period_map.keys()))
    p, iv = period_map[period_choice]

    df = fetch_index_data(sym, p, iv)
    if not df.empty:
        curr = df["Close"].iloc[-1]
        prev = df["Close"].iloc[-2] if len(df) > 1 else curr
        chg = curr - prev; pct_chg = (chg/prev)*100
        hi = df["High"].max() if "High" in df.columns else curr
        lo = df["Low"].min()  if "Low"  in df.columns else curr

        c1.metric("Current", f"{curr:,.2f}", f"{chg:+.2f} ({pct_chg:+.2f}%)")
        c2.metric("Period High", f"{hi:,.2f}")
        c3.metric("Period Low",  f"{lo:,.2f}")

        # Candlestick
        if "Open" in df.columns and "High" in df.columns:
            fig = make_subplots(rows=2, cols=1, row_heights=[0.75, 0.25], shared_xaxes=True, vertical_spacing=0.03)
            fig.add_trace(go.Candlestick(
                x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
                increasing_line_color="#22c87a", decreasing_line_color="#f05252",
                increasing_fillcolor="rgba(34,200,122,0.4)", decreasing_fillcolor="rgba(240,82,82,0.4)",
                name=idx_sel
            ), row=1, col=1)
            if "Volume" in df.columns:
                colors = ["#22c87a" if c >= o else "#f05252" for c, o in zip(df["Close"], df["Open"])]
                fig.add_trace(go.Bar(x=df.index, y=df["Volume"], marker_color=colors, name="Volume", opacity=0.6), row=2, col=1)
            theme = dict(PLOTLY_THEME)
            theme["xaxis2"] = theme["xaxis"].copy()
            theme["yaxis2"] = theme["yaxis"].copy()
            fig.update_layout(**theme, height=480, showlegend=False, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        # Technical summary
        st.markdown("#### Technical Indicators")
        df_daily = fetch_index_data(sym, "1y", "1d")
        indicators = compute_indicators(df_daily)
        if indicators:
            icols = st.columns(3)
            for i, (name, (val, sig)) in enumerate(indicators.items()):
                icols[i % 3].markdown(f"**{name}**: `{val}` {signal_badge(sig)}", unsafe_allow_html=True)
    else:
        st.warning("Could not fetch data. Please try again.")

# ══════════════════════════════════════════════════
# PAGE: HEATMAP
# ══════════════════════════════════════════════════
elif page == "🗺 Market Heatmap":
    st.markdown("## Market Heatmap")
    st.caption("Cell size = market cap · Color = daily performance")

    sector_filter = st.selectbox("Filter by Sector", ["All Sectors"] + list(SECTORS.keys()))
    if sector_filter == "All Sectors":
        syms = NIFTY50_STOCKS
    else:
        syms = {s: NIFTY50_STOCKS[s] for s in SECTORS.get(sector_filter, []) if s in NIFTY50_STOCKS}

    with st.spinner("Fetching live prices..."):
        quotes = fetch_multiple_quotes(syms)

    labels, parents, values, colors, texts = [], [], [], [], []
    sector_totals = {}
    for sector, stocks in SECTORS.items():
        sector_syms = [s for s in stocks if s in syms]
        if not sector_syms: continue
        sector_totals[sector] = len(sector_syms)
        labels.append(sector); parents.append(""); values.append(0); colors.append(0); texts.append(sector)
        for s in sector_syms:
            q = quotes.get(s, {})
            labels.append(s); parents.append(sector)
            values.append(max(1, abs(q.get("price", 1)) * 10))
            colors.append(q.get("pct", 0))
            texts.append(f"{s}<br>{q.get('pct', 0):+.2f}%")

    if labels:
        fig = go.Figure(go.Treemap(
            labels=labels, parents=parents, values=values,
            text=texts, textinfo="text",
            marker=dict(
                colors=colors,
                colorscale=[[0, "#7b1a1a"], [0.3, "#f05252"], [0.47, "#2d3a5e"],
                            [0.5, "#1c2845"], [0.53, "#1a4a2e"], [0.7, "#22c87a"], [1, "#0a4a28"]],
                cmin=-3, cmid=0, cmax=3,
                colorbar=dict(
                    title="Chg%", tickfont=dict(color="#8b93b3"),
                    bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)"
                )
            ),
            pathbar_visible=False,
            textfont=dict(family="DM Mono, monospace", size=11, color="#e8eaf0"),
        ))
        fig.update_layout(**PLOTLY_THEME, height=520, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)

    # Volume bar chart
    st.markdown("#### Volume Leaders")
    vol_data = {s: quotes.get(s, {}) for s in list(syms.keys())[:15]}
    fig_vol = go.Figure(go.Bar(
        x=list(vol_data.keys()),
        y=[v.get("pct", 0) for v in vol_data.values()],
        marker_color=["#22c87a" if v.get("pct", 0) >= 0 else "#f05252" for v in vol_data.values()],
        text=[f"{v.get('pct', 0):+.2f}%" for v in vol_data.values()],
        textposition="outside", textfont=dict(size=10),
    ))
    fig_vol.update_layout(**PLOTLY_THEME, height=240, showlegend=False, yaxis_title="% Change")
    st.plotly_chart(fig_vol, use_container_width=True)

# ══════════════════════════════════════════════════
# PAGE: AI SUGGESTIONS
# ══════════════════════════════════════════════════
elif page == "⭐ AI Suggestions":
    st.markdown("## AI Intraday Suggestions")
    st.caption(f"Generated at {datetime.now(IST).strftime('%I:%M %p IST')} · Based on technical signals")

    with st.spinner("Scanning Nifty 50 for opportunities..."):
        quotes = fetch_multiple_quotes(NIFTY50_STOCKS)
        hist_data = {}
        for sym, ticker in list(NIFTY50_STOCKS.items())[:20]:
            df = fetch_index_data(ticker, "3mo", "1d")
            if not df.empty:
                hist_data[sym] = df

    suggestions = generate_suggestions(quotes, hist_data)

    if not suggestions:
        st.info("No strong setups detected right now. Market may be in consolidation. Check back after 10:30 AM.")
    else:
        st.success(f"Found {len(suggestions)} potential opportunities today")
        for sug in suggestions:
            with st.expander(f"{'🟢' if sug['pct'] >= 0 else '🔴'} {sug['sym']} — {fmt_price(sug['price'])} ({sug['pct']:+.2f}%) · Confidence: {sug['score']}%", expanded=True):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Entry", fmt_price(sug["price"]))
                c2.metric("Target 🎯", fmt_price(sug["target"]))
                c3.metric("Stop Loss 🛑", fmt_price(sug["sl"]))
                c4.metric("Risk Level", sug["risk"])

                st.markdown("**Reasoning:**")
                for r in sug["reasons"]:
                    st.markdown(f"- {r}")

                rr = round((sug["target"] - sug["price"]) / (sug["price"] - sug["sl"]), 1)
                st.caption(f"Risk:Reward = 1:{rr} · Potential gain: {((sug['target']/sug['price'])-1)*100:.2f}% · Max loss: {((sug['sl']/sug['price'])-1)*100:.2f}%")

    # Confidence chart
    if suggestions:
        st.markdown("---")
        st.markdown("#### Signal Strength")
        fig = go.Figure(go.Bar(
            x=[s["sym"] for s in suggestions],
            y=[s["score"] for s in suggestions],
            marker_color=["#22c87a" if s["score"] > 75 else "#f5a623" if s["score"] > 60 else "#f05252" for s in suggestions],
            text=[f"{s['score']}%" for s in suggestions],
            textposition="outside", borderradius=4,
        ))
        fig.update_layout(**PLOTLY_THEME, height=240, showlegend=False, yaxis=dict(range=[0, 105]))
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════
# PAGE: TECHNICAL ANALYSIS
# ══════════════════════════════════════════════════
elif page == "🔬 Technical Analysis":
    st.markdown("## Technical Analysis")

    col_a, col_b = st.columns([1, 3])
    with col_a:
        stock_sel = st.selectbox("Stock / Index", ["NIFTY 50 (^NSEI)"] + [f"{k} ({v})" for k, v in NIFTY50_STOCKS.items()])
        ta_period  = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y"])

    sym_clean = stock_sel.split("(")[1].rstrip(")")
    with st.spinner("Computing indicators..."):
        df = fetch_index_data(sym_clean, ta_period, "1d")

    if df.empty:
        st.warning("No data available.")
    else:
        close = df["Close"]
        # Compute
        rsi  = compute_rsi(close)
        macd_line, sig_line, macd_hist = compute_macd(close)
        bb_upper, bb_mid, bb_lower = compute_bollinger(close)

        # Indicator summary
        indicators = compute_indicators(df)
        st.markdown("#### Indicator Summary")
        icols = st.columns(3)
        for i, (name, (val, sig)) in enumerate(indicators.items()):
            icols[i%3].markdown(f"**{name}**: `{val}`  {signal_badge(sig)}", unsafe_allow_html=True)

        st.markdown("---")

        # Price + BB
        st.markdown("#### Price & Bollinger Bands")
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=df.index, y=bb_upper, line=dict(color="rgba(240,82,82,.4)", width=1, dash="dot"), name="Upper BB"))
        fig1.add_trace(go.Scatter(x=df.index, y=bb_mid,   line=dict(color="#f5a623", width=1.5, dash="dash"), name="SMA 20"))
        fig1.add_trace(go.Scatter(x=df.index, y=bb_lower, line=dict(color="rgba(34,200,122,.4)", width=1, dash="dot"),
                                  fill="tonexty", fillcolor="rgba(78,140,255,.04)", name="Lower BB"))
        fig1.add_trace(go.Scatter(x=df.index, y=close, line=dict(color="#4e8cff", width=2), name="Price"))
        fig1.update_layout(**PLOTLY_THEME, height=320, showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)

        # RSI
        st.markdown("#### RSI (14)")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df.index, y=rsi, line=dict(color="#7b6cff", width=2), name="RSI", fill="tozeroy", fillcolor="rgba(123,108,255,0.06)"))
        fig2.add_hline(y=70, line_dash="dot", line_color="rgba(240,82,82,.5)", annotation_text="Overbought 70")
        fig2.add_hline(y=30, line_dash="dot", line_color="rgba(34,200,122,.5)", annotation_text="Oversold 30")
        fig2.update_layout(**PLOTLY_THEME, height=200, yaxis=dict(range=[0, 100]), showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

        # MACD
        st.markdown("#### MACD")
        fig3 = make_subplots(rows=1, cols=1)
        bar_colors = ["#22c87a" if v >= 0 else "#f05252" for v in macd_hist]
        fig3.add_trace(go.Bar(x=df.index, y=macd_hist, marker_color=bar_colors, name="Histogram", opacity=0.7))
        fig3.add_trace(go.Scatter(x=df.index, y=macd_line, line=dict(color="#4e8cff", width=2), name="MACD"))
        fig3.add_trace(go.Scatter(x=df.index, y=sig_line,  line=dict(color="#f5a623", width=1.5, dash="dash"), name="Signal"))
        fig3.update_layout(**PLOTLY_THEME, height=240, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════════
# PAGE: NEWS & SENTIMENT  
# ══════════════════════════════════════════════════
elif page == "💬 News & Sentiment":
    st.markdown("## News & Sentiment")
    st.info("💡 Live news sentiment requires a news API key. Showing simulated scores based on price momentum.")

    quotes = fetch_multiple_quotes(NIFTY50_STOCKS)
    df_q = pd.DataFrame([{"Symbol": k, "Price": v["price"], "Change%": v["pct"]}
                          for k, v in quotes.items() if v["price"] > 0])

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Market Sentiment Gauge")
        bullish = int((df_q["Change%"] > 0.5).sum() / len(df_q) * 100) if len(df_q) > 0 else 50
        bearish = int((df_q["Change%"] < -0.5).sum() / len(df_q) * 100) if len(df_q) > 0 else 30
        neutral = 100 - bullish - bearish
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number",
            value=bullish,
            title={"text": "Bullish %", "font": {"color": "#8b93b3", "size": 13}},
            gauge=dict(
                axis=dict(range=[0, 100], tickcolor="#5a6285"),
                bar=dict(color="#22c87a" if bullish > 50 else "#f05252"),
                steps=[
                    dict(range=[0, 35], color="rgba(240,82,82,.15)"),
                    dict(range=[35, 65], color="rgba(245,166,35,.1)"),
                    dict(range=[65, 100], color="rgba(34,200,122,.15)"),
                ],
                threshold=dict(line=dict(color="#4e8cff", width=2), thickness=0.75, value=50)
            ),
            number=dict(suffix="%", font=dict(color="#e8eaf0", family="DM Mono"))
        ))
        fig_g.update_layout(**PLOTLY_THEME, height=260)
        st.plotly_chart(fig_g, use_container_width=True)
        st.caption(f"Bullish: {bullish}% · Neutral: {neutral}% · Bearish: {bearish}%")

    with col2:
        st.markdown("#### Sector Sentiment")
        for sector, stocks in SECTORS.items():
            syms = {s: NIFTY50_STOCKS[s] for s in stocks if s in NIFTY50_STOCKS}
            qs = fetch_multiple_quotes(syms)
            avg = np.mean([v["pct"] for v in qs.values() if v["pct"] != 0]) if qs else 0
            score = min(max((avg + 3) / 6, 0), 1)
            label = "🟢 Bullish" if avg > 0.3 else "🔴 Bearish" if avg < -0.3 else "🟡 Neutral"
            st.markdown(f"**{sector}** — {label} `{avg:+.2f}%`")
            st.progress(score)

    st.markdown("---")
    st.markdown("#### Price Momentum as Sentiment Proxy")
    if not df_q.empty:
        df_sorted = df_q.sort_values("Change%", ascending=False)
        fig_sent = go.Figure(go.Bar(
            x=df_sorted["Symbol"], y=df_sorted["Change%"],
            marker_color=["#22c87a" if v > 0 else "#f05252" for v in df_sorted["Change%"]],
            text=[f"{v:+.2f}%" for v in df_sorted["Change%"]], textposition="outside",
        ))
        fig_sent.update_layout(**PLOTLY_THEME, height=300, showlegend=False, yaxis_title="Daily Change %")
        st.plotly_chart(fig_sent, use_container_width=True)

# ══════════════════════════════════════════════════
# PAGE: WATCHLIST
# ══════════════════════════════════════════════════
elif page == "🎯 Watchlist":
    st.markdown("## Watchlist & Alerts")

    if "watchlist" not in st.session_state:
        st.session_state.watchlist = ["INFY", "TCS", "RELIANCE", "HDFCBANK"]

    col1, col2 = st.columns([2, 1])
    with col2:
        st.markdown("#### Add to Watchlist")
        new_sym = st.selectbox("Stock", [s for s in NIFTY50_STOCKS if s not in st.session_state.watchlist])
        if st.button("+ Add", use_container_width=True):
            st.session_state.watchlist.append(new_sym)
            st.rerun()

    with col1:
        st.markdown("#### My Watchlist")
        if st.session_state.watchlist:
            watch_syms = {s: NIFTY50_STOCKS[s] for s in st.session_state.watchlist if s in NIFTY50_STOCKS}
            quotes = fetch_multiple_quotes(watch_syms)
            for sym in st.session_state.watchlist:
                q = quotes.get(sym, {})
                c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
                c1.markdown(f"**{sym}**")
                c2.markdown(f"`₹{q.get('price', 0):,.2f}`")
                c3.markdown(color_pct(q.get("pct", 0)), unsafe_allow_html=True)
                if c4.button("✕", key=f"rm_{sym}"):
                    st.session_state.watchlist.remove(sym)
                    st.rerun()

    # Mini charts for watchlist
    if st.session_state.watchlist:
        st.markdown("---")
        st.markdown("#### 1-Month Sparklines")
        wcols = st.columns(min(len(st.session_state.watchlist), 4))
        for i, sym in enumerate(st.session_state.watchlist[:4]):
            ticker = NIFTY50_STOCKS.get(sym, "")
            df_w = fetch_index_data(ticker, "1mo", "1d")
            if not df_w.empty:
                fig_w = go.Figure(go.Scatter(
                    y=df_w["Close"], mode="lines",
                    line=dict(color="#4e8cff", width=1.5),
                    fill="tozeroy", fillcolor="rgba(78,140,255,0.06)"
                ))
                fig_w.update_layout(**PLOTLY_THEME, height=120,
                                    xaxis=dict(visible=False), yaxis=dict(visible=False),
                                    margin=dict(l=0, r=0, t=20, b=0))
                fig_w.update_layout(title=dict(text=sym, font=dict(size=12, color="#e8eaf0"), x=0.05))
                wcols[i].plotly_chart(fig_w, use_container_width=True)

# ══════════════════════════════════════════════════
# PAGE: PAPER TRADING
# ══════════════════════════════════════════════════
elif page == "🛡 Paper Trading":
    st.markdown("## Paper Trading Simulator")

    if "pt_balance"   not in st.session_state: st.session_state.pt_balance   = 500000.0
    if "pt_positions" not in st.session_state: st.session_state.pt_positions = {}
    if "pt_trades"    not in st.session_state: st.session_state.pt_trades    = []

    # Live prices for positions
    pos_syms = {s: NIFTY50_STOCKS[s] for s in st.session_state.pt_positions if s in NIFTY50_STOCKS}
    live_prices = fetch_multiple_quotes(pos_syms) if pos_syms else {}

    # Stats
    total_pnl = sum(
        (live_prices.get(s, {}).get("price", pos["buy_price"]) - pos["buy_price"]) * pos["qty"]
        for s, pos in st.session_state.pt_positions.items()
    )
    portfolio_val = st.session_state.pt_balance + sum(
        live_prices.get(s, {}).get("price", pos["buy_price"]) * pos["qty"]
        for s, pos in st.session_state.pt_positions.items()
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Cash Balance",     f"₹{st.session_state.pt_balance:,.0f}")
    m2.metric("Portfolio Value",  f"₹{portfolio_val:,.0f}")
    m3.metric("Unrealised P&L",   f"₹{total_pnl:+,.0f}", delta_color="normal" if total_pnl >= 0 else "inverse")
    m4.metric("Open Positions",   len(st.session_state.pt_positions))

    st.markdown("---")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("#### Place Order")
        trade_sym   = st.selectbox("Symbol", list(NIFTY50_STOCKS.keys()))
        trade_qty   = st.number_input("Quantity", min_value=1, value=10)
        trade_type  = st.radio("Order Side", ["BUY", "SELL"], horizontal=True)

        live_q = fetch_multiple_quotes({trade_sym: NIFTY50_STOCKS[trade_sym]})
        ltp = live_q.get(trade_sym, {}).get("price", 0)
        st.metric("Current LTP", f"₹{ltp:,.2f}")
        order_val = ltp * trade_qty
        st.caption(f"Order value: ₹{order_val:,.2f}")

        if st.button(f"{'BUY 🟢' if trade_type == 'BUY' else 'SELL 🔴'} {trade_sym}", use_container_width=True):
            if trade_type == "BUY":
                if st.session_state.pt_balance >= order_val:
                    if trade_sym in st.session_state.pt_positions:
                        pos = st.session_state.pt_positions[trade_sym]
                        total_qty = pos["qty"] + trade_qty
                        avg_price = (pos["buy_price"] * pos["qty"] + ltp * trade_qty) / total_qty
                        st.session_state.pt_positions[trade_sym] = {"qty": total_qty, "buy_price": avg_price}
                    else:
                        st.session_state.pt_positions[trade_sym] = {"qty": trade_qty, "buy_price": ltp}
                    st.session_state.pt_balance -= order_val
                    st.session_state.pt_trades.append({"sym": trade_sym, "side": "BUY", "qty": trade_qty, "price": ltp, "time": datetime.now(IST).strftime("%H:%M")})
                    st.success(f"✅ BUY {trade_qty} {trade_sym} @ ₹{ltp:,.2f}")
                else:
                    st.error("Insufficient balance")
            else:
                if trade_sym in st.session_state.pt_positions:
                    pos = st.session_state.pt_positions[trade_sym]
                    if pos["qty"] >= trade_qty:
                        pnl = (ltp - pos["buy_price"]) * trade_qty
                        st.session_state.pt_balance += order_val
                        if pos["qty"] == trade_qty:
                            del st.session_state.pt_positions[trade_sym]
                        else:
                            st.session_state.pt_positions[trade_sym]["qty"] -= trade_qty
                        st.session_state.pt_trades.append({"sym": trade_sym, "side": "SELL", "qty": trade_qty, "price": ltp, "pnl": pnl, "time": datetime.now(IST).strftime("%H:%M")})
                        st.success(f"✅ SELL {trade_qty} {trade_sym} @ ₹{ltp:,.2f} | P&L: ₹{pnl:+,.2f}")
                    else:
                        st.error("Not enough shares")
                else:
                    st.error("No position in this stock")

    with col2:
        st.markdown("#### Open Positions")
        if st.session_state.pt_positions:
            rows = []
            for s, pos in st.session_state.pt_positions.items():
                lp = live_prices.get(s, {}).get("price", pos["buy_price"])
                pnl = (lp - pos["buy_price"]) * pos["qty"]
                rows.append({"Symbol": s, "Qty": pos["qty"],
                             "Avg Buy": f"₹{pos['buy_price']:,.2f}",
                             "LTP": f"₹{lp:,.2f}",
                             "P&L": f"{'+'if pnl>=0 else ''}₹{pnl:,.2f}"})
            st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
        else:
            st.info("No open positions. Place a trade to get started!")

        if st.session_state.pt_trades:
            st.markdown("#### Trade History")
            df_trades = pd.DataFrame(st.session_state.pt_trades[-10:])
            st.dataframe(df_trades, hide_index=True, use_container_width=True)

    if st.button("🔄 Reset Portfolio", type="secondary"):
        st.session_state.pt_balance = 500000.0
        st.session_state.pt_positions = {}
        st.session_state.pt_trades = []
        st.rerun()

# ══════════════════════════════════════════════════
# PAGE: BACKTESTING
# ══════════════════════════════════════════════════
elif page == "🔁 Backtesting":
    st.markdown("## Strategy Backtesting")

    col1, col2, col3, col4 = st.columns(4)
    bt_sym    = col1.selectbox("Stock", list(NIFTY50_STOCKS.keys()), index=0)
    bt_strat  = col2.selectbox("Strategy", ["SMA Crossover", "RSI Mean Reversion", "MACD Crossover"])
    bt_period = col3.selectbox("Period", ["6mo", "1y", "2y"], index=1)
    initial_cap = col4.number_input("Capital (₹)", value=100000, step=10000)

    if st.button("▶ Run Backtest", type="primary"):
        with st.spinner("Running backtest..."):
            ticker = NIFTY50_STOCKS[bt_sym]
            df = fetch_index_data(ticker, bt_period, "1d")

            if df.empty:
                st.error("Could not fetch data.")
            else:
                close = df["Close"].copy()
                signals = pd.Series(0, index=df.index)

                if bt_strat == "SMA Crossover":
                    sma_fast = close.rolling(20).mean()
                    sma_slow = close.rolling(50).mean()
                    signals[sma_fast > sma_slow] = 1
                    signals[sma_fast <= sma_slow] = -1
                elif bt_strat == "RSI Mean Reversion":
                    rsi = compute_rsi(close)
                    signals[rsi < 35] = 1
                    signals[rsi > 65] = -1
                elif bt_strat == "MACD Crossover":
                    macd_l, sig_l, _ = compute_macd(close)
                    signals[macd_l > sig_l] = 1
                    signals[macd_l <= sig_l] = -1

                position  = signals.shift(1).fillna(0)
                daily_ret = close.pct_change()
                strat_ret = position * daily_ret
                equity    = (1 + strat_ret).cumprod() * initial_cap
                bh_equity = (1 + daily_ret).cumprod() * initial_cap

                total_ret  = (equity.iloc[-1] / initial_cap - 1) * 100
                bh_ret     = (bh_equity.iloc[-1] / initial_cap - 1) * 100
                win_days   = (strat_ret > 0).sum()
                total_days = (strat_ret != 0).sum()
                win_rate   = win_days / total_days * 100 if total_days > 0 else 0
                sharpe     = strat_ret.mean() / strat_ret.std() * np.sqrt(252) if strat_ret.std() > 0 else 0
                rolling_max = equity.cummax()
                drawdown   = (equity - rolling_max) / rolling_max * 100
                max_dd     = drawdown.min()

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Total Return",  f"{total_ret:+.2f}%", f"vs B&H {bh_ret:+.2f}%")
                m2.metric("Sharpe Ratio",  f"{sharpe:.2f}")
                m3.metric("Win Rate",      f"{win_rate:.1f}%")
                m4.metric("Max Drawdown",  f"{max_dd:.2f}%")

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=equity.index,    y=equity,    mode="lines", name="Strategy",
                                         line=dict(color="#4e8cff", width=2)))
                fig.add_trace(go.Scatter(x=bh_equity.index, y=bh_equity, mode="lines", name="Buy & Hold",
                                         line=dict(color="#8b93b3", width=1.5, dash="dash")))
                fig.update_layout(**PLOTLY_THEME, height=360, title=f"{bt_strat} — {bt_sym} Equity Curve")
                st.plotly_chart(fig, use_container_width=True)

                st.markdown("#### Drawdown")
                fig2 = go.Figure(go.Scatter(x=drawdown.index, y=drawdown, mode="lines", fill="tozeroy",
                                             line=dict(color="#f05252", width=1.5), fillcolor="rgba(240,82,82,.1)"))
                fig2.update_layout(**PLOTLY_THEME, height=200, showlegend=False, yaxis_title="Drawdown %")
                st.plotly_chart(fig2, use_container_width=True)

# ══════════════════════════════════════════════════
# PAGE: LEARN
# ══════════════════════════════════════════════════
elif page == "📚 Learn":
    st.markdown("## Trading Education")
    st.caption("Master concepts that drive Indian markets")

    topics = {
        "📊 Candlestick Patterns": ("Beginner", """
**Key patterns to know:**
- **Doji**: Open = Close → indecision, possible reversal
- **Hammer**: Small body, long lower wick → bullish reversal at support
- **Engulfing**: Larger candle engulfs previous → strong momentum signal
- **Morning Star / Evening Star**: 3-candle reversal patterns

In NSE/BSE, these are most reliable on daily and 15-min charts during high-volume periods (9:15–10:30 AM, 2:00–3:30 PM).
"""),
        "📈 RSI (Relative Strength Index)": ("Beginner", """
**Formula**: RSI = 100 − 100/(1 + RS) where RS = Avg Gain/Avg Loss over 14 periods

**Interpretation**:
- RSI > 70 → Overbought (potential sell signal)
- RSI < 30 → Oversold (potential buy signal)  
- RSI crossing 50 from below → bullish momentum building

**Nifty-specific**: During strong bull markets (like 2021–2024), RSI can stay overbought (70–80) for extended periods. Use 80/20 levels instead.
"""),
        "〰️ Moving Averages": ("Beginner", """
**Types used in Indian markets**:
- **20 EMA**: Intraday & swing trading reference
- **50 SMA**: Medium-term trend
- **200 SMA**: Bull/Bear market separator ("Death Cross" / "Golden Cross")

**Nifty 50 golden cross (50 SMA crosses above 200 SMA)** has been a reliable bull signal historically, generating 15–25% returns within 6 months.
"""),
        "⚡ MACD Strategy": ("Intermediate", """
**Components**: MACD Line (12 EMA − 26 EMA), Signal Line (9 EMA of MACD), Histogram

**Signals**:
- MACD crosses above Signal → BUY
- MACD crosses below Signal → SELL
- Histogram expanding = strengthening trend
- Divergence between price & MACD → potential reversal

**Best used on**: Daily charts for positional trades, 15-min for intraday.
"""),
        "🛡 Risk Management": ("Essential", """
**Golden rules for Indian retail traders**:

1. **1% Rule**: Never risk more than 1–2% of capital on a single trade
2. **Stop Loss**: Always pre-defined before entry. For Nifty stocks, 1–1.5% SL is typical intraday
3. **Risk:Reward**: Minimum 1:2 (risk ₹100 to make ₹200)
4. **Position Sizing**: Capital × Risk% ÷ (Entry − Stop Loss)
5. **Avoid overtrading**: 3–5 quality trades > 20 mediocre ones

**F&O Warning**: 90% of F&O traders lose money. Start with cash segment.
"""),
        "🔍 Fundamental Analysis": ("Intermediate", """
**Key ratios for NSE/BSE stocks**:

| Ratio | Good Range | Caution |
|-------|-----------|---------|
| P/E   | < Sector avg | > 40 for non-growth |
| P/B   | < 3 for value | > 10 |
| ROE   | > 15% | < 10% |
| Debt/Equity | < 1 | > 2 |
| ROCE  | > 20% | < 12% |

**Best free sources**: NSE website, BSE filings, Screener.in, Tickertape
"""),
    }

    for title, (level, content) in topics.items():
        badge = "🟢" if level == "Beginner" else "🟡" if level == "Intermediate" else "🔴" if level == "Advanced" else "⭐"
        with st.expander(f"{title}  ·  {badge} {level}"):
            st.markdown(content)

# ─── FOOTER ───────────────────────────────────────
st.markdown("---")
st.caption("BazaarAI · Data via Yahoo Finance · For educational purposes only · Not financial advice · Refresh every 5 min")

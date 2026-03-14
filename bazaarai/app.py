import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import pytz

st.set_page_config(
    page_title="BazaarAI — Indian Market Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── GLOBAL CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap');

/* ── Reset & Base ── */
html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background-color: #0a0f1e !important;
    color: #e8eaf0 !important;
}
.block-container { padding: 1.5rem 2rem 3rem !important; max-width: 1400px !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #0f1729 !important;
    border-right: 1px solid rgba(99,132,199,0.15) !important;
    min-width: 230px !important;
}
section[data-testid="stSidebar"] > div { padding-top: 1rem !important; }
section[data-testid="stSidebar"] * { color: #e8eaf0 !important; }
section[data-testid="stSidebar"] .stRadio label {
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #8b93b3 !important;
    padding: 6px 8px !important;
    border-radius: 8px !important;
    cursor: pointer !important;
}
section[data-testid="stSidebar"] .stRadio label:hover { color: #e8eaf0 !important; background: rgba(78,140,255,0.08) !important; }

/* ── Metric Cards ── */
div[data-testid="metric-container"] {
    background: #12192e !important;
    border: 1px solid rgba(99,132,199,0.18) !important;
    border-radius: 12px !important;
    padding: 18px 20px !important;
}
div[data-testid="metric-container"] label {
    color: #5a6285 !important;
    font-size: 10px !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    font-weight: 600 !important;
}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 22px !important;
    font-weight: 500 !important;
    color: #e8eaf0 !important;
}
div[data-testid="metric-container"] div[data-testid="stMetricDelta"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 12px !important;
}

/* ── Tabs ── */
div[data-testid="stTabs"] { border-bottom: 1px solid rgba(99,132,199,0.15) !important; }
div[data-testid="stTabs"] button {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #8b93b3 !important;
    background: transparent !important;
    border: none !important;
    padding: 10px 16px !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #4e8cff !important;
    border-bottom: 2px solid #4e8cff !important;
}
div[data-testid="stTabs"] button:hover { color: #e8eaf0 !important; }

/* ── Inputs & Selects ── */
div[data-baseweb="select"] > div {
    background: #12192e !important;
    border: 1px solid rgba(99,132,199,0.25) !important;
    border-radius: 8px !important;
    color: #e8eaf0 !important;
}
input, textarea {
    background: #12192e !important;
    border: 1px solid rgba(99,132,199,0.25) !important;
    border-radius: 8px !important;
    color: #e8eaf0 !important;
}
.stSelectbox label, .stMultiSelect label, .stNumberInput label, .stRadio > label {
    font-size: 11px !important;
    color: #5a6285 !important;
    text-transform: uppercase !important;
    letter-spacing: .5px !important;
    font-weight: 600 !important;
}

/* ── Buttons ── */
.stButton > button {
    background: transparent !important;
    border: 1px solid rgba(99,132,199,0.3) !important;
    border-radius: 8px !important;
    color: #e8eaf0 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 6px 16px !important;
    transition: all .15s !important;
}
.stButton > button:hover {
    background: rgba(78,140,255,0.12) !important;
    border-color: #4e8cff !important;
    color: #4e8cff !important;
}
.stButton > button[kind="primary"] {
    background: #4e8cff !important;
    border-color: #4e8cff !important;
    color: #fff !important;
}
.stButton > button[kind="primary"]:hover { background: #3a7aef !important; }

/* ── Dataframe ── */
div[data-testid="stDataFrame"] {
    background: #12192e !important;
    border: 1px solid rgba(99,132,199,0.15) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}
div[data-testid="stDataFrame"] th {
    background: #0f1729 !important;
    color: #5a6285 !important;
    font-size: 10px !important;
    text-transform: uppercase !important;
    letter-spacing: .5px !important;
}
div[data-testid="stDataFrame"] td { color: #e8eaf0 !important; font-size: 13px !important; }

/* ── Progress bar ── */
div[data-testid="stProgress"] > div > div { background: #12192e !important; }
div[data-testid="stProgress"] > div > div > div { background: #4e8cff !important; }

/* ── Expander ── */
details {
    background: #12192e !important;
    border: 1px solid rgba(99,132,199,0.18) !important;
    border-radius: 12px !important;
    margin-bottom: 10px !important;
}
details summary {
    color: #e8eaf0 !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    padding: 14px 18px !important;
}
details > div { padding: 0 18px 16px !important; }

/* ── Alerts/Info ── */
div[data-testid="stAlert"] {
    background: rgba(78,140,255,0.08) !important;
    border: 1px solid rgba(78,140,255,0.25) !important;
    border-radius: 10px !important;
    color: #e8eaf0 !important;
}

/* ── Dividers ── */
hr { border-color: rgba(99,132,199,0.12) !important; }

/* ── Custom HTML components ── */
.idx-card {
    background: #12192e;
    border: 1px solid rgba(99,132,199,0.18);
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 0;
}
.idx-card.up   { border-left: 3px solid #22c87a; }
.idx-card.down { border-left: 3px solid #f05252; }
.idx-name  { font-size:10px; color:#5a6285; text-transform:uppercase; letter-spacing:1px; margin-bottom:6px; font-weight:600; }
.idx-value { font-family:'DM Mono',monospace; font-size:24px; font-weight:500; margin-bottom:8px; }
.badge-up  { background:rgba(34,200,122,.15); color:#22c87a; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:700; font-family:'DM Mono',monospace; }
.badge-dn  { background:rgba(240,82,82,.15);  color:#f05252; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:700; font-family:'DM Mono',monospace; }
.badge-neu { background:rgba(139,147,179,.15);color:#8b93b3; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:700; font-family:'DM Mono',monospace; }

.sug-card {
    background: #12192e;
    border: 1px solid rgba(99,132,199,0.18);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 12px;
    position: relative;
    overflow: hidden;
}
.sug-card-top-buy  { height:3px; background:linear-gradient(90deg,#22c87a,#1dd9b2); margin:-20px -20px 16px -20px; }
.sug-card-top-watch{ height:3px; background:linear-gradient(90deg,#f5a623,#f79c42); margin:-20px -20px 16px -20px; }
.sug-ticker { font-family:'DM Mono',monospace; font-size:20px; font-weight:500; }
.sug-name   { font-size:12px; color:#8b93b3; margin-top:2px; }
.signal-buy { background:rgba(34,200,122,.15); color:#22c87a; border:1px solid rgba(34,200,122,.3); padding:4px 12px; border-radius:20px; font-size:11px; font-weight:700; letter-spacing:.5px; }
.signal-watch{background:rgba(245,166,35,.15); color:#f5a623; border:1px solid rgba(245,166,35,.3); padding:4px 12px; border-radius:20px; font-size:11px; font-weight:700; letter-spacing:.5px; }
.lvl-box { background:#0f1729; border-radius:8px; padding:12px; text-align:center; }
.lvl-label{ font-size:9px; color:#5a6285; text-transform:uppercase; letter-spacing:.5px; margin-bottom:4px; font-weight:600; }
.lvl-val-e { font-family:'DM Mono',monospace; font-size:14px; font-weight:500; color:#4e8cff; }
.lvl-val-t { font-family:'DM Mono',monospace; font-size:14px; font-weight:500; color:#22c87a; }
.lvl-val-s { font-family:'DM Mono',monospace; font-size:14px; font-weight:500; color:#f05252; }
.tag-pill  { display:inline-block; background:rgba(78,140,255,.1); color:#4e8cff; border-radius:4px; font-size:10px; font-weight:600; padding:2px 8px; margin:2px 2px 0 0; }
.risk-dot-e{ display:inline-block; width:9px; height:9px; border-radius:50%; background:#22c87a; margin-right:3px; }
.risk-dot-m{ display:inline-block; width:9px; height:9px; border-radius:50%; background:#f5a623; margin-right:3px; }
.risk-dot-h{ display:inline-block; width:9px; height:9px; border-radius:50%; background:#f05252; margin-right:3px; }
.risk-dot-e{ display:inline-block; width:9px; height:9px; border-radius:50%; background:rgba(99,132,199,0.2); margin-right:3px; }

.ind-row { display:flex; align-items:center; justify-content:space-between; padding:9px 0; border-bottom:1px solid rgba(99,132,199,0.08); }
.ind-row:last-child { border-bottom:none; }
.ind-name { font-size:13px; color:#8b93b3; }
.ind-val  { font-family:'DM Mono',monospace; font-size:13px; }
.sig-buy  { background:rgba(34,200,122,.18); color:#22c87a; font-size:10px; font-weight:700; padding:2px 8px; border-radius:4px; text-transform:uppercase; letter-spacing:.5px; }
.sig-sell { background:rgba(240,82,82,.18);  color:#f05252; font-size:10px; font-weight:700; padding:2px 8px; border-radius:4px; text-transform:uppercase; letter-spacing:.5px; }
.sig-neu  { background:rgba(139,147,179,.18);color:#8b93b3; font-size:10px; font-weight:700; padding:2px 8px; border-radius:4px; text-transform:uppercase; letter-spacing:.5px; }

.sec-row { display:flex; align-items:center; gap:12px; padding:7px 0; border-bottom:1px solid rgba(99,132,199,0.07); }
.sec-row:last-child{ border-bottom:none; }
.sec-name { font-size:12px; width:130px; flex-shrink:0; color:#8b93b3; }
.sec-bar-bg{ flex:1; height:5px; background:#1c2845; border-radius:3px; overflow:hidden; }
.sec-bar-g { height:100%; border-radius:3px; background:#22c87a; }
.sec-bar-r { height:100%; border-radius:3px; background:#f05252; }
.sec-pct  { font-family:'DM Mono',monospace; font-size:11px; width:54px; text-align:right; flex-shrink:0; }

.section-hdr{ font-size:10px; letter-spacing:1.2px; text-transform:uppercase; color:#5a6285; font-weight:600; margin-bottom:10px; }
.card-wrap{ background:#12192e; border:1px solid rgba(99,132,199,0.18); border-radius:12px; padding:20px; }
.news-item{ display:flex; align-items:flex-start; gap:12px; padding:11px 0; border-bottom:1px solid rgba(99,132,199,0.08); }
.news-item:last-child{ border-bottom:none; }
.news-dot-pos{ width:8px; height:8px; border-radius:50%; background:#22c87a; flex-shrink:0; margin-top:5px; }
.news-dot-neg{ width:8px; height:8px; border-radius:50%; background:#f05252; flex-shrink:0; margin-top:5px; }
.news-dot-neu{ width:8px; height:8px; border-radius:50%; background:#f5a623; flex-shrink:0; margin-top:5px; }
.news-hl  { font-size:13px; line-height:1.5; }
.news-src { font-size:11px; color:#5a6285; margin-top:3px; }
.news-score-pos{ font-family:'DM Mono',monospace; font-size:12px; background:rgba(34,200,122,.12); color:#22c87a; padding:2px 8px; border-radius:4px; flex-shrink:0; }
.news-score-neg{ font-family:'DM Mono',monospace; font-size:12px; background:rgba(240,82,82,.12); color:#f05252; padding:2px 8px; border-radius:4px; flex-shrink:0; }
.news-score-neu{ font-family:'DM Mono',monospace; font-size:12px; background:rgba(139,147,179,.12); color:#8b93b3; padding:2px 8px; border-radius:4px; flex-shrink:0; }

.logo-main { font-family:'DM Serif Display',serif; font-size:26px; color:#e8eaf0; }
.logo-main span { color:#4e8cff; }
.logo-sub  { font-size:10px; color:#5a6285; letter-spacing:2px; text-transform:uppercase; margin-top:2px; }
.ist-clock { font-family:'DM Mono',monospace; font-size:13px; color:#1dd9b2; }
.page-title{ font-family:'DM Serif Display',serif; font-size:28px; color:#e8eaf0; margin-bottom:4px; }
.page-sub  { font-size:12px; color:#5a6285; margin-bottom:1.2rem; }
</style>
""", unsafe_allow_html=True)

# ── CONSTANTS ─────────────────────────────────────────────────────────────────
IST = pytz.timezone("Asia/Kolkata")

INDICES = {
    "NIFTY 50":     "^NSEI",
    "SENSEX":       "^BSESN",
    "BANK NIFTY":   "^NSEBANK",
    "NIFTY IT":     "^CNXIT",
    "NIFTY MIDCAP": "^NSEMDCP50",
}

NIFTY50 = {
    "RELIANCE":"RELIANCE.NS","TCS":"TCS.NS","INFY":"INFY.NS",
    "HDFCBANK":"HDFCBANK.NS","ICICIBANK":"ICICIBANK.NS",
    "HINDUNILVR":"HINDUNILVR.NS","SBIN":"SBIN.NS",
    "BAJFINANCE":"BAJFINANCE.NS","KOTAKBANK":"KOTAKBANK.NS",
    "BHARTIARTL":"BHARTIARTL.NS","WIPRO":"WIPRO.NS",
    "SUNPHARMA":"SUNPHARMA.NS","AXISBANK":"AXISBANK.NS",
    "MARUTI":"MARUTI.NS","NESTLEIND":"NESTLEIND.NS",
    "LTIM":"LTIM.NS","TITAN":"TITAN.NS","TECHM":"TECHM.NS",
    "HCLTECH":"HCLTECH.NS","DRREDDY":"DRREDDY.NS",
    "DIVISLAB":"DIVISLAB.NS","TATASTEEL":"TATASTEEL.NS",
    "JSWSTEEL":"JSWSTEEL.NS","ONGC":"ONGC.NS",
    "COALINDIA":"COALINDIA.NS","ASIANPAINT":"ASIANPAINT.NS",
    "M&M":"M&M.NS","ITC":"ITC.NS","CIPLA":"CIPLA.NS",
    "ADANIENT":"ADANIENT.NS","ADANIPORTS":"ADANIPORTS.NS",
    "NTPC":"NTPC.NS","POWERGRID":"POWERGRID.NS",
    "ULTRACEMCO":"ULTRACEMCO.NS","BAJAJFINSV":"BAJAJFINSV.NS",
}

SECTORS = {
    "IT":      ["TCS","INFY","WIPRO","HCLTECH","TECHM","LTIM"],
    "Banking": ["HDFCBANK","ICICIBANK","SBIN","AXISBANK","KOTAKBANK"],
    "Pharma":  ["SUNPHARMA","DRREDDY","DIVISLAB","CIPLA"],
    "Auto":    ["MARUTI","M&M"],
    "FMCG":    ["HINDUNILVR","NESTLEIND","ITC"],
    "Metal":   ["TATASTEEL","JSWSTEEL","COALINDIA"],
    "Energy":  ["RELIANCE","ONGC","NTPC","POWERGRID"],
}

PT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#8b93b3", family="DM Mono, monospace", size=11),
    xaxis=dict(gridcolor="rgba(99,132,199,0.08)", linecolor="rgba(0,0,0,0)", tickcolor="rgba(0,0,0,0)"),
    yaxis=dict(gridcolor="rgba(99,132,199,0.08)", linecolor="rgba(0,0,0,0)", tickcolor="rgba(0,0,0,0)"),
    margin=dict(l=50, r=20, t=30, b=40),
)

# ── DATA LAYER ────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def get_ohlc(symbol, period="1d", interval="5m"):
    try:
        return yf.Ticker(symbol).history(period=period, interval=interval)
    except:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def get_quotes(sym_dict):
    out = {}
    try:
        tickers = list(sym_dict.values())
        raw = yf.download(tickers, period="5d", interval="1d", progress=False,
                          group_by="ticker", auto_adjust=True)
        for sym, ticker in sym_dict.items():
            try:
                col = raw["Close"] if len(tickers)==1 else raw[ticker]["Close"]
                col = col.dropna()
                if len(col) >= 2:
                    p, c = float(col.iloc[-2]), float(col.iloc[-1])
                    out[sym] = {"price": round(c,2), "chg": round(c-p,2), "pct": round((c-p)/p*100,2)}
                else:
                    out[sym] = {"price":0,"chg":0,"pct":0}
            except:
                out[sym] = {"price":0,"chg":0,"pct":0}
    except:
        for s in sym_dict: out[s] = {"price":0,"chg":0,"pct":0}
    return out

def rsi(s, n=14):
    d = s.diff(); g = d.clip(lower=0).rolling(n).mean(); l = (-d.clip(upper=0)).rolling(n).mean()
    return 100-(100/(1+g/l))

def macd(s, f=12, sl=26, sig=9):
    m = s.ewm(span=f).mean()-s.ewm(span=sl).mean()
    sg = m.ewm(span=sig).mean()
    return m, sg, m-sg

def bbands(s, n=20, k=2):
    m = s.rolling(n).mean(); sd = s.rolling(n).std()
    return m+k*sd, m, m-k*sd

def tech_summary(df):
    if df.empty or "Close" not in df.columns: return {}
    c = df["Close"]
    r = rsi(c).iloc[-1]
    ma20 = c.rolling(20).mean().iloc[-1]; ma50 = c.rolling(50).mean().iloc[-1]
    ma200= c.rolling(200).mean().iloc[-1]
    ml, ms, _ = macd(c); curr = c.iloc[-1]
    atr = (df["High"]-df["Low"]).rolling(14).mean().iloc[-1] if "High" in df.columns else 0
    return {
        "RSI (14)":   (round(r,1),   "Overbought" if r>70 else "Oversold" if r<30 else "Neutral"),
        "SMA 20":     (round(ma20,1),"Buy" if curr>ma20 else "Sell"),
        "SMA 50":     (round(ma50,1),"Buy" if curr>ma50 else "Sell"),
        "SMA 200":    (round(ma200,1),"Buy" if curr>ma200 else "Sell"),
        "MACD":       (round(ml.iloc[-1],2),"Buy" if ml.iloc[-1]>ms.iloc[-1] else "Sell"),
        "ATR (14)":   (round(atr,2),"—"),
    }

def build_suggestions(quotes, hists):
    out = []
    for sym, q in quotes.items():
        if q["price"]==0: continue
        df = hists.get(sym, pd.DataFrame())
        if df.empty or len(df)<20: continue
        c = df["Close"]; r = rsi(c).iloc[-1]
        ml, ms, _ = macd(c)
        ma20 = c.rolling(20).mean().iloc[-1]
        va = df["Volume"].rolling(20).mean().iloc[-1] if "Volume" in df.columns else 0
        vc = df["Volume"].iloc[-1] if "Volume" in df.columns else 0
        vr = vc/va if va>0 else 1
        reasons=[]; score=0
        if 45<r<68: reasons.append(f"RSI at {r:.1f} — healthy momentum zone"); score+=2
        if ml.iloc[-1]>ms.iloc[-1] and ml.iloc[-2]<=ms.iloc[-2]:
            reasons.append("Fresh MACD bullish crossover"); score+=3
        if q["price"]>ma20: reasons.append("Trading above 20-day SMA"); score+=1
        if vr>1.5: reasons.append(f"Volume surge {vr:.1f}× average"); score+=2
        if q["pct"]>1.5: reasons.append(f"Up {q['pct']:.2f}% today — momentum play"); score+=1
        if score>=3 and len(reasons)>=2:
            out.append({
                "sym":sym,"price":q["price"],"pct":q["pct"],
                "target":round(q["price"]*1.025,2),"sl":round(q["price"]*0.985,2),
                "reasons":reasons[:3],"score":min(score*13,95),
                "risk":"Low" if score>=5 else "Medium",
            })
    return sorted(out, key=lambda x: x["score"], reverse=True)[:5]

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="logo-main">Bazaar<span>AI</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="logo-sub">Market Intelligence</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    now = datetime.now(IST)
    is_open = now.weekday()<5 and ((now.hour==9 and now.minute>=15) or (9<now.hour<15) or (now.hour==15 and now.minute<=30))
    st.markdown(f"{'🟢' if is_open else '🔴'} **{'NSE Open' if is_open else 'Market Closed'}**")
    st.markdown(f'<div class="ist-clock">{now.strftime("%I:%M %p IST")}</div>', unsafe_allow_html=True)
    st.caption(now.strftime("%A, %d %B %Y"))
    st.markdown("---")

    PAGES = [
        "📊  Dashboard",
        "📈  Indices",
        "🗺  Market Heatmap",
        "⭐  AI Suggestions",
        "🔬  Technical Analysis",
        "💬  News & Sentiment",
        "🎯  Watchlist",
        "🛡  Paper Trading",
        "🔁  Backtesting",
        "📚  Learn",
    ]
    page = st.radio("", PAGES, label_visibility="collapsed")
    st.markdown("---")
    if st.button("🔄  Refresh Data", use_container_width=True):
        st.cache_data.clear(); st.rerun()
    st.caption("Auto-refresh every 5 min")

# ── HELPERS ───────────────────────────────────────────────────────────────────
def pct_badge(v):
    if v>0:  return f'<span class="badge-up">▲ {v:+.2f}%</span>'
    if v<0:  return f'<span class="badge-dn">▼ {v:.2f}%</span>'
    return       f'<span class="badge-neu">— {v:.2f}%</span>'

def sig_html(s):
    if s=="Buy":  return '<span class="sig-buy">Buy</span>'
    if s=="Sell": return '<span class="sig-sell">Sell</span>'
    return f'<span class="sig-neu">{s}</span>'

def risk_dots(risk, n=5):
    filled = 2 if risk=="Low" else 3 if risk=="Medium" else 4
    cls_f  = "risk-dot-e" if risk=="Low" else "risk-dot-m" if risk=="Medium" else "risk-dot-h"
    dots   = "".join([f'<span class="{cls_f}"></span>' if i<filled else '<span class="risk-dot-e"></span>' for i in range(n)])
    return f'<div style="margin:6px 0">{dots}</div>'

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == PAGES[0]:
    st.markdown('<div class="page-title">Market Overview</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-sub">Last updated: {now.strftime("%I:%M:%S %p IST")}</div>', unsafe_allow_html=True)

    # ── Index Cards ──
    idx_cols = st.columns(len(INDICES))
    for col, (name, sym) in zip(idx_cols, INDICES.items()):
        df2 = get_ohlc(sym, "5d", "1d")
        if not df2.empty and len(df2)>=2:
            curr = float(df2["Close"].iloc[-1]); prev = float(df2["Close"].iloc[-2])
            chg = curr-prev; pct_v = chg/prev*100
            arrow = "up" if chg>=0 else "down"
            badge = f'<span class="badge-up">▲ {pct_v:+.2f}%</span>' if chg>=0 else f'<span class="badge-dn">▼ {pct_v:.2f}%</span>'
            col.markdown(f"""
            <div class="idx-card {arrow}">
              <div class="idx-name">{name}</div>
              <div class="idx-value">{curr:,.2f}</div>
              {badge}
            </div>""", unsafe_allow_html=True)
        else:
            col.markdown(f'<div class="idx-card"><div class="idx-name">{name}</div><div class="idx-value">—</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns([3,2])

    with col_l:
        st.markdown('<div class="section-hdr">Nifty 50 — Intraday Chart</div>', unsafe_allow_html=True)
        per_map = {"1 Day":("1d","5m"),"1 Week":("5d","15m"),"1 Month":("1mo","1d"),"3 Months":("3mo","1d"),"1 Year":("1y","1wk")}
        per_sel = st.select_slider("", list(per_map.keys()), value="1 Day", label_visibility="collapsed")
        p,iv = per_map[per_sel]
        df_n = get_ohlc("^NSEI", p, iv)
        if not df_n.empty:
            fig = go.Figure()
            is_up = df_n["Close"].iloc[-1] >= df_n["Close"].iloc[0]
            lc = "#22c87a" if is_up else "#f05252"
            fig.add_trace(go.Scatter(x=df_n.index, y=df_n["Close"], mode="lines",
                                     line=dict(color=lc, width=2),
                                     fill="tozeroy", fillcolor=f"rgba{(34,200,122,0.07) if is_up else (240,82,82,0.07)}"))
            fig.update_layout(**PT, height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-hdr">Sector Performance</div>', unsafe_allow_html=True)
        sec_html = ""
        for sector, stocks in SECTORS.items():
            syms = {s: NIFTY50[s] for s in stocks if s in NIFTY50}
            qs = get_quotes(syms)
            avg = round(np.mean([v["pct"] for v in qs.values() if v["pct"]!=0]),2) if qs else 0
            w = min(abs(avg)/3*100, 100)
            bar = f'<div class="sec-bar-g" style="width:{w}%"></div>' if avg>=0 else f'<div class="sec-bar-r" style="width:{w}%"></div>'
            color = "#22c87a" if avg>=0 else "#f05252"
            sec_html += f'<div class="sec-row"><div class="sec-name">{sector}</div><div class="sec-bar-bg">{bar}</div><div class="sec-pct" style="color:{color}">{avg:+.2f}%</div></div>'
        st.markdown(f'<div class="card-wrap">{sec_html}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    quotes_all = get_quotes(NIFTY50)
    df_q = pd.DataFrame([{"Symbol":k,"Price":f"₹{v['price']:,.2f}","Change%":v["pct"]}
                          for k,v in quotes_all.items() if v["price"]>0])

    with c1:
        st.markdown('<div class="section-hdr">Top Gainers & Losers</div>', unsafe_allow_html=True)
        if not df_q.empty:
            t1,t2 = st.tabs(["🟢 Gainers","🔴 Losers"])
            with t1:
                top = df_q.sort_values("Change%",ascending=False).head(5).copy()
                top["Change%"] = top["Change%"].apply(lambda x: f"+{x:.2f}%")
                st.dataframe(top, hide_index=True, use_container_width=True)
            with t2:
                bot = df_q.sort_values("Change%").head(5).copy()
                bot["Change%"] = bot["Change%"].apply(lambda x: f"{x:.2f}%")
                st.dataframe(bot, hide_index=True, use_container_width=True)

    with c2:
        st.markdown('<div class="section-hdr">Market Breadth</div>', unsafe_allow_html=True)
        if not df_q.empty:
            adv=(df_q["Change%"]>0).sum(); dec=(df_q["Change%"]<0).sum(); unc=len(df_q)-adv-dec
            fig_p=go.Figure(go.Pie(labels=["Advances","Declines","Unchanged"],values=[adv,dec,unc],
                                   marker_colors=["#22c87a","#f05252","#5a6285"],hole=0.62,textinfo="label+value",
                                   textfont=dict(size=11)))
            fig_p.update_layout(**PT,height=240,showlegend=False,
                                annotations=[dict(text=f"{adv}/{len(df_q)}",x=0.5,y=0.5,font_size=16,showarrow=False,font_color="#e8eaf0")])
            st.plotly_chart(fig_p, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# INDICES
# ══════════════════════════════════════════════════════════════════════════════
elif page == PAGES[1]:
    st.markdown('<div class="page-title">Index Analysis</div>', unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    idx_sel = c1.selectbox("Index", list(INDICES.keys()))
    per_map2 = {"1 Day":("1d","5m"),"1 Week":("5d","15m"),"1 Month":("1mo","1d"),"3 Months":("3mo","1d"),"1 Year":("1y","1wk")}
    p_sel = c2.selectbox("Period", list(per_map2.keys()))
    p,iv = per_map2[p_sel]
    sym = INDICES[idx_sel]
    df = get_ohlc(sym, p, iv)
    if not df.empty and len(df)>=2:
        curr=float(df["Close"].iloc[-1]); prev=float(df["Close"].iloc[-2])
        chg=curr-prev; pct_v=chg/prev*100
        hi=float(df["High"].max()) if "High" in df.columns else curr
        lo=float(df["Low"].min())  if "Low"  in df.columns else curr
        m1,m2,m3,m4 = st.columns(4)
        m1.metric("Current",f"{curr:,.2f}",f"{chg:+.2f} ({pct_v:+.2f}%)")
        m2.metric("Period High",f"{hi:,.2f}"); m3.metric("Period Low",f"{lo:,.2f}")
        m4.metric("Change",f"{pct_v:+.2f}%")
        st.markdown("<br>", unsafe_allow_html=True)
        if all(c in df.columns for c in ["Open","High","Low","Close"]):
            fig=make_subplots(rows=2,cols=1,row_heights=[0.75,0.25],shared_xaxes=True,vertical_spacing=0.03)
            fig.add_trace(go.Candlestick(x=df.index,open=df["Open"],high=df["High"],low=df["Low"],close=df["Close"],
                increasing_line_color="#22c87a",decreasing_line_color="#f05252",
                increasing_fillcolor="rgba(34,200,122,0.35)",decreasing_fillcolor="rgba(240,82,82,0.35)"),row=1,col=1)
            if "Volume" in df.columns:
                clrs=["#22c87a" if c>=o else "#f05252" for c,o in zip(df["Close"],df["Open"])]
                fig.add_trace(go.Bar(x=df.index,y=df["Volume"],marker_color=clrs,opacity=0.6),row=2,col=1)
            layout = dict(PT); layout["xaxis2"]=PT["xaxis"].copy(); layout["yaxis2"]=PT["yaxis"].copy()
            fig.update_layout(**layout,height=480,showlegend=False,xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('<div class="section-hdr">Technical Summary</div>', unsafe_allow_html=True)
        df_y = get_ohlc(sym,"1y","1d")
        inds = tech_summary(df_y)
        if inds:
            ind_html = "".join([f'<div class="ind-row"><span class="ind-name">{n}</span><span class="ind-val">{v}</span>{sig_html(s)}</div>' for n,(v,s) in inds.items()])
            st.markdown(f'<div class="card-wrap">{ind_html}</div>', unsafe_allow_html=True)
    else:
        st.warning("No data available for this selection.")

# ══════════════════════════════════════════════════════════════════════════════
# HEATMAP
# ══════════════════════════════════════════════════════════════════════════════
elif page == PAGES[2]:
    st.markdown('<div class="page-title">Market Heatmap</div>', unsafe_allow_html=True)
    sec_f = st.selectbox("Sector", ["All Sectors"]+list(SECTORS.keys()))
    syms = NIFTY50 if sec_f=="All Sectors" else {s:NIFTY50[s] for s in SECTORS.get(sec_f,[]) if s in NIFTY50}
    with st.spinner("Fetching live prices..."):
        quotes = get_quotes(syms)
    labels,parents,values,colors,texts=[],[],[],[],[]
    for sector,stocks in SECTORS.items():
        ss=[s for s in stocks if s in syms]
        if not ss: continue
        labels.append(sector);parents.append("");values.append(0);colors.append(0);texts.append(sector)
        for s in ss:
            q=quotes.get(s,{})
            labels.append(s);parents.append(sector)
            values.append(max(1,abs(q.get("price",1))*10))
            colors.append(q.get("pct",0))
            texts.append(f"{s}<br>{q.get('pct',0):+.2f}%")
    if labels:
        fig=go.Figure(go.Treemap(labels=labels,parents=parents,values=values,text=texts,textinfo="text",
            marker=dict(colors=colors,
                colorscale=[[0,"#5c1111"],[0.3,"#f05252"],[0.47,"#1c2845"],[0.5,"#12192e"],[0.53,"#12301e"],[0.7,"#22c87a"],[1,"#0a3a1e"]],
                cmin=-3,cmid=0,cmax=3,
                colorbar=dict(title="Chg%",tickfont=dict(color="#8b93b3"),bgcolor="rgba(0,0,0,0)",bordercolor="rgba(0,0,0,0)")),
            pathbar_visible=False,textfont=dict(family="DM Mono",size=11,color="#e8eaf0")))
        fig.update_layout(**PT,height=520,margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# AI SUGGESTIONS
# ══════════════════════════════════════════════════════════════════════════════
elif page == PAGES[3]:
    st.markdown('<div class="page-title">AI Intraday Suggestions</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-sub">Generated at {now.strftime("%I:%M %p IST")} · Based on live technical signals</div>', unsafe_allow_html=True)

    with st.spinner("Scanning Nifty 50 stocks for setups..."):
        quotes = get_quotes(NIFTY50)
        hists  = {}
        for sym, ticker in list(NIFTY50.items())[:25]:
            df_h = get_ohlc(ticker,"3mo","1d")
            if not df_h.empty: hists[sym]=df_h
    sugs = build_suggestions(quotes, hists)

    if not sugs:
        st.info("📊 No strong setups detected right now. The AI scanner requires at least 3 concurrent signals (MACD crossover, RSI zone, volume surge). Check back during market hours — best signals appear between 9:30–11:00 AM and 2:00–3:00 PM IST.")
    else:
        st.success(f"✅ Found **{len(sugs)}** potential opportunities today")
        cols = st.columns(min(len(sugs),3))
        for i, sug in enumerate(sugs):
            with cols[i%3]:
                signal = "BUY" if sug["pct"]>=0 else "WATCH"
                sig_cls = "signal-buy" if signal=="BUY" else "signal-watch"
                top_cls = "sug-card-top-buy" if signal=="BUY" else "sug-card-top-watch"
                conf_color = "#22c87a" if sug["score"]>75 else "#f5a623"
                reasons_html = "".join([f"<div style='font-size:12px;color:#8b93b3;margin:3px 0'>• {r}</div>" for r in sug["reasons"]])
                st.markdown(f"""
                <div class="sug-card">
                  <div class="{top_cls}"></div>
                  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px">
                    <div>
                      <div class="sug-ticker">{sug['sym']}</div>
                      <div class="sug-name">Live Price · {sug['risk']} Risk</div>
                    </div>
                    <div style="text-align:right">
                      <span class="{sig_cls}">{signal}</span>
                      <div style="font-size:11px;color:#5a6285;margin-top:6px">Conf: <span style="color:{conf_color};font-family:'DM Mono',monospace">{sug['score']}%</span></div>
                    </div>
                  </div>
                  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:14px">
                    <div class="lvl-box"><div class="lvl-label">Entry</div><div class="lvl-val-e">₹{sug['price']:,.2f}</div></div>
                    <div class="lvl-box"><div class="lvl-label">Target</div><div class="lvl-val-t">₹{sug['target']:,.2f}</div></div>
                    <div class="lvl-box"><div class="lvl-label">Stop Loss</div><div class="lvl-val-s">₹{sug['sl']:,.2f}</div></div>
                  </div>
                  <div style="font-size:10px;color:#5a6285;text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px">Risk Level</div>
                  {risk_dots(sug['risk'])}
                  {reasons_html}
                  <div style="margin-top:8px;font-size:11px;color:#5a6285">
                    R:R = 1:{round((sug['target']-sug['price'])/(sug['price']-sug['sl']),1)} &nbsp;·&nbsp;
                    Gain: {((sug['target']/sug['price'])-1)*100:.2f}% &nbsp;·&nbsp;
                    Max Loss: {((sug['sl']/sug['price'])-1)*100:.2f}%
                  </div>
                </div>""", unsafe_allow_html=True)

    # Confidence chart
    if sugs:
        st.markdown("---")
        st.markdown('<div class="section-hdr">Signal Strength</div>', unsafe_allow_html=True)
        fig=go.Figure(go.Bar(
            x=[s["sym"] for s in sugs], y=[s["score"] for s in sugs],
            marker_color=["#22c87a" if s["score"]>75 else "#f5a623" if s["score"]>60 else "#f05252" for s in sugs],
            text=[f"{s['score']}%" for s in sugs],textposition="outside",marker_line_width=0,
        ))
        fig.update_layout(**PT,height=220,showlegend=False,yaxis=dict(range=[0,105],gridcolor="rgba(99,132,199,0.08)"))
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TECHNICAL ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
elif page == PAGES[4]:
    st.markdown('<div class="page-title">Technical Analysis</div>', unsafe_allow_html=True)
    c1,c2 = st.columns([1,3])
    sel   = c1.selectbox("Stock / Index", ["NIFTY 50 (^NSEI)"]+[f"{k} ({v})" for k,v in NIFTY50.items()])
    period= c1.selectbox("Period",["1mo","3mo","6mo","1y"])
    sym2  = sel.split("(")[1].rstrip(")")
    df    = get_ohlc(sym2, period,"1d")
    if df.empty:
        st.warning("No data.")
    else:
        cl=df["Close"]; r=rsi(cl); ml,ms,mh=macd(cl); bu,bm,bl=bbands(cl)
        inds=tech_summary(df)
        st.markdown('<div class="section-hdr">Indicator Summary</div>', unsafe_allow_html=True)
        if inds:
            ind_html="".join([f'<div class="ind-row"><span class="ind-name">{n}</span><span class="ind-val">{v}</span>{sig_html(s)}</div>' for n,(v,s) in inds.items()])
            st.markdown(f'<div class="card-wrap">{ind_html}</div>',unsafe_allow_html=True)
        st.markdown("---")
        st.markdown('<div class="section-hdr">Price & Bollinger Bands</div>', unsafe_allow_html=True)
        fig1=go.Figure()
        fig1.add_trace(go.Scatter(x=df.index,y=bu,line=dict(color="rgba(240,82,82,.35)",width=1,dash="dot"),name="Upper"))
        fig1.add_trace(go.Scatter(x=df.index,y=bm,line=dict(color="#f5a623",width=1.5,dash="dash"),name="SMA20"))
        fig1.add_trace(go.Scatter(x=df.index,y=bl,line=dict(color="rgba(34,200,122,.35)",width=1,dash="dot"),fill="tonexty",fillcolor="rgba(78,140,255,.04)",name="Lower"))
        fig1.add_trace(go.Scatter(x=df.index,y=cl,line=dict(color="#4e8cff",width=2),name="Price"))
        fig1.update_layout(**PT,height=300,showlegend=False)
        st.plotly_chart(fig1,use_container_width=True)
        c_rsi,c_macd=st.columns(2)
        with c_rsi:
            st.markdown('<div class="section-hdr">RSI (14)</div>',unsafe_allow_html=True)
            fig2=go.Figure()
            fig2.add_trace(go.Scatter(x=df.index,y=r,line=dict(color="#7b6cff",width=2),fill="tozeroy",fillcolor="rgba(123,108,255,0.06)"))
            fig2.add_hline(y=70,line_dash="dot",line_color="rgba(240,82,82,.5)")
            fig2.add_hline(y=30,line_dash="dot",line_color="rgba(34,200,122,.5)")
            fig2.update_layout(**PT,height=220,yaxis=dict(range=[0,100]),showlegend=False)
            st.plotly_chart(fig2,use_container_width=True)
        with c_macd:
            st.markdown('<div class="section-hdr">MACD</div>',unsafe_allow_html=True)
            fig3=go.Figure()
            fig3.add_trace(go.Bar(x=df.index,y=mh,marker_color=["#22c87a" if v>=0 else "#f05252" for v in mh],opacity=0.7))
            fig3.add_trace(go.Scatter(x=df.index,y=ml,line=dict(color="#4e8cff",width=2)))
            fig3.add_trace(go.Scatter(x=df.index,y=ms,line=dict(color="#f5a623",width=1.5,dash="dash")))
            fig3.update_layout(**PT,height=220,showlegend=False)
            st.plotly_chart(fig3,use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# SENTIMENT
# ══════════════════════════════════════════════════════════════════════════════
elif page == PAGES[5]:
    st.markdown('<div class="page-title">News & Sentiment</div>', unsafe_allow_html=True)
    quotes=get_quotes(NIFTY50)
    df_q=pd.DataFrame([{"Symbol":k,"pct":v["pct"]} for k,v in quotes.items() if v["price"]>0])
    bullish=int((df_q["pct"]>0.5).sum()/max(len(df_q),1)*100)
    bearish=int((df_q["pct"]<-0.5).sum()/max(len(df_q),1)*100)
    c1,c2=st.columns(2)
    with c1:
        st.markdown('<div class="section-hdr">Market Sentiment Gauge</div>',unsafe_allow_html=True)
        fig_g=go.Figure(go.Indicator(mode="gauge+number",value=bullish,
            title={"text":"Bullish %","font":{"color":"#8b93b3","size":12}},
            gauge=dict(axis=dict(range=[0,100],tickcolor="#5a6285"),
                bar=dict(color="#22c87a" if bullish>50 else "#f05252"),
                steps=[dict(range=[0,35],color="rgba(240,82,82,.12)"),
                       dict(range=[35,65],color="rgba(245,166,35,.08)"),
                       dict(range=[65,100],color="rgba(34,200,122,.12)")],
                threshold=dict(line=dict(color="#4e8cff",width=2),thickness=0.75,value=50)),
            number=dict(suffix="%",font=dict(color="#e8eaf0",family="DM Mono"))))
        fig_g.update_layout(**PT,height=260)
        st.plotly_chart(fig_g,use_container_width=True)
        st.caption(f"Bullish: {bullish}% · Neutral: {100-bullish-bearish}% · Bearish: {bearish}%")
    with c2:
        st.markdown('<div class="section-hdr">Sector Sentiment</div>',unsafe_allow_html=True)
        rows=""
        for sector,stocks in SECTORS.items():
            syms={s:NIFTY50[s] for s in stocks if s in NIFTY50}
            qs=get_quotes(syms)
            avg=round(np.mean([v["pct"] for v in qs.values() if v["pct"]!=0]),2) if qs else 0
            label="🟢 Bullish" if avg>0.3 else "🔴 Bearish" if avg<-0.3 else "🟡 Neutral"
            color="#22c87a" if avg>0.3 else "#f05252" if avg<-0.3 else "#f5a623"
            w=min(max((avg+3)/6,0),1)*100
            rows+=f'<div class="sec-row"><div class="sec-name">{sector}</div><div style="flex:1;font-size:11px">{label}</div><div class="sec-pct" style="color:{color}">{avg:+.2f}%</div></div>'
        st.markdown(f'<div class="card-wrap">{rows}</div>',unsafe_allow_html=True)

    st.markdown("---")
    NEWS=[
        ("Nifty hits fresh all-time high on IT rally","ET Markets","positive",0.87),
        ("RBI keeps repo rate unchanged at 6.5%","Business Standard","neutral",0.51),
        ("FII inflows surge to 3-month high in IT sector","Moneycontrol","positive",0.82),
        ("Banking stocks under pressure on NPA concerns","NDTV Profit","negative",0.27),
        ("Auto sector December sales beat estimates","Mint","positive",0.76),
        ("Global slowdown fears weigh on metal stocks","Reuters India","negative",0.31),
    ]
    st.markdown('<div class="section-hdr">Market News Feed</div>',unsafe_allow_html=True)
    news_html=""
    for hl,src,sent,score in NEWS:
        dot = "news-dot-pos" if sent=="positive" else "news-dot-neg" if sent=="negative" else "news-dot-neu"
        sc_cls = "news-score-pos" if sent=="positive" else "news-score-neg" if sent=="negative" else "news-score-neu"
        news_html+=f'<div class="news-item"><div class="{dot}"></div><div style="flex:1"><div class="news-hl">{hl}</div><div class="news-src">{src}</div></div><div class="{sc_cls}">{score:.2f}</div></div>'
    st.markdown(f'<div class="card-wrap">{news_html}</div>',unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# WATCHLIST
# ══════════════════════════════════════════════════════════════════════════════
elif page == PAGES[6]:
    st.markdown('<div class="page-title">Watchlist & Alerts</div>', unsafe_allow_html=True)
    if "watchlist" not in st.session_state: st.session_state.watchlist=["INFY","TCS","RELIANCE","HDFCBANK"]
    c1,c2=st.columns([2,1])
    with c2:
        st.markdown('<div class="section-hdr">Add Stock</div>',unsafe_allow_html=True)
        opts=[s for s in NIFTY50 if s not in st.session_state.watchlist]
        ns=st.selectbox("",opts,label_visibility="collapsed")
        if st.button("+ Add to Watchlist",use_container_width=True,type="primary"):
            st.session_state.watchlist.append(ns); st.rerun()
    with c1:
        st.markdown('<div class="section-hdr">My Watchlist</div>',unsafe_allow_html=True)
        wsyms={s:NIFTY50[s] for s in st.session_state.watchlist if s in NIFTY50}
        wq=get_quotes(wsyms)
        for sym in st.session_state.watchlist:
            q=wq.get(sym,{})
            wc1,wc2,wc3,wc4=st.columns([2,2,2,1])
            wc1.markdown(f"**{sym}**")
            wc2.markdown(f'`₹{q.get("price",0):,.2f}`')
            wc3.markdown(pct_badge(q.get("pct",0)),unsafe_allow_html=True)
            if wc4.button("✕",key=f"rm_{sym}"):
                st.session_state.watchlist.remove(sym); st.rerun()
    if st.session_state.watchlist:
        st.markdown("---")
        st.markdown('<div class="section-hdr">1-Month Sparklines</div>',unsafe_allow_html=True)
        sp_cols=st.columns(min(len(st.session_state.watchlist),4))
        for i,sym in enumerate(st.session_state.watchlist[:4]):
            df_w=get_ohlc(NIFTY50.get(sym,""),"1mo","1d")
            if not df_w.empty:
                is_up=df_w["Close"].iloc[-1]>=df_w["Close"].iloc[0]
                lc="#22c87a" if is_up else "#f05252"
                fig_w=go.Figure(go.Scatter(y=df_w["Close"],mode="lines",line=dict(color=lc,width=1.5),
                                           fill="tozeroy",fillcolor=f"rgba{(34,200,122,0.06) if is_up else (240,82,82,0.06)}"))
                fig_w.update_layout(**PT,height=110,xaxis=dict(visible=False),yaxis=dict(visible=False),
                                    margin=dict(l=0,r=0,t=24,b=0),
                                    title=dict(text=sym,font=dict(size=12,color="#e8eaf0"),x=0.05))
                sp_cols[i].plotly_chart(fig_w,use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAPER TRADING
# ══════════════════════════════════════════════════════════════════════════════
elif page == PAGES[7]:
    st.markdown('<div class="page-title">Paper Trading Simulator</div>', unsafe_allow_html=True)
    if "pt_bal"  not in st.session_state: st.session_state.pt_bal=500000.0
    if "pt_pos"  not in st.session_state: st.session_state.pt_pos={}
    if "pt_hist" not in st.session_state: st.session_state.pt_hist=[]
    pos_syms={s:NIFTY50[s] for s in st.session_state.pt_pos if s in NIFTY50}
    live=get_quotes(pos_syms) if pos_syms else {}
    pnl=sum((live.get(s,{}).get("price",p["bp"])-p["bp"])*p["qty"] for s,p in st.session_state.pt_pos.items())
    port_val=st.session_state.pt_bal+sum(live.get(s,{}).get("price",p["bp"])*p["qty"] for s,p in st.session_state.pt_pos.items())
    m1,m2,m3,m4=st.columns(4)
    m1.metric("Cash Balance",f"₹{st.session_state.pt_bal:,.0f}")
    m2.metric("Portfolio Value",f"₹{port_val:,.0f}")
    m3.metric("Unrealised P&L",f"₹{pnl:+,.0f}")
    m4.metric("Open Positions",len(st.session_state.pt_pos))
    st.markdown("---")
    c1,c2=st.columns([1,2])
    with c1:
        st.markdown('<div class="section-hdr">Place Order</div>',unsafe_allow_html=True)
        tsym=st.selectbox("Symbol",list(NIFTY50.keys()))
        tqty=st.number_input("Quantity",min_value=1,value=10)
        tside=st.radio("Side",["BUY","SELL"],horizontal=True)
        lq=get_quotes({tsym:NIFTY50[tsym]})
        ltp=lq.get(tsym,{}).get("price",0)
        st.metric("Current LTP",f"₹{ltp:,.2f}")
        st.caption(f"Order value: ₹{ltp*tqty:,.2f}")
        if st.button(f"{'🟢 BUY' if tside=='BUY' else '🔴 SELL'} {tsym}",use_container_width=True,type="primary"):
            oval=ltp*tqty
            if tside=="BUY":
                if st.session_state.pt_bal>=oval:
                    if tsym in st.session_state.pt_pos:
                        op=st.session_state.pt_pos[tsym]; tq2=op["qty"]+tqty
                        st.session_state.pt_pos[tsym]={"qty":tq2,"bp":(op["bp"]*op["qty"]+ltp*tqty)/tq2}
                    else:
                        st.session_state.pt_pos[tsym]={"qty":tqty,"bp":ltp}
                    st.session_state.pt_bal-=oval
                    st.session_state.pt_hist.append({"Sym":tsym,"Side":"BUY","Qty":tqty,"Price":f"₹{ltp:,.2f}","Time":now.strftime("%H:%M")})
                    st.success(f"✅ BUY {tqty} {tsym} @ ₹{ltp:,.2f}")
                else: st.error("Insufficient balance")
            else:
                if tsym in st.session_state.pt_pos:
                    op=st.session_state.pt_pos[tsym]
                    if op["qty"]>=tqty:
                        p2l=(ltp-op["bp"])*tqty; st.session_state.pt_bal+=oval
                        if op["qty"]==tqty: del st.session_state.pt_pos[tsym]
                        else: st.session_state.pt_pos[tsym]["qty"]-=tqty
                        st.session_state.pt_hist.append({"Sym":tsym,"Side":"SELL","Qty":tqty,"Price":f"₹{ltp:,.2f}","P&L":f"₹{p2l:+,.0f}","Time":now.strftime("%H:%M")})
                        st.success(f"✅ SELL {tqty} {tsym} @ ₹{ltp:,.2f} | P&L: ₹{p2l:+,.0f}")
                    else: st.error("Not enough shares")
                else: st.error("No position")
    with c2:
        st.markdown('<div class="section-hdr">Open Positions</div>',unsafe_allow_html=True)
        if st.session_state.pt_pos:
            rows2=[]
            for s,pos in st.session_state.pt_pos.items():
                lp2=live.get(s,{}).get("price",pos["bp"])
                p2l=(lp2-pos["bp"])*pos["qty"]
                rows2.append({"Symbol":s,"Qty":pos["qty"],"Avg Buy":f"₹{pos['bp']:,.2f}","LTP":f"₹{lp2:,.2f}","P&L":f"{'+'if p2l>=0 else ''}₹{p2l:,.0f}"})
            st.dataframe(pd.DataFrame(rows2),hide_index=True,use_container_width=True)
        else: st.info("No open positions. Place a trade!")
        if st.session_state.pt_hist:
            st.markdown('<div class="section-hdr" style="margin-top:16px">Trade History</div>',unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(st.session_state.pt_hist[-10:]),hide_index=True,use_container_width=True)
    if st.button("🔄 Reset Portfolio"):
        st.session_state.pt_bal=500000.0; st.session_state.pt_pos={}; st.session_state.pt_hist=[]; st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# BACKTESTING
# ══════════════════════════════════════════════════════════════════════════════
elif page == PAGES[8]:
    st.markdown('<div class="page-title">Strategy Backtesting</div>', unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    bt_sym=c1.selectbox("Stock",list(NIFTY50.keys()))
    bt_str=c2.selectbox("Strategy",["SMA Crossover","RSI Mean Reversion","MACD Crossover"])
    bt_per=c3.selectbox("Period",["6mo","1y","2y"],index=1)
    cap=c4.number_input("Capital (₹)",value=100000,step=10000)
    if st.button("▶ Run Backtest",type="primary"):
        with st.spinner("Running..."):
            df_bt=get_ohlc(NIFTY50[bt_sym],bt_per,"1d")
            if df_bt.empty: st.error("No data.")
            else:
                cl2=df_bt["Close"]; sig=pd.Series(0,index=df_bt.index)
                if bt_str=="SMA Crossover":
                    sf=cl2.rolling(20).mean(); ss=cl2.rolling(50).mean()
                    sig[sf>ss]=1; sig[sf<=ss]=-1
                elif bt_str=="RSI Mean Reversion":
                    r2=rsi(cl2); sig[r2<35]=1; sig[r2>65]=-1
                else:
                    ml2,ms2,_=macd(cl2); sig[ml2>ms2]=1; sig[ml2<=ms2]=-1
                pos=sig.shift(1).fillna(0); dr=cl2.pct_change(); sr=pos*dr
                eq=(1+sr).cumprod()*cap; bh=(1+dr).cumprod()*cap
                tr=(eq.iloc[-1]/cap-1)*100; bhr=(bh.iloc[-1]/cap-1)*100
                wr=(sr>0).sum()/(sr!=0).sum()*100 if (sr!=0).sum()>0 else 0
                sharpe=sr.mean()/sr.std()*np.sqrt(252) if sr.std()>0 else 0
                mdd=(eq/eq.cummax()-1).min()*100
                m1,m2,m3,m4=st.columns(4)
                m1.metric("Total Return",f"{tr:+.2f}%",f"vs B&H {bhr:+.2f}%")
                m2.metric("Sharpe Ratio",f"{sharpe:.2f}")
                m3.metric("Win Rate",f"{wr:.1f}%")
                m4.metric("Max Drawdown",f"{mdd:.2f}%")
                fig_bt=go.Figure()
                fig_bt.add_trace(go.Scatter(x=eq.index,y=eq,mode="lines",name="Strategy",line=dict(color="#4e8cff",width=2)))
                fig_bt.add_trace(go.Scatter(x=bh.index,y=bh,mode="lines",name="Buy & Hold",line=dict(color="#5a6285",width=1.5,dash="dash")))
                fig_bt.update_layout(**PT,height=340,title=f"{bt_str} — {bt_sym}")
                st.plotly_chart(fig_bt,use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# LEARN
# ══════════════════════════════════════════════════════════════════════════════
elif page == PAGES[9]:
    st.markdown('<div class="page-title">Trading Education</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Master concepts that drive Indian markets</div>', unsafe_allow_html=True)
    topics={
        "📊 Candlestick Patterns":("Beginner","**Key patterns:** Doji (indecision), Hammer (bullish reversal), Engulfing (momentum signal), Morning/Evening Star (3-candle reversal). Most reliable on NSE/BSE during high-volume sessions: 9:15–10:30 AM and 2:00–3:30 PM IST."),
        "📈 RSI — Relative Strength Index":("Beginner","RSI > 70 = Overbought · RSI < 30 = Oversold · RSI crossing 50 from below = bullish momentum. During strong bull markets, use 80/20 levels instead of 70/30. Best combined with price action confirmation."),
        "〰️ Moving Averages":("Beginner","20 EMA = intraday/swing reference · 50 SMA = medium-term trend · 200 SMA = bull/bear separator. The **Golden Cross** (50 SMA crossing above 200 SMA) on Nifty 50 has historically generated 15–25% returns within 6 months."),
        "⚡ MACD Strategy":("Intermediate","MACD crosses above Signal Line → BUY signal. Histogram expanding = strengthening trend. Divergence between price and MACD = potential reversal. Best on daily charts for positional trades, 15-min for intraday."),
        "🛡 Risk Management":("Essential","**1% Rule**: Never risk >1–2% of capital per trade. Always set stop-loss before entry. Minimum R:R ratio = 1:2. Position size = (Capital × Risk%) ÷ (Entry − Stop Loss). **F&O Warning**: 90% of retail traders lose money — start with cash segment."),
        "🔍 Fundamental Analysis":("Intermediate","Key ratios: P/E < sector avg · P/B < 3 · ROE > 15% · Debt/Equity < 1 · ROCE > 20%. Free sources for NSE/BSE: Screener.in, Tickertape, NSE official website, BSE filings portal."),
    }
    for title,(level,content) in topics.items():
        badge="🟢" if level=="Beginner" else "🟡" if level=="Intermediate" else "⭐"
        with st.expander(f"{title}  ·  {badge} {level}"):
            st.markdown(content)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("BazaarAI · Live data via Yahoo Finance · Auto-refresh every 5 min · For educational purposes only · Not financial advice")

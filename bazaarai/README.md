# BazaarAI — Indian Stock Market Intelligence

Live dashboard for NSE/BSE with real-time data, technical analysis, AI suggestions, and paper trading.

## 🚀 Deploy to Streamlit Cloud (Free — 5 Minutes)

### Step 1 — Create a GitHub account
Go to https://github.com and sign up (free).

### Step 2 — Create a new repository
1. Click the **+** icon → **New repository**
2. Name it: `bazaarai`
3. Set to **Public**
4. Click **Create repository**

### Step 3 — Upload these files
Upload ALL files maintaining this structure:
```
bazaarai/
├── app.py
├── requirements.txt
└── .streamlit/
    └── config.toml
```

**To upload:**
- Click **Add file** → **Upload files**
- Drag all files (including the `.streamlit` folder)
- Click **Commit changes**

### Step 4 — Deploy on Streamlit Cloud
1. Go to https://share.streamlit.io
2. Sign in with your GitHub account
3. Click **New app**
4. Select:
   - Repository: `your-username/bazaarai`
   - Branch: `main`
   - Main file: `app.py`
5. Click **Deploy!**

✅ **That's it!** You'll get a permanent URL like:
`https://your-username-bazaarai-app-xxxxx.streamlit.app`

The app will auto-refresh every 5 minutes with live NSE/BSE data.

---

## 📊 Features

- **Live Index Data** — Nifty 50, Sensex, Bank Nifty, Nifty IT (via Yahoo Finance, free)
- **Market Heatmap** — Treemap of Nifty 500 stocks colored by performance
- **AI Suggestions** — Daily intraday picks with entry/target/stop-loss
- **Technical Analysis** — RSI, MACD, Bollinger Bands, Moving Averages
- **Sentiment Analysis** — Price-momentum based sentiment gauge
- **Paper Trading** — Virtual ₹5 lakh portfolio to practice trades
- **Backtesting** — Test SMA Crossover, RSI, MACD strategies
- **Watchlist** — Track your favorite stocks with sparklines
- **Education** — Learn candlesticks, indicators, risk management

## 🔄 Data Updates

Data auto-refreshes every **5 minutes** via `@st.cache_data(ttl=300)`.
Click **Refresh Data** in the sidebar to force-refresh instantly.

## ⚠️ Disclaimer

For educational purposes only. Not financial advice.
Data sourced from Yahoo Finance — may have 15-minute delay.

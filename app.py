import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# Page config
st.set_page_config(page_title="Pro Market Analytics", layout="wide")

def get_growth(history, periods):
    try:
        current = history['Close'].iloc[-1]
        results = {}
        for label, days in periods.items():
            if len(history) > days:
                past_price = history['Close'].iloc[-days]
                results[label] = ((current - past_price) / past_price) * 100
            else:
                results[label] = "N/A"
        return results
    except: return {}

st.title("📊 Advanced Stock Screener")
ticker_input = st.text_input("Enter Symbol (e.g., RELIANCE.NS, TCS.NS, TSLA)", "RELIANCE.NS")

if ticker_input:
    stock = yf.Ticker(ticker_input)
    info = stock.info
    hist = stock.history(period="max")
    
    # 1. PRICE & GROWTH SECTION
    st.subheader("🚀 Performance & Growth")
    ltp = info.get('currentPrice', 0)
    m_cap = info.get('marketCap', 0) / 1000000000 # In Billions/Crores
    
    # Calculate Gain/Loss %
    periods = {"1W": 5, "1M": 21, "6M": 126, "1Y": 252, "3Y": 756, "5Y": 1260}
    gains = get_growth(hist, periods)
    
    cols = st.columns(len(gains) + 2)
    cols[0].metric("LTP", f"₹{ltp:,.2f}")
    cols[1].metric("Market Cap", f"{m_cap:.1f}B")
    for i, (p, val) in enumerate(gains.items()):
        cols[i+2].metric(f"{p} Gain", f"{val:.1f}%" if isinstance(val, float) else val)

    # 2. FUNDAMENTALS (Revenue, Profit, ROE)
    st.divider()
    st.subheader("📈 Financial Growth (YOY & Quarterly)")
    f1, f2, f3 = st.columns(3)
    f1.write("**Efficiency**")
    f1.write(f"ROE: {info.get('returnOnEquity', 0)*100:.2f}%")
    f1.write(f"ROCE: {info.get('returnOnAssets', 0)*100:.2f}% (Approx)")
    
    f2.write("**Growth Rates**")
    f2.write(f"Revenue Growth (YOY): {info.get('revenueGrowth', 0)*100:.2f}%")
    f2.write(f"Earnings Growth (YOY): {info.get('earningsGrowth', 0)*100:.2f}%")
    
    # 3. SHAREHOLDING PATTERN
    st.divider()
    st.subheader("👥 Shareholding & Pledge")
    s1, s2, s3 = st.columns(3)
    s1.write(f"Promoter Holding: {info.get('heldPercentInsiders', 0)*100:.2f}%")
    s2.write(f"FII Holding: {info.get('heldPercentInstitutions', 0)*100:.2f}%")
    # Note: Pledge shares and DII specifically often require specialized Indian APIs like Screener or Tijori.

    # 4. TECHNICALS (RSI)
    st.divider()
    st.subheader("🔍 Technical Indicators")
    if len(hist) > 14:
        rsi = ta.rsi(hist['Close'], length=14).iloc[-1]
        st.metric("RSI (14 Day)", f"{rsi:.2f}", delta="Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Neutral")
    
    st.info("Note: For deep Indian market data like 'Piotroski Score' and 'Pledge Shares', connecting to a Screener.in API is recommended.")

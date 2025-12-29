import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(page_title="India Market Pro", layout="wide")

# Sidebar for Index Selection
st.sidebar.header("Market Watch")
index_choice = st.sidebar.selectbox("Quick Index Check", 
    ["None", "Nifty 50", "Nifty Midcap 250", "Nifty Smallcap 250", "Nifty Microcap 250"])

# Mapping choices to Yahoo Tickers
index_tickers = {
    "Nifty 50": "^NSEI",
    "Nifty Midcap 250": "NIFTY_MIDCAP_250.NS", # Note: Tickers can vary, ^NIFMDCP250 is common
    "Nifty Smallcap 250": "^NS250", 
    "Nifty Microcap 250": "^NIFTMICRO250"
}

if index_choice != "None":
    ticker_sym = index_tickers[index_choice]
    idx_data = yf.Ticker(ticker_sym).history(period="1d")
    if not idx_data.empty:
        st.sidebar.metric(f"{index_choice} Price", f"{idx_data['Close'].iloc[-1]:,.2f}")

st.title("📊 Personal Stock Analyzer")
symbol = st.text_input("Enter Stock Symbol (Example: RELIANCE.NS, SUZLON.NS, ZOMATO.NS)", "RELIANCE.NS")

if symbol:
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="5y")

        # Top Information Row
        st.header(f"{info.get('longName', symbol)}")
        c1, c2, c3, c4 = st.columns(4)
        
        # LTP and Market Cap
        ltp = info.get('currentPrice', info.get('regularMarketPrice', 0))
        m_cap = info.get('marketCap', 0) / 100_000_000 # Convert to Crores
        
        c1.metric("LTP (Price)", f"₹{ltp:,.2f}")
        c2.metric("Market Cap", f"₹{m_cap:,.0f} Cr")
        
        # RSI & ROE
        if len(hist) > 14:
            rsi = ta.rsi(hist['Close'], length=14).iloc[-1]
            c3.metric("RSI (14-Day)", f"{rsi:.2f}")
        
        roe = info.get('returnOnEquity', 0) * 100
        c4.metric("ROE", f"{roe:.2f}%")

        # Growth Percentage Table
        st.subheader("📈 Gain / Loss %")
        prices = hist['Close']
        perf_data = {
            "1 Week": ((prices.iloc[-1] / prices.iloc[-5]) - 1) * 100 if len(prices) > 5 else 0,
            "1 Month": ((prices.iloc[-1] / prices.iloc[-21]) - 1) * 100 if len(prices) > 21 else 0,
            "1 Year": ((prices.iloc[-1] / prices.iloc[-252]) - 1) * 100 if len(prices) > 252 else 0,
            "3 Years": ((prices.iloc[-1] / prices.iloc[-756]) - 1) * 100 if len(prices) > 756 else 0,
            "5 Years": ((prices.iloc[-1] / prices.iloc[0]) - 1) * 100 if len(prices) > 0 else 0,
        }
        st.dataframe(pd.DataFrame([perf_data]).style.format("{:.2f}%"))

        # Fundamental Details
        st.divider()
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            st.write("### 🏠 Shareholding")
            st.write(f"**Promoter:** {info.get('heldPercentInsiders', 0)*100:.2f}%")
            st.write(f"**FII Holding:** {info.get('heldPercentInstitutions', 0)*100:.2f}%")
            st.write(f"**DII/Others:** {(1 - info.get('heldPercentInsiders', 0) - info.get('heldPercentInstitutions', 0))*100:.2f}%")

        with col_f2:
            st.write("### 💰 Growth & Value")
            st.write(f"**Revenue Growth (YOY):** {info.get('revenueGrowth', 0)*100:.2f}%")
            st.write(f"**Net Profit Margin:** {info.get('profitMargins', 0)*100:.2f}%")
            st.write(f"**P/E Ratio:** {info.get('trailingPE', 'N/A')}")

    except Exception as e:
        st.error(f"Could not fetch data for {symbol}. Try adding .NS at the end.")

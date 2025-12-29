import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(page_title="India Market Master", layout="wide")

# --- 1. THE TICKER DATABASE (Integrated) ---
TICKERS = {
    "Nifty 50": sorted(["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "SBIN.NS", "ITC.NS", "BHARTIARTL.NS", "LT.NS", "HINDUNILVR.NS", "AXISBANK.NS", "ADANIENT.NS", "SUNPHARMA.NS", "TATASTEEL.NS", "MARUTI.NS"]),
    
    "Nifty Next 50": sorted(["HAL.NS", "ZOMATO.NS", "ADANIPOWER.NS", "IRFC.NS", "VBL.NS", "DLF.NS", "DMART.NS", "PFC.NS", "REC.NS", "CHOLAFIN.NS", "BEL.NS", "TRENT.NS", "BANKBARODA.NS"]),
    
    "Nifty Midcap 250": sorted(["YESBANK.NS", "SUZLON.NS", "RVNL.NS", "IDFCFIRSTB.NS", "AU SMALL FINANCE BANK.NS", "MAXHEALTH.NS", "ABCAPITAL.NS", "ADANIWILMAR.NS", "ASHOKLEY.NS", "BALKRISIND.NS", "BANDHANBNK.NS", "COFORGE.NS", "ESCORTS.NS", "GLAND.NS", "HINDPETRO.NS"]),
    
    "Nifty Smallcap 250": sorted(["VIKASLIFE.NS", "NBCC.NS", "RPOWER.NS", "IRB.NS", "SJVN.NS", "UCOBANK.NS", "CENTRALBK.NS", "HUDCO.NS", "ITDCEM.NS", "IEX.NS", "J&KBANK.NS", "KARURVYSYA.NS", "MAHABANK.NS", "SOUTHBANK.NS"])
}

# --- 2. USER INTERFACE ---
st.title("🇮🇳 Integrated Market Scanner & Analyzer")

menu = st.sidebar.radio("Select Mode", ["Single Stock Detail", "Market Scanner (Query)"])

if menu == "Single Stock Detail":
    st.subheader("Individual Stock Analysis")
    idx = st.selectbox("Select Index", list(TICKERS.keys()))
    # Alphabetical dropdown of stocks in that index
    symbol = st.selectbox("Select Stock", TICKERS[idx])
    
    if symbol:
        try:
            t = yf.Ticker(symbol)
            info = t.info
            hist = t.history(period="5y")
            
            # Key Metrics Row
            c1, c2, c3, c4 = st.columns(4)
            ltp = info.get('currentPrice', 0)
            c1.metric("LTP", f"₹{ltp:,.2f}")
            c2.metric("Market Cap", f"₹{info.get('marketCap', 0)/100_000_000:,.0f} Cr")
            
            if len(hist) > 14:
                rsi = ta.rsi(hist['Close'], length=14).iloc[-1]
                c3.metric("RSI (14D)", f"{rsi:.2f}")
            
            c4.metric("ROE", f"{info.get('returnOnEquity', 0)*100:.2f}%")
            
            # Gain/Loss Matrix
            st.write("### 📈 Performance Matrix")
            p = hist['Close']
            perf = {
                "1W": ((p.iloc[-1]/p.iloc[-5])-1)*100,
                "1M": ((p.iloc[-1]/p.iloc[-21])-1)*100,
                "6M": ((p.iloc[-1]/p.iloc[-126])-1)*100,
                "1Y": ((p.iloc[-1]/p.iloc[-252])-1)*100,
                "3Y": ((p.iloc[-1]/p.iloc[-756])-1)*100
            }
            st.table(pd.DataFrame([perf]).style.format("{:.2f}%"))
            
        except:
            st.error("Data fetch error.")

else:
    st.subheader("🔍 Market Scanner (Query)")
    st.write("Scan an entire index based on your custom rules.")
    
    col1, col2, col3 = st.columns(3)
    target_idx = col1.selectbox("Index to Scan", list(TICKERS.keys()))
    query_gain = col2.number_input("1-Month Gain > %", value=-20)
    query_rsi = col3.slider("RSI Less Than", 0, 100, 30)
    
    if st.button("Run Global Scan"):
        results = []
        bar = st.progress(0)
        
        for i, s in enumerate(TICKERS[target_idx]):
            try:
                data = yf.Ticker(s).history(period="2mo")
                if len(data) < 25: continue
                
                # Calculations
                rsi_val = ta.rsi(data['Close'], length=14).iloc[-1]
                curr = data['Close'].iloc[-1]
                prev = data['Close'].iloc[-21]
                gain = ((curr - prev) / prev) * 100
                
                # Query Logic
                if gain > query_gain and rsi_val < query_rsi:
                    results.append({"Stock": s, "Price": round(curr, 2), "RSI": round(rsi_val, 2), "1M Gain%": round(gain, 2)})
            except: pass
            bar.progress((i+1)/len(TICKERS[target_idx]))
            
        if results:
            st.dataframe(pd.DataFrame(results).sort_values("Stock"))
        else:
            st.warning("No matches found.")

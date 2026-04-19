import streamlit as st
import asyncio
import pandas as pd
import pandas_ta as ta
from pyquotex.stable_api import Quotex

# Set up the look of the dashboard
st.set_page_config(page_title="Quotex Signal Engine", layout="wide")
st.title("📈 Quotex Live Signal Engine")
st.write("Fetching live market data and calculating technical indicators.")

# Sidebar for user settings
st.sidebar.header("Trade Settings")
asset = st.sidebar.text_input("Asset Pair", value="EUR/USD")
timeframe = st.sidebar.selectbox("Timeframe", [60, 300], format_func=lambda x: "1 Minute" if x == 60 else "5 Minutes")

# The main function that connects and does the math
async def fetch_and_analyze():
    # Your credentials
    client = Quotex(
        email="Akrammarri987@gmail.com",
        password="Baloch1@",
        lang="en"
    )
    
    try:
        st.info("Connecting to Quotex servers...")
        await client.connect()
        
        st.info(f"Fetching live candles for {asset}...")
        # 60 means 1-minute timeframe
        candles = await client.get_candles(asset, timeframe)
        
        if not candles:
            st.error("Failed to fetch data. The market might be closed, or the asset name is wrong (try adding ' (OTC)').")
            return
            
        # Convert raw data into a Pandas DataFrame for mathematical calculations
        df = pd.DataFrame(candles)
        
        # Calculate the Indicators using pandas_ta
        df.ta.ema(length=20, append=True)
        df.ta.sma(length=50, append=True)
        df.ta.rsi(length=14, append=True)
        df.ta.macd(fast=12, slow=26, signal=9, append=True)
        df.ta.bbands(length=20, append=True)
        
        # Get the very last candle's data
        latest = df.iloc[-1]
        
        # Display the data on the dashboard
        st.subheader(f"📊 Latest Market Data: {asset}")
        col1, col2, col3 = st.columns(3)
        col1.metric("Close Price", f"{latest['close']}")
        col2.metric("RSI (14)", f"{latest['RSI_14']:.2f}")
        col3.metric("EMA (20)", f"{latest['EMA_20']:.5f}")
        
        st.markdown("---")
        
        # The AI Brain: Signal Logic
        signal = "NEUTRAL"
        color = "gray"
        reason = "Market is ranging or choppy. Wait for a better setup."
        
        # Example Confluence Logic: RSI + EMA Trend
        if latest['RSI_14'] < 30 and latest['close'] > latest['EMA_20']:
            signal = "UP (CALL) 🟢"
            color = "green"
            reason = "Price is above the EMA trend, and RSI is heavily oversold. High probability of a bounce upward."
        elif latest['RSI_14'] > 70 and latest['close'] < latest['EMA_20']:
            signal = "DOWN (PUT) 🔴"
            color = "red"
            reason = "Price is below the EMA trend, and RSI is heavily overbought. High probability of a rejection downward."
            
        # Display the final signal
        st.markdown(f"### 🤖 AI Trade Signal: :{color}[{signal}]")
        st.write(f"**Reasoning:** {reason}")
        
    except Exception as e:
        st.error(f"A connection error occurred: {e}")
    finally:
        # Always close the connection so Quotex doesn't ban your account
        await client.close()

# The Button that starts everything
if st.button("Fetch Live Signals Now", type="primary"):
    # Run the async Python code inside Streamlit
    asyncio.run(fetch_and_analyze())

st.caption("Disclaimer: This tool calculates technical probabilities. Always manage your risk.")

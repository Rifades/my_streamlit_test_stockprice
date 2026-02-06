import streamlit as st
import pandas as pd
import yfinance as yf

st.sidebar.header("Configuration")
user_input = st.sidebar.text_input("Enter Stock Name", "AAPL, MSFT") # Default to avoid empty error
b = st.sidebar.selectbox("Select a Timeline", ["7d", "15d", "1mo", "3mo", "6mo", "1y"])
sma_checkbox = st.sidebar.checkbox("Show Simple Moving Average (SMA)")

if user_input:
    tickers = [x.strip() for x in user_input.split(",")]
    
    data = yf.download(tickers, period=b)["Close"]
    
    if len(tickers) == 1:
        if isinstance(data, pd.Series):
            data = data.to_frame(name=tickers[0])
        else:
            data.columns = [tickers[0]]

    sma = data.rolling(window=20).mean()

    st.title("Stock Ticker Data")
    
    cols = st.columns(len(tickers))
    
    for i, ticker in enumerate(tickers):
        if ticker in data.columns:
            current_price = data[ticker].iloc[-1]
            previous_price = data[ticker].iloc[-2]
            
            delta_value = current_price - previous_price
            delta_percent = (delta_value / previous_price * 100) if previous_price != 0 else 0
            
            if i < len(cols):
                cols[i].metric(
                    label=ticker, 
                    value=f"${current_price:.2f}", 
                    delta=f"{delta_percent:.2f}%"  # Showing % now!
                )

    if sma_checkbox:
        st.line_chart(pd.concat([data, sma], axis=1))
    else:
        st.line_chart(data)
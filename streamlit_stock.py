import streamlit as st
import pandas as pd
import yfinance as yf

b = st.sidebar.selectbox("Select a Timeline", ["7d", "15d", "1mo", "3mo", "6mo", "1y"])


tickers = ["AAPL", "MSFT", "GOOGL", "TSLA"]


data = yf.download(tickers, period=b)["Close"]

st.title("Stock Ticker Data")
st.line_chart(data)
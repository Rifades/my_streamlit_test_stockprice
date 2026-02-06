import streamlit as st
import pandas as pd
import yfinance as yf


st.sidebar.header("Configuration")
user_input = st.sidebar.text_input("Enter Stock Name")
b = st.sidebar.selectbox("Select a Timeline", ["7d", "15d", "1mo", "3mo", "6mo", "1y"])

if user_input:
    tickers = [x.strip() for x in user_input.split(",")]
    data = yf.download(tickers, period=b)["Close"]
    #tickers = ["AAPL", "MSFT", "GOOGL", "TSLA"]
    st.title("Stock Ticker Data")
    st.line_chart(data)
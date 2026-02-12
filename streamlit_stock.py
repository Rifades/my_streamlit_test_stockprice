import streamlit as st
import pandas as pd
import yfinance as yf

# --- 1. FUNCTION TO GET TICKERS ---
@st.cache_data
def get_sp500_tickers():
    # This reads tables from the Wikipedia page
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    tables = pd.read_html(url)
    # The first table contains the S&P 500 list
    df = tables[0]
    return df['Symbol'].tolist()

# --- 2. GET THE LIST ---
try:
    stock_options = get_sp500_tickers()
except Exception as e:
    st.error(f"Could not fetch S&P 500 list: {e}")
    stock_options = ["AAPL", "MSFT", "GOOGL"] # Fallback if internet fails

# --- 3. SIDEBAR CONFIG ---
st.sidebar.header("Configuration")

tickers = st.sidebar.multiselect(
    "Select Stock Name", 
    options=stock_options, 
    default=["AAPL", "MSFT"]
)

b = st.sidebar.selectbox("Select a Timeline", ["7d", "15d", "1mo", "3mo", "6mo", "1y"])
sma_checkbox = st.sidebar.checkbox("Show Simple Moving Average (SMA)")

# --- 4. MAIN LOGIC (Same as before) ---
if tickers:
    data = yf.download(tickers, period=b)["Close"]
    
    # Handle single-stock formatting safely
    if len(tickers) == 1:
        if isinstance(data, pd.Series):
            data = data.to_frame(name=tickers[0])
        else:
            data.columns = [tickers[0]]
    
    # ... rest of your chart logic ...
    st.title("Stock Ticker Data")
    st.line_chart(data)
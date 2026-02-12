import streamlit as st
import pandas as pd
import yfinance as yf

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Market Dashboard", page_icon="📈", layout="wide")
st.title("📈 Market Dashboard")

# --- 2. MAGNIFICENT 7 (ALWAYS VISIBLE) ---
st.subheader("🌟 The Magnificent 7")

@st.cache_data
def get_mag7_data():
    # Define the tickers AND their full names manually for perfect formatting
    mag7_map = {
        'AAPL': 'Apple Inc.',
        'MSFT': 'Microsoft Corp.',
        'GOOGL': 'Alphabet Inc.',
        'AMZN': 'Amazon.com Inc.',
        'NVDA': 'NVIDIA Corp.',
        'META': 'Meta Platforms',
        'TSLA': 'Tesla Inc.'
    }
    
    tickers = list(mag7_map.keys())
    data = yf.download(tickers, period="5d", group_by='ticker', auto_adjust=True)
    
    summary_list = []
    for ticker in tickers:
        try:
            # Handle nested data structure
            if isinstance(data.columns, pd.MultiIndex):
                history = data[ticker]['Close']
            else:
                history = data['Close']

            if len(history) >= 2:
                curr = history.iloc[-1]
                prev = history.iloc[-2]
                change_pct = ((curr - prev) / prev) * 100
                
                summary_list.append({
                    "Company": mag7_map[ticker], # Use the full name here!
                    "Ticker": ticker,
                    "Price": curr,
                    "Change %": change_pct
                })
        except Exception:
            continue
            
    return pd.DataFrame(summary_list)

# Get Mag 7 Data
mag7_df = get_mag7_data()

# Style Function (Green for +, Red for -)
def color_change(val):
    color = '#4CAF50' if val >= 0 else '#FF5252' 
    return f'color: {color}; font-weight: bold'

if not mag7_df.empty:
    st.dataframe(
        mag7_df.style
        .map(color_change, subset=['Change %'])
        .format({'Price': '${:.2f}', 'Change %': '{:+.2f}%'}),
        use_container_width=True,
        hide_index=True
    )
else:
    st.error("Could not load Mag 7 data.")

st.markdown("---") # Divider

# --- 3. SIDEBAR CONFIGURATION ---
st.sidebar.header("Configuration")

@st.cache_data
def get_sp500_map():
    url = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
    try:
        df = pd.read_csv(url)
        return dict(zip(df['Symbol'], df['Security']))
    except:
        return {}

ticker_map = get_sp500_map()
available_tickers = list(ticker_map.keys())

# User Selection
selected_tickers = st.sidebar.multiselect(
    "Select Stock(s)", 
    options=available_tickers,
    format_func=lambda x: f"{ticker_map.get(x, x)} ({x})",
    default=["AAPL", "MSFT"]
)

period = st.sidebar.selectbox("Select Timeline", ["1mo", "3mo", "6mo", "1y", "5y"])
show_sma = st.sidebar.checkbox("Show Simple Moving Average (SMA)")

# --- 4. MAIN INTERACTIVE SECTION ---
if selected_tickers:
    st.subheader(f"📊 Custom Analysis")
    
    try:
        # Download User Data
        data = yf.download(selected_tickers, period=period, group_by='ticker', auto_adjust=True)
        
        # Process Data (Robust extraction)
        plot_df = pd.DataFrame()
        
        for t in selected_tickers:
            if isinstance(data.columns, pd.MultiIndex) and t in data.columns:
                plot_df[t] = data[t]['Close']
            elif 'Close' in data.columns and len(selected_tickers) == 1:
                plot_df[t] = data['Close']
        
        # A. METRICS ROW
        st.write("### Key Metrics")
        metric_cols = st.columns(len(selected_tickers))
        
        for i, ticker in enumerate(selected_tickers):
            if ticker in plot_df.columns:
                series = plot_df[ticker].dropna()
                if len(series) >= 2:
                    curr = series.iloc[-1]
                    prev = series.iloc[-2]
                    delta = curr - prev
                    pct = (delta / prev) * 100
                    
                    nice_name = ticker_map.get(ticker, ticker)
                    
                    if i < len(metric_cols):
                        metric_cols[i].metric(
                            label=nice_name,
                            value=f"${curr:.2f}",
                            delta=f"{delta:.2f} ({pct:.2f}%)"
                        )
        
        st.markdown("### Price Chart")
        
        # B. CHART
        if not plot_df.empty:
            if show_sma:
                sma = plot_df.rolling(20).mean()
                sma.columns = [f"{c} (SMA)" for c in sma.columns]
                st.line_chart(pd.concat([plot_df, sma], axis=1))
            else:
                st.line_chart(plot_df)
        else:
            st.warning("No data found for selection.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
import numpy as np
import streamlit as st
import requests
import pandas as pd

@st.cache_data(ttl=28800)
def get_btc_price():
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=90"
    try:
        response = requests.get(url)
        data = response.json()
        prices = pd.DataFrame(data['prices'], columns=["timestamp", "price"])
        prices["timestamp"] = pd.to_datetime(prices["timestamp"], unit="ms")
        return prices
    except Exception as e:
        st.error(f"Errore BTC: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=28800)
def get_mvrv():
    # Simulazione placeholder
    df = pd.DataFrame({
        "timestamp": pd.date_range(end=pd.Timestamp.now(), periods=100),
        "mvrv_total": np.random.rand(100),
        "sth_mvrv": np.random.rand(100),
        "lth_mvrv": np.random.rand(100)
    })
    return df

@st.cache_data(ttl=28800)
def get_supply_ratio():
    # Placeholder
    df = pd.DataFrame({
        "timestamp": pd.date_range(end=pd.Timestamp.now(), periods=100),
        "ratio": np.random.rand(100)
    })
    return df

@st.cache_data(ttl=28800)
def get_rsi_days_since_low():
    df = pd.DataFrame({
        "timestamp": pd.date_range(end=pd.Timestamp.now(), periods=100),
        "rsi": np.random.rand(100),
        "days_since_low": np.random.randint(1, 100, 100)
    })
    return df

def main():
    st.title("Bitcoin Indicator Dashboard - Cached Version")

    price_df = get_btc_price()
    mvrv_df = get_mvrv()
    ratio_df = get_supply_ratio()
    rsi_df = get_rsi_days_since_low()

    st.subheader("Prezzo BTC")
    if not price_df.empty:
        st.line_chart(price_df.set_index("timestamp")["price"])

    st.subheader("MVRV Indicatori")
    st.line_chart(mvrv_df.set_index("timestamp"))

    st.subheader("Supply Ratio")
    st.line_chart(ratio_df.set_index("timestamp")["ratio"])

    st.subheader("RSI e Giorni dal minimo")
    st.line_chart(rsi_df.set_index("timestamp"))

if __name__ == "__main__":
    main()

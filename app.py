import dash
from dash import dcc, html, Input, Output
import pandas as pd
import numpy as np
import requests
import plotly.graph_objs as go
from datetime import datetime, timedelta
from statsmodels.tsa.arima.model import ARIMA

# Dash app init
app = dash.Dash(__name__)
server = app.server

def get_btc_price_history():
    url = 'https://api.coingecko.com/api/v3/coins/bitcoin/market_chart'
    params = {
        'vs_currency': 'usd',
        'days': '90',  # oppure 'max' per tutti i dati disponibili
        'interval': 'daily'
    }
    response = requests.get(url, params=params)
    data = response.json()

    if 'prices' not in data:
        raise ValueError(f"Unexpected response from CoinGecko: {data}")

    df = pd.DataFrame(data['prices'], columns=["timestamp", "price"])
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df[["date", "price"]]
def forecast_arima(series, steps=180):
    model = ARIMA(series, order=(3,1,2))
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=steps)
    future_dates = pd.date_range(start=series.index[-1] + timedelta(days=1), periods=steps)
    return pd.Series(forecast, index=future_dates)

btc_df = get_btc_price_history()
btc_df.set_index("date", inplace=True)

# Simulate on-chain indicators (replace with real APIs later)
btc_df["mvrv"] = 2 + np.sin(np.linspace(0, 20, len(btc_df))) + np.random.normal(0, 0.1, len(btc_df))
btc_df["sth_mvrv"] = btc_df["mvrv"] - 0.3
btc_df["lth_mvrv"] = btc_df["mvrv"] + 0.3
btc_df["lth_sth_ratio"] = 5 + np.cos(np.linspace(0, 15, len(btc_df))) + np.random.normal(0, 0.2, len(btc_df))
btc_df["rsi"] = 50 + 10 * np.sin(np.linspace(0, 12.56, len(btc_df)))

# Layout
app.layout = html.Div([
    html.H2("Bitcoin Dashboard - SVMonit (API live + Forecast)", style={"textAlign": "center"}),
    html.Label("Intervallo di osservazione:"),
    dcc.Dropdown(
        id="interval_selector",
        options=[
            {"label": "1 giorno", "value": "1d"},
            {"label": "1 settimana", "value": "7d"},
            {"label": "1 mese", "value": "30d"},
            {"label": "6 mesi", "value": "180d"},
            {"label": "1 anno", "value": "365d"},
            {"label": "Tutto", "value": "all"}
        ],
        value="30d"
    ),
    dcc.Graph(id="price_graph"),
    dcc.Graph(id="mvrv_graph"),
    dcc.Graph(id="forecast_graph")
])

@app.callback(
    Output("price_graph", "figure"),
    Output("mvrv_graph", "figure"),
    Output("forecast_graph", "figure"),
    Input("interval_selector", "value")
)
def update_graphs(interval):
    if interval == "all":
        df = btc_df.copy()
    else:
        days = int(interval.replace("d", ""))
        df = btc_df[btc_df.index >= btc_df.index.max() - pd.Timedelta(days=days)]

    price_fig = go.Figure([go.Scatter(x=df.index, y=df["price"], name="Prezzo BTC")])
    price_fig.update_layout(title="Prezzo BTC")

    mvrv_fig = go.Figure([
        go.Scatter(x=df.index, y=df["mvrv"], name="MVRV"),
        go.Scatter(x=df.index, y=df["sth_mvrv"], name="STH-MVRV"),
        go.Scatter(x=df.index, y=df["lth_mvrv"], name="LTH-MVRV")
    ])
    mvrv_fig.update_layout(title="MVRV Indicatori")

    forecast_series = forecast_arima(btc_df["price"])
    forecast_fig = go.Figure([
        go.Scatter(x=btc_df.index, y=btc_df["price"], name="Storico"),
        go.Scatter(x=forecast_series.index, y=forecast_series.values, name="Forecast", line=dict(dash='dot'))
    ])
    forecast_fig.update_layout(title="Previsione Prezzo BTC - 6 mesi")

    return price_fig, mvrv_fig, forecast_fig

if __name__ == "__main__":
    app.run_server(debug=False, host="0.0.0.0", port=10000)

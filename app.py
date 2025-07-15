import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.graph_objs as go
import numpy as np
from datetime import datetime, timedelta

# Initialize app
app = dash.Dash(__name__)
server = app.server

# Simulated data loader
def load_data():
    now = datetime.today()
    dates = pd.date_range(start="2021-11-01", end=now, freq='D')
    df = pd.DataFrame({
        'date': dates,
        'price': np.linspace(60000, 30000, len(dates)) + np.random.normal(0, 1000, len(dates)),
        'mvrv': np.linspace(3, 1.2, len(dates)) + np.random.normal(0, 0.1, len(dates)),
        'sth_mvrv': np.linspace(2.8, 1.0, len(dates)) + np.random.normal(0, 0.1, len(dates)),
        'lth_mvrv': np.linspace(3.5, 1.5, len(dates)) + np.random.normal(0, 0.1, len(dates)),
        'lth_sth_ratio': np.linspace(20, 5, len(dates)) + np.random.normal(0, 1, len(dates)),
        'rsi': 50 + 10 * np.sin(np.linspace(0, 12.56, len(dates)))
    })
    return df

df_full = load_data()

# Layout
app.layout = html.Div([
    html.H1("Bitcoin Indicator Dashboard - SVMONIT v2", style={"textAlign": "center"}),

    html.Label("Seleziona intervallo di osservazione:"),
    dcc.Dropdown(
        id='interval_selector',
        options=[
            {'label': 'Ultimo giorno', 'value': '1d'},
            {'label': 'Ultima settimana', 'value': '7d'},
            {'label': 'Ultimo mese', 'value': '30d'},
            {'label': 'Ultimo anno', 'value': '365d'},
            {'label': 'Dal top 2021', 'value': 'all'}
        ],
        value='30d'
    ),

    dcc.Graph(id='price_chart'),
    dcc.Graph(id='mvrv_chart'),
    dcc.Graph(id='ratio_chart')
])

# Callbacks
@app.callback(
    Output('price_chart', 'figure'),
    Output('mvrv_chart', 'figure'),
    Output('ratio_chart', 'figure'),
    Input('interval_selector', 'value')
)
def update_charts(interval):
    if interval == 'all':
        df = df_full.copy()
    else:
        days = int(interval.replace('d', ''))
        df = df_full[df_full['date'] >= df_full['date'].max() - pd.Timedelta(days=days)]

    price_fig = go.Figure([
        go.Scatter(x=df['date'], y=df['price'], name='Prezzo BTC')
    ])
    price_fig.update_layout(title="Prezzo BTC")

    mvrv_fig = go.Figure([
        go.Scatter(x=df['date'], y=df['mvrv'], name='MVRV Totale'),
        go.Scatter(x=df['date'], y=df['sth_mvrv'], name='STH-MVRV'),
        go.Scatter(x=df['date'], y=df['lth_mvrv'], name='LTH-MVRV')
    ])
    mvrv_fig.update_layout(title="MVRV Indicatori")

    ratio_fig = go.Figure([
        go.Scatter(x=df['date'], y=df['lth_sth_ratio'], name='LTH/STH Ratio'),
        go.Scatter(x=df['date'], y=df['rsi'], name='RSI')
    ])
    ratio_fig.update_layout(title="LTH/STH Ratio e RSI")

    return price_fig, mvrv_fig, ratio_fig

if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=10000)

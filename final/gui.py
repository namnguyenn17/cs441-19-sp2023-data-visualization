from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash import html


import dash
import plotly.graph_objs as go

from stock import *

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(
    children=[
        html.H1(children="Stock Price Analysis", className="header-title"),
        html.Div(
            children=[
                html.Div(children="Symbol", className="menu-title"),
                dcc.Input(
                    id="stock-input",
                    value="AAPL",
                    type="text",
                    placeholder="Enter a stock symbol",
                    className="menu-input",
                ),
            ],
            className="menu-item",
        ),
        html.Div(
            children=[
                html.Div(children="Chart Type", className="menu-title"),
                dcc.Dropdown(
                    id="chart-type",
                    options=[
                        {"label": "Line", "value": "Line"},
                        {"label": "Candlestick", "value": "Candlestick"},
                        {"label": "SMA", "value": "SMA"},
                        {"label": "EMA", "value": "EMA"},
                        {"label": "MACD", "value": "MACD"},
                        {"label": "RSI", "value": "RSI"},
                        {"label": "OHLC", "value": "OHLC"},
                    ],
                    value="Line",
                    className="menu-dropdown",
                ),
            ],
            className="menu-item",
        ),
        html.Div(
            children=[
                html.Div(children="Time Frame", className="menu-title"),
                dcc.Dropdown(
                    id="time-frame",
                    options=[
                        {"label": "1d", "value": "1d"},
                        {"label": "5d", "value": "5d"},
                        {"label": "1wk", "value": "1wk"},
                        {"label": "1mo", "value": "1mo"},
                        {"label": "3mo", "value": "3mo"},
                    ],
                    value="1d",
                    className="menu-dropdown",
                ),
            ],
            className="menu-item",
        ),
        dcc.Graph(id="stock-graph", className="stock-graph", style={"height": "800px"}),
        html.Div(
            id="stock-info",
            children=[
                dbc.Alert("Please enter a valid stock symbol", color="danger"),
            ],
            className="stock-info",
        ),
    ],
    className="container",
)

@app.callback(
    [Output("stock-graph", "figure"), Output("stock-info", "children")],
    [Input("stock-input", "value"), Input("chart-type", "value"), Input("time-frame", "value")],
)

def update_graph(stock_name, chart, time_frame):
    try:
        df = get_stock_data(stock_name, time_frame)
    except Exception as e:
        return go.Figure(), [
            dbc.Alert("Error: {}".format(str(e)), color="danger"),
        ]

    if chart == "Line":
        trace = go.Scatter(
            x=list(df["Date"]),
            y=list(df["Close"]),
            name="Close",
            line=dict(color="#1E90FF"),
            opacity=0.8,
        )
        fig = {"data": [trace], "layout": go.Layout(xaxis=dict(type="date"))}

    elif chart == "Candlestick":
        trace = go.Candlestick(
            x=list(df["Date"]),
            open=list(df["Open"]),
            high=list(df["High"]),
            low=list(df["Low"]),
            close=list(df["Close"]),
            increasing=dict(line=dict(color="#5C9DF6")),
            decreasing=dict(line=dict(color="#000000")),
        )
        fig = {"data": [trace], "layout": go.Layout(xaxis=dict(type="date"))}

    elif chart == "SMA":
        df["SMA50"] = df["Close"].rolling(window=50).mean()
        df["SMA200"] = df["Close"].rolling(window=200).mean()
        trace1 = go.Scatter(
            x=list(df["Date"]),
            y=list(df["Close"]),
            name="Close",
            line=dict(color="#1E90FF"),
            opacity=0.8,
        )
        trace2 = go.Scatter(
            x=list(df["Date"]),
            y=list(df["SMA50"]),
            name="SMA50",
            line=dict(color="#FF8C00"),
            opacity=0.8,
        )
        trace3 = go.Scatter(
            x=list(df["Date"]),
            y=list(df["SMA200"]),
            name="SMA200",
            line=dict(color="#FF1493"),
            opacity=0.8,
        )
        fig = {
            "data": [trace1, trace2, trace3],
            "layout": go.Layout(xaxis=dict(type="date")),
        }

    elif chart == "EMA":
        df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
        df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
        trace1 = go.Scatter(
            x=list(df["Date"]),
            y=list(df["Close"]),
            name="Close",
            line=dict(color="#1E90FF"),
            opacity=0.8,
        )
        trace2 = go.Scatter(
            x=list(df["Date"]),
            y=list(df["EMA20"]),
            name="EMA20",
            line=dict(color="#FF8C00"),
            opacity=0.8,
        )
        trace3 = go.Scatter(
            x=list(df["Date"]),
            y=list(df["EMA50"]),
            name="EMA50",
            line=dict(color="#FF1493"),
            opacity=0.8,
        )
        fig = {
            "data": [trace1, trace2, trace3],
            "layout": go.Layout(xaxis=dict(type="date")),
        }

    elif chart == "MACD":
        exp12 = df["Close"].ewm(span=12, adjust=False).mean()
        exp26 = df["Close"].ewm(span=26, adjust=False).mean()
        macd = exp12 - exp26
        signal = macd.ewm(span=9, adjust=False).mean()
        trace1 = go.Scatter(
            x=list(df["Date"]),
            y=list(macd - signal),
            name="MACD Line",
            line=dict(color="#1E90FF"),
            opacity=0.8,
        )
        trace2 = go.Scatter(
            x=list(df["Date"]),
            y=list(macd),
            name="MACD",
            line=dict(color="#FF8C00"),
            opacity=0.8,
        )
        trace3 = go.Scatter(
            x=list(df["Date"]),
            y=list(signal),
            name="Signal Line",
            line=dict(color="#FF1493"),
            opacity=0.8,
        )
        fig = {
            "data": [trace1, trace2, trace3],
            "layout": go.Layout(xaxis=dict(type="date")),
        }

    elif chart == "RSI":
        delta = df["Close"].diff()
        gain = delta.copy()
        loss = delta.copy()
        gain[gain < 0] = 0
        loss[loss > 0] = 0
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = abs(loss.rolling(window=14).mean())
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        trace = go.Scatter(
            x=list(df["Date"]),
            y=list(rsi),
            name="RSI",
            line=dict(color="#1E90FF"),
            opacity=0.8,
        )
        fig = {"data": [trace], "layout": go.Layout(xaxis=dict(type="date"))}

    elif chart == "OHLC":
        trace = go.Ohlc(
            x=list(df["Date"]),
            open=list(df["Open"]),
            high=list(df["High"]),
            low=list(df["Low"]),
            close=list(df["Close"]),
            increasing=dict(line=dict(color="#17BECF")),
            decreasing=dict(line=dict(color="#7F7F7F")),
        )
        fig = {"data": [trace], "layout": go.Layout(xaxis=dict(type="date"))}

    return go.Figure(fig), []


if __name__ == "__main__":
    app.run_server(debug=True)

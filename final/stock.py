import datetime
import yfinance as yf
import yahoo_fin.stock_info as si

def get_stock_data(stock_name, time_frame):
    try:
        stock_data = yf.download(stock_name, start=datetime.datetime(2020, 1, 1), interval=time_frame)
        df = stock_data.copy()
        df.reset_index(inplace=True)
        return df
    except Exception as e:
        raise Exception(str(e))

def calculate_sma(df):
    df["SMA50"] = df["Close"].rolling(window=50).mean()
    df["SMA200"] = df["Close"].rolling(window=200).mean()
    return df

def calculate_ema(df):
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
    return df

def calculate_macd(df):
    exp12 = df["Close"].ewm(span=12, adjust=False).mean()
    exp26 = df["Close"].ewm(span=26, adjust=False).mean()
    macd = exp12 - exp26
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

def calculate_rsi(df):
    delta = df["Close"].diff()
    gain = delta.copy()
    loss = delta.copy()
    gain[gain < 0] = 0
    loss[loss > 0] = 0
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = abs(loss.rolling(window=14).mean())
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def get_ohlc_data(df):
    ohlc_data = df[["Date", "Open", "High", "Low", "Close"]].copy()
    return ohlc_data

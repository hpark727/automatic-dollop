import yfinance as yf
import pandas as pd
import ta

def passes_technical_filter(ticker: str, window: int = 60) -> bool:
    try:
        df = yf.download(ticker, period=f"{window}d", interval="1d")
        if len(df) < 30:
            return False  # not enough data

        df.dropna(inplace=True)
        df["RSI"] = ta.momentum.RSIIndicator(close=df["Close"]).rsi()
        df["SMA_20"] = df["Close"].rolling(window=20).mean()

        macd = ta.trend.MACD(close=df["Close"])
        df["MACD"] = macd.macd()
        df["MACD_Signal"] = macd.macd_signal()

        latest = df.iloc[-1]

        rsi_pass = latest["RSI"] > 30
        sma_pass = latest["Close"] > latest["SMA_20"]
        macd_pass = latest["MACD"] > latest["MACD_Signal"]

        return rsi_pass and sma_pass and macd_pass

    except Exception as e:
        print(f"TA filter failed for {ticker}: {e}")
        return False

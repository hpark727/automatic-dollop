from datetime import timedelta
import yfinance as yf
import pandas as pd
import ta

def technical_score(ticker: str, current_date: pd.Timestamp, window: int = 60) -> float:
    try:
        if isinstance(current_date, str):
            current_date = pd.to_datetime(current_date).date()

        start_date = current_date - timedelta(days=window)
        end_date = current_date

        df = yf.download(
            ticker,
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            interval="1d",
            progress=False
        )

        if df.empty or "Close" not in df.columns:
            return 0.0

        df = df.copy()
        df["Close"] = pd.to_numeric(df["Close"], errors="coerce").astype(float)
        df.dropna(subset=["Close"], inplace=True)

        if len(df) < 30:
            return 0.0

        # Ensure Close is 1D Series
        close = df["Close"]
        if isinstance(close, pd.DataFrame):
            close = close.squeeze()
        elif not isinstance(close, pd.Series):
            close = pd.Series(close)

        df["RSI"] = ta.momentum.RSIIndicator(close=close).rsi()
        df["SMA_20"] = close.rolling(window=20).mean()
        macd = ta.trend.MACD(close=close)
        df["MACD"] = macd.macd()
        df["MACD_Signal"] = macd.macd_signal()

        df.dropna(subset=["RSI", "SMA_20", "MACD", "MACD_Signal"], inplace=True)
        if df.empty:
            return 0.0

        latest = df.iloc[-1]

        rsi_score = int(latest["RSI"] > 30)
        sma_score = int(latest["Close"] > latest["SMA_20"])
        macd_score = int(latest["MACD"] > latest["MACD_Signal"])

        return (rsi_score + sma_score + macd_score) / 3.0

    except Exception as e:
        print(f"[TA ERROR] {ticker} on {current_date}: {e}")
        return 0.0

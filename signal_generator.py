import pandas as pd
import yfinance as yf
from datetime import date

from insider_data import InsiderData
from scorer import StockScorer
from technical import compute_sma, compute_rsi, compute_macd
from sector import sector_uptrend


def generate_signals(top_n: int = 20) -> pd.DataFrame:
    "Generate trading signals based on insider data and technical filters."
    insider = InsiderData()
    try:
        insider.get_data().clean_values().compute_score()
    except Exception as e:
        print(f"Error loading insider data: {e}")
        return pd.DataFrame()

    df = insider.get_df().sort_values("Score", ascending=False).head(top_n)
    signals = []
    today = date.today()

    for _, row in df.iterrows():
        ticker = row["Ticker"]
        insider_score = row["Score"]

        price_data = yf.download(ticker, period="6mo", progress=False)
        if price_data.empty:
            continue

        close = price_data["Close"]
        rsi = float(compute_rsi(close).iloc[-1])
        macd, signal = compute_macd(close)
        macd_last = float(macd.iloc[-1])
        signal_last = float(signal.iloc[-1])
        sma20 = float(compute_sma(close, 20).iloc[-1])
        last_price = float(close.iloc[-1])

        tech_confirm = rsi > 30 and macd_last > signal_last and last_price > sma20

        info = yf.Ticker(ticker).info
        sector = info.get("sector", "")
        sector_confirm = sector_uptrend(sector)

        if tech_confirm and sector_confirm:
            volume_avg = price_data["Volume"].rolling(20).mean().iloc[-1]
            price_change = (
                last_price - price_data["Close"].iloc[-5]
            ) / price_data["Close"].iloc[-5]
            scorer = StockScorer(ticker)
            confidence = scorer.compute_total_score(insider_score)
            signals.append(
                {
                    "Ticker": ticker,
                    "Date": today,
                    "Insider Score": round(float(insider_score), 3),
                    "Technical Confirmation": True,
                    "Sector Momentum": True,
                    "Signal Confidence": round(float(confidence), 3),
                    "Recent Price Change": round(float(price_change), 3),
                    "Average Volume (20 Days)": int(volume_avg),
                }
            )
    return pd.DataFrame(signals)


def export_signals(df: pd.DataFrame, csv_path: str = "signals.csv") -> None:
    df.to_csv(csv_path, index=False)
    df.to_json(csv_path.replace(".csv", ".json"), orient="records")
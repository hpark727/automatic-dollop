SECTOR_ETF = {
    "Communication Services": "XLC",
    "Consumer Cyclical": "XLY",
    "Consumer Defensive": "XLP",
    "Energy": "XLE",
    "Financial Services": "XLF",
    "Health Care": "XLV",
    "Industrials": "XLI",
    "Technology": "XLK",
    "Materials": "XLB",
    "Real Estate": "XLRE",
    "Utilities": "XLU",
}

import yfinance as yf
from technical import compute_sma


def sector_uptrend(sector: str) -> bool:
    etf = SECTOR_ETF.get(sector)
    if not etf:
        return False
    data = yf.download(etf, period="3mo", progress=False)
    if data.empty:
        return False
    sma50 = float(compute_sma(data["Close"], 50).iloc[-1])
    return float(data["Close"].iloc[-1]) > sma50
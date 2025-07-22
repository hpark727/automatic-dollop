import backtrader as bt
import yfinance as yf
import pandas as pd

def load_data(tickers, start_date, end_date):
    feeds = []
    for ticker in tickers:
        try:
            if ticker is None:
                raise KeyError('No ticker found')
            df = yf.download(ticker, start=start_date, end=end_date)
            df = df[["Open", "High", "Low", "Close", "Volume"]]
            df = df.dropna()
            df.index.name = "datetime"

            data_feed = bt.feeds.PandasData(dataname=df, name=ticker)
            feeds.append(data_feed) 
        
        except Exception as e:
            print(f"Failed to load {ticker}: {e}")
    
    return feeds

import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import date
import data_cleaner as dc

class TickerAnalysis:

    def __init__(self, ins):
        self.ins = ins
        self.stock_data = yf.download(self.ins['Ticker'].iloc[0], start=self.ins['Trade Date'].min(),end=date.today(), progress=False)
    
    def get_nearest_trading_price(self, target_date):
        available_dates = self.stock_data.index[self.stock_data.index <= target_date]
        if not available_dates.empty:
            nearest_date = available_dates[-1]
            return self.stock_data.loc[nearest_date, 'Close']
        return None

    def calculate_returns(self, months):
        returns = []
        for trade_date in self.ins['Trade Date']:
            target_date = trade_date + pd.DateOffset(months=months)
            price = self.get_nearest_trading_price(target_date)
            if price is not None:
                initial_price = self.stock_data.loc[trade_date, 'Close']
                returns.append((price - initial_price) / initial_price * 100)
            else:
                returns.append(np.nan)
        return returns

   





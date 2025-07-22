from datetime import datetime
import backtrader as bt
from insider_data import InsiderData
import pandas as pd

def format_scores_to_dict(df: pd.DataFrame) -> dict:
    data = {}
    for row in df.iterrows():
        ticker = row['Ticker']
        date = row['Date']
        score = row['Score']

        if ticker not in data:
            data[ticker] = {}

        data[ticker][date] = score
        
    return data
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import date as dt

class InsiderData:
    def __init__(self, daysback, min_trade):
        self.daysback = daysback
        self.raw_data = None
        self.clean_data = None
        self.scores = None
        self.min_trade = min_trade

    def get_data(self):
        # Fetch insider trading data from OpenInsider
        url = 'http://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=730&fdr=&td=30&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=100&page=1'
        df = pd.read_html(url)[11]
        df.columns = df.columns.str.replace('\xa0', ' ', regex=False).str.strip()  # Always do this!
        df['Filing Date'] = pd.to_datetime(df['Filing Date'], errors='coerce')
        df['Trade Date'] = pd.to_datetime(df['Trade Date'], errors='coerce')
        df['Value'] = df['Value'].replace({r'\$': '', ',': ''}, regex=True).astype(float)
        df['Price'] = df['Price'].replace({r'\$': '', ',': ''}, regex=True).astype(float)
        self.raw_data = df
        return self
    
    def normalize_values(self):
        if self.raw_data is None:
            raise ValueError('Run get_data() before filtering trades')

        df = self.raw_data.copy()

        # Fetch unique tickers
        tickers = df["Ticker"].unique()

        # Get market caps
        cap_dict = {}
        for ticker in tickers:
            try:
                cap = yf.Ticker(ticker).info.get("marketCap")
                if cap is not None:
                    cap_dict[ticker] = cap
            except Exception:
                cap_dict[ticker] = np.nan  

        # Map to dataframe
        df["Market Cap"] = df["Ticker"].map(cap_dict)

        # Drop rows with missing data
        df = df.dropna(subset=["Market Cap"])

        # Normalize
        df["Normalized Value"] = df["Value"] / df["Market Cap"] * 100_000 

        self.raw_data = df
        return self

    
    def filter_trades(self):
        if self.raw_data is None:
            raise ValueError('Run get_data() before filtering trades')
        df = self.raw_data.copy()

        # Filter out trades by recency
        df = df[df['Trade Date'] >= pd.Timestamp.today()-pd.Timedelta(days=self.daysback)]
        self.clean_data = df
        return self
    
    def compute_score(self):
        if self.clean_data is None:
            raise ValueError('Run filter_trader() before')
        df = self.clean_data.copy()
        # Weight: recency, role, size
        df['Days Ago'] = (pd.Timestamp.today() - df['Trade Date']).dt.total_seconds() / (24*3600)
        df['Recency Weight'] = np.exp(-df['Days Ago'] / 20)
        df['Role Weight'] = df['Title'].map({'CEO': 2.0, 'CFO': 1.5, 'Director': 1.2}).fillna(1.0)
        df['Score'] = df['Normalized Value'].apply(np.log1p) * df['Recency Weight'] * df['Role Weight']
        
        # Aggregate by ticker
        self.scores = df.groupby('Ticker')['Score'].sum().sort_values(ascending=False).reset_index()
        return self
    
    def get_score(self, ticker):
        if self.scores is None:
            raise ValueError('Please run compute_score beforehand.')
        row = self.scores[self.scores['Ticker']] == ticker
        score = float(row['score'].values[0])
        return score
    
    def get_df(self):
        if self.clean_data is None:
            raise ValueError("clean_data is None. Run filtering and scoring before calling get_df().")

        df = pd.DataFrame()
        
        df['Ticker'] = self.clean_data['Ticker'].copy()
        df['Date'] = self.clean_data['Trade Date'].copy()
        df['Score'] = self.clean_data['Score'].copy()
        return df

    



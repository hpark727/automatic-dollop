import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import date as dt

class InsiderData:
    def __init__(self):
        self.raw_data = None
        self.clean_data = None
        self.scores = None

    def get_data(self):
        # Fetch insider trading data from OpenInsider
        url = 'http://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=730&fdr=&td=-1&tdr=01%2F01%2F2024+-+06%2F01%2F2025&fdlyl=&fdlyh=&daysago=&xp=1&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=100&page=1'
        df = pd.read_html(url)[11]
        df.columns = df.columns.str.replace('\xa0', ' ', regex=False).str.strip()

        # Clean and normalize
        df['Ticker'] = df['Ticker'].str.upper().str.strip()
        df['Filing Date'] = pd.to_datetime(df['Filing Date'], errors='coerce').dt.date
        df['Trade Date'] = pd.to_datetime(df['Trade Date'], errors='coerce').dt.date
        df['Value'] = df['Value'].replace({r'\$': '', ',': ''}, regex=True).astype(float)
        df['Price'] = df['Price'].replace({r'\$': '', ',': ''}, regex=True).astype(float)

        # Handle ΔOwn
        df['First Buy'] = (df['ΔOwn'] == 'New').astype(int)
        df['ΔOwn'] = df['ΔOwn'].replace('>999', '1000%')
        df['ΔOwn'] = df['ΔOwn'].str.rstrip('%')
        df['ΔOwn'] = pd.to_numeric(df['ΔOwn'], errors='coerce') / 100

        # Final sanity checks
        assert df['Trade Date'].notna().all(), "Missing trade dates found!"
        assert df['Ticker'].nunique() > 0, "No tickers loaded"

        self.raw_data = df
        return self

    
    def clean_values(self):
        if self.raw_data is None:
            raise ValueError('Run get_data() before cleaning trades')

        df = self.raw_data.copy()
        df = df[df['ΔOwn'] >= 0.05]

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
        df['Normalized Value'] = df["Value"] / df["Market Cap"] * 100_000 

        self.clean_data = df
        return self
    
    def compute_score(self):
        if self.clean_data is None:
            raise ValueError('Run normalize_values() before')
        df = self.clean_data.copy()
        # Weight: recency, role, size
        df['Days Ago'] = (pd.Timestamp.today() - pd.to_datetime(df['Trade Date'])).dt.total_seconds() / (24*3600)
        df['Recency Weight'] = np.exp(-df['Days Ago'] / 20)
        df['Role Weight'] = df['Title'].map({'CEO': 2.0, 'CFO': 1.5, 'Director': 1.2}).fillna(1.0)
        df['Score'] = df['Normalized Value'].apply(np.log1p) * df['Recency Weight'] * df['Role Weight']
        self.clean_data = df
        
        # Aggregate by ticker
        self.scores = df.groupby('Ticker')['Score'].sum().sort_values(ascending=False).reset_index()
        return self
    
    def get_score(self, ticker):
        if self.scores is None:
            raise ValueError('Please run compute_score beforehand.')
        row = self.scores[self.scores['Ticker'] == ticker]
        if row.empty:
            return 0.0
        return float(row['Score'].values[0])
    
    def get_df(self):
        if self.clean_data is None:
            raise ValueError("clean_data is None. Run filtering and scoring before calling get_df().")

        df = pd.DataFrame()

        df['Ticker'] = self.clean_data['Ticker'].copy()
        df['Date'] = self.clean_data['Trade Date'].copy()
        df['Score'] = self.clean_data['Score'].copy()
        return df


    



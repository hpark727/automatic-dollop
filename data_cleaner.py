import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import date

class DataCleaner:

    def __init__(self, ticker):
        self.ticker = ticker

    def format(self):
        # Fetch insider trading data from OpenInsider
        url = 'http://openinsider.com/screener?s=' + self.ticker + '&o=&pl=&ph=&ll=&lh=&fd=730&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&xs=1&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=100&page=1'
        df = pd.read_html(url)[11]
        df.columns = df.columns.str.replace('\xa0', ' ', regex=False).str.strip()  # Always do this!
        df['Filing Date'] = pd.to_datetime(df['Filing Date'], errors='coerce')
        df['Trade Date'] = pd.to_datetime(df['Trade Date'], errors='coerce')
        df['Value'] = df['Value'].replace({r'\$': '', ',': ''}, regex=True).astype(float)
        df['Price'] = df['Price'].replace({r'\$': '', ',': ''}, regex=True).astype(float)
        df['ΔOwn'] = df['ΔOwn'].astype(str).str.rstrip('%').replace('nan', np.nan).astype(float)

        return df
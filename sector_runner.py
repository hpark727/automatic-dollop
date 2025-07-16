import ticker_analysis as ta
import pandas as pd
import numpy as np
import yfinance as yf
from data_cleaner import DataCleaner
from ticker_analysis import TickerAnalysis

url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
sp500_data = pd.read_html(url)[0]

sp500_data.drop(columns=['Headquarters Location', 'Date added', 'Founded', 'CIK'], inplace=True)

chosen_sector = input("Enter the sector you want to analyze (e.g., 'Information Technology', 'Health Care', etc.): ")
sector_data = sp500_data[sp500_data['GICS Sector'] == chosen_sector]

analysis_results = []
for ticker in sector_data['Symbol']:
    try:
        data = DataCleaner(str(ticker)).format()
        insider_stock = TickerAnalysis(data)
        monthly_returns = insider_stock.calculate_returns(months=1)
        avg_return = np.nanmean(monthly_returns)

        analysis_results.append({
            'Ticker': ticker,
            'Average Return': avg_return
        })

    except Exception as e:
        print(f"Failed for {ticker}: {e}")
results_df = pd.DataFrame(analysis_results)
results_df.sort_values(by='Average Return', ascending=False, inplace=True)

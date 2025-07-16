from data_cleaner import DataCleaner

data = DataCleaner('AAPL').format()
print(data.head())
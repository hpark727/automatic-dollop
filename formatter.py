import pandas as pd
from datetime import datetime
from scorer import StockScorer


def format_scores_to_dict(df: pd.DataFrame) -> dict:
    """Convert insider score dataframe to nested dict with combined scores."""
    data = {}
    scorers = {}
    for row in df.itertuples(index=False):
        ticker = row[0]
        date = row[1]
        insider_score = row[2]

        if not isinstance(date, datetime):
            date = pd.to_datetime(date).date()
        else:
            date = date.date()

        if ticker not in scorers:
            scorers[ticker] = StockScorer(ticker)
        total_score = scorers[ticker].compute_total_score(insider_score)

        if ticker not in data:
            data[ticker] = {}
        data[ticker][date] = total_score
    return data
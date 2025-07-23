import pandas as pd
from technical_analysis import technical_score
from datetime import datetime

def format_scores_to_dict(df: pd.DataFrame, use_ta: bool = True, ta_weight: float = 0.5) -> dict:
    """
    Converts a DataFrame with ['Ticker', 'Trade Date', 'Score'] into a nested dictionary:
    {
        'AAPL': {
            datetime.date(2023, 7, 1): 0.85,
            datetime.date(2023, 7, 10): 0.9,
        },
        ...
    }
    Optionally enhances score with a technical analysis overlay.
    """
    data = {}
    for row in df.itertuples(index=False):
        ticker = row[0]
        date = row[1]
        base_score = row[2]

        # Ensure date is a datetime.date object
        if isinstance(date, str):
            date = datetime.strptime(date, "%Y-%m-%d").date()

        # Apply TA score if applicable
        ta_score = None
        if use_ta:
            ta_score = technical_score(ticker, date)

        if ta_score is None or not isinstance(ta_score, (int, float)):
            final_score = base_score
        else:
            final_score = (1 - ta_weight) * base_score + ta_weight * ta_score

        # Store in nested dict
        if ticker not in data:
            data[ticker] = {}

        data[ticker][date] = final_score

    return data

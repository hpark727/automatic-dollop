import pandas as pd
from technical_analysis import technical_score
from datetime import datetime

def format_scores_to_dict(df: pd.DataFrame, use_ta: bool = True, ta_weight: float = 0.5) -> dict:
    data = {}
    for row in df.itertuples(index=False):
        ticker = row[0]
        date = row[1]
        base_score = row[2]

        if not isinstance(date, datetime):
            date = pd.to_datetime(date).date()
        else:
            date = date.date()
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

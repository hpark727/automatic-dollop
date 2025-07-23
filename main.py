from backtest import run_backtest
from insider_data import InsiderData
from datetime import datetime
from formatter import format_scores_to_dict

# Step 1: Generate signals
insider = InsiderData()
insider.get_data().clean_values().compute_score()
score_dict = format_scores_to_dict(insider.get_df())  # {ticker: {date: score}}

# Step 2: Define backtest params
start_date = "2024-01-01"
end_date = "2025-06-01"
initial_cash = 100000
hold_days = 60
top_n = 3

# Step 3: Run simulation
results = run_backtest(
    score_dict=score_dict,
    start=start_date,
    end=end_date,
    hold_days=hold_days,
    top_n=top_n,
    cash=initial_cash
)
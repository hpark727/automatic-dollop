from backtest import run_backtest
from insider_data import InsiderData
from formatter import format_scores_to_dict
from visualizer import plot_trade_returns, plot_portfolio_returns


def main():
    # Step 1: Generate signals
    insider = InsiderData()
    insider.get_data().clean_values().compute_score()
    score_dict = format_scores_to_dict(insider.get_df())

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

    print("\n===== BACKTEST RESULTS =====")
    for k, v in results.items():
        if k != 'trades':
            print(f"{k}: {v}")

    trades = results.get('trades', [])
    if not trades:
        print("No trades recorded.")
    else:
        plot_trade_returns(trades)
        plot_portfolio_returns(trades)


if __name__ == "__main__":
    main()

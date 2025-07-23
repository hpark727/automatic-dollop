import pandas as pd
import matplotlib.pyplot as plt


def _prepare_trade_df(trades: list) -> pd.DataFrame:
    """Helper to convert trade list into a sorted DataFrame."""
    df = pd.DataFrame(trades)
    df["exit_date"] = pd.to_datetime(df["exit_date"])
    df = df.sort_values("exit_date")
    return df


def plot_trade_returns(trades: list) -> None:
    """Plot cumulative profit/loss for each ticker over time."""
    if not trades:
        print("No trades to plot")
        return

    df = _prepare_trade_df(trades)

    pivot = df.pivot_table(
        index="exit_date",
        columns="ticker",
        values="pnl",
        aggfunc="sum",
    ).fillna(0)
    cumulative = pivot.cumsum()

    ax = cumulative.plot(marker="o", figsize=(10, 6))
    ax.set_title("Trade Profit/Loss by Ticker")
    ax.set_xlabel("Exit Date")
    ax.set_ylabel("Cumulative PnL")
    ax.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.show()


def plot_portfolio_returns(trades: list) -> None:
    """Plot cumulative profit/loss for the portfolio over time."""
    if not trades:
        print("No trades to plot")
        return

    df = _prepare_trade_df(trades)

    cumulative = df.set_index("exit_date")["pnl"].cumsum()

    ax = cumulative.plot(marker="o", figsize=(10, 6))
    ax.set_title("Portfolio Profit/Loss Over Time")
    ax.set_xlabel("Exit Date")
    ax.set_ylabel("Cumulative PnL")
    ax.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.show()

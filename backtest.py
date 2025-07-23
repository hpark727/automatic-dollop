import backtrader as bt
from strategy import InsiderStrategy
from datafeed import load_data

# backtest engine
def run_backtest(score_dict, start, end, hold_days=30, top_n=3, cash=100000):
    cerebro = bt.Cerebro()
    
    cerebro.broker.setcash(cash)
    cerebro.broker.setcommission(commission=0.001)

    tickers = list(score_dict.keys())  
    feeds = load_data(tickers, start, end)
    if not feeds:
        raise RuntimeError("No valid data feeds were loaded.")

    for feed in feeds:
        cerebro.adddata(feed)

    # Add analyzers
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')

    cerebro.addstrategy(
        InsiderStrategy,
        score_dict=score_dict,
        hold_days=hold_days,
        top_n=top_n
    )

    results = cerebro.run()
    strat = results[0]  # Only one strategy instance

    # Collect results
    sharpe = strat.analyzers.sharpe.get_analysis()
    drawdown = strat.analyzers.drawdown.get_analysis()
    returns = strat.analyzers.returns.get_analysis()

    #Print summary
    print("\n===== BACKTEST SUMMARY =====")
    print(f"Initial Cash: ${cash:,.2f}")
    print(f"Final Portfolio Value: ${cerebro.broker.getvalue():,.2f}")
    print(f"Total Return: {returns['rtot']*100:.2f}%")
    print(f"Annual Return: {returns['rnorm']*100:.2f}%")
    print(f"Sharpe Ratio: {sharpe.get('sharperatio', 'N/A'):.2f}")
    print(f"Max Drawdown: {drawdown['max']['drawdown']:.2f}%")

    cerebro.plot(style='candlestick')
    return {
        'final_value': cerebro.broker.getvalue(),
        'return_total': returns['rtot'],
        'return_annual': returns['rnorm'],
        'sharpe': sharpe.get('sharperatio', None),
        'max_drawdown': drawdown['max']['drawdown']
    }
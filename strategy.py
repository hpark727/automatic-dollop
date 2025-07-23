from datetime import timedelta
import backtrader as bt
import pandas as pd

class InsiderStrategy(bt.Strategy):
    def __init__(self, score_dict, hold_days=20, top_n=1):
        self.score_dict = score_dict
        self.hold_days = hold_days
        self.top_n = top_n
        self.open_trades = {} 

    def next(self):
        current_date = self.datas[0].datetime.date(0)
        executed_trades = 0
        scored_today = []
        for data in self.datas:
            ticker = data._name
            if current_date in self.score_dict.get(ticker, {}):
                score = self.score_dict[ticker][current_date]
                scored_today.append((data, score))
        

        scored_today.sort(key=lambda x: x[1], reverse=True)
        top_signals = scored_today[:self.top_n]
        print(top_signals)

        for data, score in top_signals:
            if not self.getposition(data).size:
                self.buy(data=data)
                executed_trades = executed_trades+1
                self.open_trades[data] = current_date + timedelta(days=self.hold_days)

        # Exit: Close positions that hit hold duration
        for data in list(self.open_trades.keys()):
            if current_date >= self.open_trades[data]:
                self.close(data=data)
                del self.open_trades[data]

        print(f"[{current_date}] Executed {executed_trades} trade(s)")

import yfinance as yf
import numpy as np

class StockScorer:
    def __init__(self, ticker):
        self.ticker = ticker
        self.stock = yf.Ticker(ticker)
        self.metrics = self.stock.info

    def safe_get(self, key):
        value = self.metrics.get(key)
        return np.nan if value in [None, 'None', 'NaN'] else value

    def compute_valuation_score(self):
        # Lower is better for these metrics
        forward_pe = self.safe_get('forwardPE')
        price_to_book = self.safe_get('priceToBook')
        ev_to_revenue = self.safe_get('enterpriseToRevenue')
        ev_to_ebitda = self.safe_get('enterpriseToEbitda')

        metrics = [forward_pe, price_to_book, ev_to_revenue, ev_to_ebitda]
        score = np.nanmean([-1 * val if not np.isnan(val) else np.nan for val in metrics])
        return score if not np.isnan(score) else 0

    def compute_growth_score(self):
        # Higher is better
        revenue_growth = self.safe_get('revenueGrowth')
        earnings_growth = self.safe_get('earningsQuarterlyGrowth')

        metrics = [revenue_growth, earnings_growth]
        score = np.nanmean([val if not np.isnan(val) else np.nan for val in metrics])
        return score if not np.isnan(score) else 0

    def compute_profitability_score(self):
        gross_margin = self.safe_get('grossMargins')
        op_margin = self.safe_get('operatingMargins')
        roe = self.safe_get('returnOnEquity')
        roa = self.safe_get('returnOnAssets')

        metrics = [gross_margin, op_margin, roe, roa]
        score = np.nanmean([val if not np.isnan(val) else np.nan for val in metrics])
        return score if not np.isnan(score) else 0        

    def compute_total_score(self, insider_score=0.0, weights=None):
        if weights is None:
            weights = {
                'insider': 0.4,
                'valuation': 0.2,
                'growth': 0.2,
                'profitability': 0.2
            }

        val_score = self.compute_valuation_score()
        growth_score = self.compute_growth_score()
        prof_score = self.compute_profitability_score()

        total_score = (
            weights['insider'] * insider_score +
            weights['valuation'] * val_score +
            weights['growth'] * growth_score +
            weights['profitability'] * prof_score
        )
        return total_score
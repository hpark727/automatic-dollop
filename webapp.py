from flask import Flask, request, render_template_string
from insider_data import InsiderData
from formatter import format_scores_to_dict
from backtest import run_backtest
from visualizer import plot_trade_returns, plot_portfolio_returns
import io
import base64
import matplotlib.pyplot as plt

app = Flask(__name__)

INDEX_HTML = """
<!doctype html>
<title>Insider Backtester</title>
<h1>Run Backtest</h1>
<form method=post>
  Start Date: <input type=date name=start value="{{start}}"><br>
  End Date: <input type=date name=end value="{{end}}"><br>
  <button type=submit>Run</button>
</form>
{% if metrics %}
<h2>Results</h2>
<ul>
  <li>Final Value: {{ metrics['final_value'] }}</li>
  <li>Total Return: {{ metrics['return_total'] }}</li>
  <li>Annual Return: {{ metrics['return_annual'] }}</li>
  <li>Sharpe Ratio: {{ metrics['sharpe'] }}</li>
  <li>Max Drawdown: {{ metrics['max_drawdown'] }}</li>
</ul>
{% endif %}
{% if trade_plot %}
  <h3>Trade PnL</h3>
  <img src="data:image/png;base64,{{ trade_plot }}">
{% endif %}
{% if portfolio_plot %}
  <h3>Portfolio PnL</h3>
  <img src="data:image/png;base64,{{ portfolio_plot }}">
{% endif %}
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    metrics = None
    trade_plot = None
    portfolio_plot = None
    start = request.form.get('start', '')
    end = request.form.get('end', '')
    if request.method == 'POST':
        insider = InsiderData()
        insider.get_data(start, end).clean_values().compute_score()
        score_dict = format_scores_to_dict(insider.get_df())
        result = run_backtest(score_dict, start, end)
        metrics = result
        trades = result.get('trades', [])
        if trades:
            fig = plot_trade_returns(trades, show=False)
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            trade_plot = base64.b64encode(buf.getvalue()).decode()
            plt.close(fig)

            fig = plot_portfolio_returns(trades, show=False)
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            portfolio_plot = base64.b64encode(buf.getvalue()).decode()
            plt.close(fig)
    return render_template_string(INDEX_HTML, metrics=metrics, trade_plot=trade_plot,
                                  portfolio_plot=portfolio_plot, start=start, end=end)

if __name__ == '__main__':
    app.run(debug=True)

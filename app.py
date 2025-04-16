"""
app.py: Flask web application for portfolio optimization via Monte Carlo simulation

- Loads financial data from GitHub CSV
- Allows user to set risk-free rate and number of simulations
- Displays efficient frontier, optimal portfolios, and asset allocations
"""
import io
import base64
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.exceptions import HTTPException

# Constants
DATA_URL = "https://raw.githubusercontent.com/gahoccode/Datasets/main/myport2.csv"
TRADING_DAYS_PER_YEAR = 252
DEFAULT_NUM_PORT = 5000
DEFAULT_RF_RATE = 0.0

app = Flask(__name__)
app.secret_key = "portfolio_secret_key"

# Utility Functions

def load_data(url: str) -> pd.DataFrame:
    """Load and preprocess dataset from GitHub CSV."""
    df = pd.read_csv(url)
    df = df.dropna()
    df.set_index(df.columns[0], inplace=True)
    return df

def calculate_log_returns(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate logarithmic returns of asset prices."""
    return np.log(df / df.shift(1)).dropna()

def run_monte_carlo(df: pd.DataFrame, num_port: int, risk_free_rate: float):
    """Run Monte Carlo simulation for portfolio optimization."""
    log_ret = calculate_log_returns(df)
    cov_matrix = log_ret.cov() * TRADING_DAYS_PER_YEAR
    mean_returns = log_ret.mean() * TRADING_DAYS_PER_YEAR
    n_assets = len(df.columns)
    all_wts = np.zeros((num_port, n_assets))
    port_returns = np.zeros(num_port)
    port_risk = np.zeros(num_port)
    sharpe_ratio = np.zeros(num_port)
    np.random.seed(42)
    for i in range(num_port):
        wts = np.random.uniform(size=n_assets)
        wts = wts / np.sum(wts)
        all_wts[i, :] = wts
        port_ret = np.sum(mean_returns * wts)
        port_sd = np.sqrt(np.dot(wts.T, np.dot(cov_matrix, wts)))
        port_returns[i] = port_ret
        port_risk[i] = port_sd
        sr = (port_ret - risk_free_rate) / port_sd if port_sd > 0 else 0.0
        sharpe_ratio[i] = sr
    results = {
        "all_wts": all_wts,
        "port_returns": port_returns,
        "port_risk": port_risk,
        "sharpe_ratio": sharpe_ratio,
        "mean_returns": mean_returns,
        "cov_matrix": cov_matrix
    }
    return results

def get_optimal_portfolios(results):
    """Extract indices and weights for optimal portfolios."""
    max_sr_idx = results["sharpe_ratio"].argmax()
    min_var_idx = results["port_risk"].argmin()
    return {
        "max_sr": {
            "idx": max_sr_idx,
            "ret": results["port_returns"][max_sr_idx],
            "risk": results["port_risk"][max_sr_idx],
            "sr": results["sharpe_ratio"][max_sr_idx],
            "wts": results["all_wts"][max_sr_idx]
        },
        "min_var": {
            "idx": min_var_idx,
            "ret": results["port_returns"][min_var_idx],
            "risk": results["port_risk"][min_var_idx],
            "sr": results["sharpe_ratio"][min_var_idx],
            "wts": results["all_wts"][min_var_idx]
        }
    }

def plot_efficient_frontier(results, optimal):
    """Generate efficient frontier plot with optimal portfolios highlighted."""
    fig, ax = plt.subplots(figsize=(8,6))
    scatter = ax.scatter(results["port_risk"], results["port_returns"], c=results["sharpe_ratio"], cmap='viridis', alpha=0.5)
    ax.scatter(optimal["max_sr"]["risk"], optimal["max_sr"]["ret"], c='red', marker='*', s=200, label='Max Sharpe Ratio')
    ax.scatter(optimal["min_var"]["risk"], optimal["min_var"]["ret"], c='blue', marker='*', s=200, label='Min Variance')
    ax.set_xlabel('Risk (Std Dev)')
    ax.set_ylabel('Expected Return')
    ax.set_title('Efficient Frontier')
    ax.legend()
    plt.colorbar(scatter, ax=ax, label='Sharpe Ratio')
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    img_b64 = base64.b64encode(buf.getvalue()).decode()
    return img_b64

def plot_weights_pie(asset_names, weights, title):
    """Generate a pie chart for portfolio weights."""
    fig, ax = plt.subplots()
    ax.pie(weights, labels=asset_names, autopct='%1.1f%%', startangle=90)
    ax.set_title(title)
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    img_b64 = base64.b64encode(buf.getvalue()).decode()
    return img_b64

# Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            rf_rate = float(request.form.get('risk_free_rate', DEFAULT_RF_RATE))
            num_port = int(request.form.get('num_port', DEFAULT_NUM_PORT))
            if num_port < 1000 or num_port > 20000:
                flash('Number of simulations must be between 1000 and 20000.', 'danger')
                return redirect(url_for('index'))
            return redirect(url_for('optimize', rf_rate=rf_rate, num_port=num_port))
        except Exception as e:
            flash(f'Invalid input: {e}', 'danger')
    return render_template('index.html', default_rf=DEFAULT_RF_RATE, default_num_port=DEFAULT_NUM_PORT)

@app.route('/optimize')
def optimize():
    try:
        rf_rate = float(request.args.get('rf_rate', DEFAULT_RF_RATE))
        num_port = int(request.args.get('num_port', DEFAULT_NUM_PORT))
        df = load_data(DATA_URL)
        results = run_monte_carlo(df, num_port, rf_rate)
        optimal = get_optimal_portfolios(results)
        ef_img = plot_efficient_frontier(results, optimal)
        max_sr_pie = plot_weights_pie(df.columns, optimal["max_sr"]["wts"], 'Max Sharpe Ratio Portfolio')
        min_var_pie = plot_weights_pie(df.columns, optimal["min_var"]["wts"], 'Min Variance Portfolio')
        return render_template('results.html',
            ef_img=ef_img,
            max_sr_pie=max_sr_pie,
            min_var_pie=min_var_pie,
            max_sr=optimal["max_sr"],
            min_var=optimal["min_var"],
            asset_names=list(df.columns),
            rf_rate=rf_rate,
            num_port=num_port
        )
    except Exception as e:
        flash(f'Error during optimization: {e}', 'danger')
        return redirect(url_for('index'))

@app.errorhandler(HTTPException)
def handle_exception(e):
    flash(f'HTTP Error: {e}', 'danger')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

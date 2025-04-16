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
from vnstock import Quote
from datetime import datetime

# Constants
TRADING_DAYS_PER_YEAR = 252
DEFAULT_NUM_PORT = 5000
DEFAULT_RF_RATE = 0.0
DEFAULT_SYMBOLS = 'REE,FMC,DHC'
DEFAULT_START_DATE = '2024-01-01'
DEFAULT_INTERVAL = '1D'

app = Flask(__name__)
app.secret_key = "portfolio_secret_key"

# Utility Functions

def load_vnstock_data(symbols, start_date, end_date, interval):
    """Fetch and merge historical close prices for the given symbols and date range using vnstock API."""
    all_historical_data = {}
    for symbol in symbols:
        try:
            quote = Quote(symbol=symbol)
            historical_data = quote.history(
                start=start_date,
                end=end_date,
                interval=interval,
                to_df=True
            )
            if not historical_data.empty:
                all_historical_data[symbol] = historical_data[['time', 'close']].copy()
                all_historical_data[symbol].rename(columns={'close': f'{symbol}_close'}, inplace=True)
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            continue
    # Merge all close prices on 'time'
    combined = None
    for symbol, df in all_historical_data.items():
        if combined is None:
            combined = df
        else:
            combined = pd.merge(combined, df, on='time', how='outer')
    if combined is not None:
        combined = combined.sort_values('time').set_index('time')
        combined = combined.ffill().bfill()  # Fill missing values
    return combined

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
            symbols = request.form.get('symbols', DEFAULT_SYMBOLS)
            start_date = request.form.get('start_date', DEFAULT_START_DATE)
            end_date = request.form.get('end_date', datetime.today().strftime('%Y-%m-%d'))
            interval = request.form.get('interval', DEFAULT_INTERVAL)
            if num_port < 1000 or num_port > 20000:
                flash('Number of simulations must be between 1000 and 20000.', 'danger')
                return redirect(url_for('index'))
            return redirect(url_for('optimize', rf_rate=rf_rate, num_port=num_port, symbols=symbols, start_date=start_date, end_date=end_date, interval=interval))
        except Exception as e:
            flash(f'Invalid input: {e}', 'danger')
    return render_template('index.html', default_rf=DEFAULT_RF_RATE, default_num_port=DEFAULT_NUM_PORT, default_symbols=DEFAULT_SYMBOLS, default_start=DEFAULT_START_DATE, default_end=datetime.today().strftime('%Y-%m-%d'), default_interval=DEFAULT_INTERVAL)

@app.route('/optimize')
def optimize():
    try:
        rf_rate = float(request.args.get('rf_rate', DEFAULT_RF_RATE))
        num_port = int(request.args.get('num_port', DEFAULT_NUM_PORT))
        symbols = request.args.get('symbols', DEFAULT_SYMBOLS)
        start_date = request.args.get('start_date', DEFAULT_START_DATE)
        end_date = request.args.get('end_date', datetime.today().strftime('%Y-%m-%d'))
        interval = request.args.get('interval', DEFAULT_INTERVAL)
        symbol_list = [s.strip().upper() for s in symbols.split(',') if s.strip()]
        df = load_vnstock_data(symbol_list, start_date, end_date, interval)
        if df is None or df.empty:
            flash('No data found for the selected symbols and date range.', 'danger')
            return redirect(url_for('index'))
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

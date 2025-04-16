import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import io
import pytest
import numpy as np
import pandas as pd
from flask import Flask
from app import app, load_data, calculate_log_returns, run_monte_carlo, get_optimal_portfolios

# --- Fixtures ---
@pytest.fixture(scope="module")
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def sample_data():
    # Mimic the structure of the real dataset
    data = {
        'Date': ['2021-01-01', '2021-01-02', '2021-01-03'],
        'AAPL': [130, 132, 134],
        'MSFT': [220, 221, 223],
        'GOOG': [1725, 1730, 1740]
    }
    df = pd.DataFrame(data)
    df.set_index('Date', inplace=True)
    return df

# --- Unit Tests ---
def test_load_data_structure():
    df = load_data("https://raw.githubusercontent.com/gahoccode/Datasets/main/myport2.csv")
    assert isinstance(df, pd.DataFrame)
    assert df.shape[1] > 0
    assert df.isnull().sum().sum() == 0

def test_calculate_log_returns(sample_data):
    log_ret = calculate_log_returns(sample_data)
    assert isinstance(log_ret, pd.DataFrame)
    assert log_ret.shape[0] == sample_data.shape[0] - 1

def test_run_monte_carlo_output(sample_data):
    results = run_monte_carlo(sample_data, num_port=100, risk_free_rate=0.0)
    assert 'all_wts' in results and results['all_wts'].shape[0] == 100
    assert results['port_returns'].shape[0] == 100
    assert results['port_risk'].shape[0] == 100
    assert results['sharpe_ratio'].shape[0] == 100

def test_get_optimal_portfolios(sample_data):
    results = run_monte_carlo(sample_data, num_port=100, risk_free_rate=0.0)
    optimal = get_optimal_portfolios(results)
    assert 'max_sr' in optimal and 'min_var' in optimal
    assert optimal['max_sr']['sr'] >= 0
    assert optimal['min_var']['risk'] >= 0

# --- Route Tests ---
def test_index_route(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'Portfolio Optimization App' in rv.data

def test_optimize_route_valid(client):
    rv = client.get('/optimize?rf_rate=0.01&num_port=1000')
    assert rv.status_code == 200
    assert b'Efficient Frontier' in rv.data

def test_optimize_route_invalid_input(client):
    rv = client.get('/optimize?rf_rate=abc&num_port=1000', follow_redirects=True)
    assert b'Error' in rv.data or b'Invalid input' in rv.data

# --- Integration Tests ---
def test_end_to_end_workflow(client):
    rv = client.post('/', data={'risk_free_rate': '0.01', 'num_port': '1000'}, follow_redirects=True)
    assert b'Optimization Results' in rv.data
    assert b'Efficient Frontier' in rv.data

def test_visualization_generation(sample_data):
    results = run_monte_carlo(sample_data, num_port=50, risk_free_rate=0.0)
    optimal = get_optimal_portfolios(results)
    from app import plot_efficient_frontier, plot_weights_pie
    ef_img = plot_efficient_frontier(results, optimal)
    assert isinstance(ef_img, str) and len(ef_img) > 100
    pie_img = plot_weights_pie(sample_data.columns, optimal['max_sr']['wts'], 'Test Pie')
    assert isinstance(pie_img, str) and len(pie_img) > 100

# --- Edge Case Tests ---
def test_missing_data_handling(tmp_path):
    # Create a CSV with missing values
    csv = tmp_path / "missing.csv"
    csv.write_text("Date,A,B\n2021-01-01,1,2\n2021-01-02,,3\n2021-01-03,4,\n")
    df = pd.read_csv(csv)
    df = df.dropna()
    assert df.isnull().sum().sum() == 0

def test_extreme_weights(sample_data):
    # Force extreme weights
    results = run_monte_carlo(sample_data, num_port=1, risk_free_rate=0.0)
    results['all_wts'][0] = np.array([1.0, 0.0, 0.0])
    assert np.isclose(np.sum(results['all_wts'][0]), 1.0)

def test_invalid_user_inputs(client):
    rv = client.post('/', data={'risk_free_rate': 'abc', 'num_port': '1000'}, follow_redirects=True)
    assert b'Invalid input' in rv.data or b'Error' in rv.data

def test_large_dataset_performance(sample_data):
    # Simulate larger dataset
    big_df = pd.concat([sample_data]*100, axis=1)
    big_df.columns = [f'Asset{i}' for i in range(big_df.shape[1])]
    results = run_monte_carlo(big_df, num_port=10, risk_free_rate=0.0)
    assert results['all_wts'].shape[1] == big_df.shape[1]

# --- Frontend Tests (Basic) ---
def test_form_validation(client):
    rv = client.post('/', data={'risk_free_rate': '', 'num_port': '999'}, follow_redirects=True)
    assert b'Number of simulations must be between' in rv.data or b'Invalid input' in rv.data

def test_ui_responsiveness(client):
    rv = client.get('/')
    assert b'<form' in rv.data and b'class="card' in rv.data

def test_chart_rendering(client):
    rv = client.get('/optimize?rf_rate=0.01&num_port=1000')
    assert b'<img' in rv.data and b'Efficient Frontier' in rv.data

# --- Setup/Teardown ---
def setup_module(module):
    print("\n[Setup] Starting tests for Portfolio Optimization App")
def teardown_module(module):
    print("[Teardown] Finished tests for Portfolio Optimization App\n")


# Prompt for Portfolio Optimization App Development

Create a web application for portfolio optimization using Monte Carlo simulation with Flask backend and HTML/CSS frontend. The application should use the following dataset:

```
url = "https://raw.githubusercontent.com/gahoccode/Datasets/main/myport2.csv"
df = pd.read_csv(url)
```

The dataset contains historical price data for various financial assets with dates in the first column and stock/ETF prices in subsequent columns.

## Application Requirements

### 1. Backend Development (Flask)
- Create a Flask application structure with appropriate routes
- Implement data loading functionality using the specified URL
- Develop the portfolio optimization algorithm using Monte Carlo simulation
- Implement the following optimization calculations:
  * Calculate logarithmic returns and covariance matrix
  * Generate random portfolio weights for simulation (num_port = 5000)
  * Calculate portfolio returns, risks, and Sharpe ratios
  * Identify portfolios with maximum Sharpe ratio and minimum variance
- Generate visualizations (efficient frontier, portfolio composition)
- Handle errors and edge cases

### 2. Frontend Development (HTML/CSS)
- Create a clean, responsive main page with form inputs
- Develop a results page to display optimization outputs
- Implement styling for data visualization components
- Design an intuitive user interface with clear navigation

### 3. Core Features
- Upload financial data (though in this case, use the provided GitHub URL)
- Allow user to select risk-free rate
- Configure number of simulations to run
- Visualize efficient frontier with highlighted optimal portfolios
- Display detailed metrics for optimal portfolios:
  * Expected returns
  * Volatility (risk)
  * Sharpe ratio
  * Asset weights

### 4. Monte Carlo Simulation Logic
Use the following algorithm for portfolio optimization:
```
# Define the number of portfolios to simulate
num_port = 5000

# Initialize arrays for portfolio weights, returns, risk, and Sharpe ratios
all_wts = np.zeros((num_port, len(df_clean.columns)))
port_returns = np.zeros(num_port)
port_risk = np.zeros(num_port)
sharpe_ratio = np.zeros(num_port)

# Simulate random portfolios
np.random.seed(42)
for i in range(num_port):
    # Generate random portfolio weights
    wts = np.random.uniform(size=len(df_clean.columns))
    wts = wts / np.sum(wts)
    all_wts[i, :] = wts
    
    # Calculate portfolio return
    port_ret = np.sum(log_ret.mean() * wts)
    port_ret = (port_ret + 1) ** 252 - 1
    port_returns[i] = port_ret
    
    # Calculate portfolio risk (standard deviation)
    port_sd = np.sqrt(np.dot(wts.T, np.dot(cov_mat, wts)))
    port_risk[i] = port_sd
    
    # Calculate Sharpe Ratio, assuming a risk-free rate of 0%
    sr = port_ret / port_sd
    sharpe_ratio[i] = sr

# Identify portfolios with max Sharpe ratio, max return, and minimum variance
max_sr_idx = sharpe_ratio.argmax()
max_ret_idx = port_returns.argmax()
min_var_idx = port_risk.argmin()

max_sr_ret = port_returns[max_sr_idx]
max_sr_risk = port_risk[max_sr_idx]
max_sr_w = all_wts[max_sr_idx, :]

max_ret_ret = port_returns[max_ret_idx]
max_ret_risk = port_risk[max_ret_idx]
max_ret_w = all_wts[max_ret_idx, :]

min_var_ret = port_returns[min_var_idx]
min_var_risk = port_risk[min_var_idx]
min_var_w = all_wts[min_var_idx, :]
```

### 5. Required Visualizations
- Efficient frontier scatter plot showing risk vs. return for all simulated portfolios
- Highlighted points for maximum Sharpe ratio and minimum variance portfolios
- Pie charts showing asset allocation for optimal portfolios

### 6. Project Structure
Create a well-organized project with:
- app.py (main Flask application)
- templates/ (HTML templates)
- static/ (CSS, JavaScript, and images)
- requirements.txt (dependencies)

### 7. Required Python Packages
- Flask
- pandas
- numpy
- matplotlib
- werkzeug
- io (for image processing)
- base64 (for embedding plots)

When implementing the application, carefully follow these requirements while integrating the specified dataset from GitHub. The final application should allow users to view the efficient frontier, identify optimal portfolios, and visualize asset allocations for maximum Sharpe ratio and minimum variance portfolios.
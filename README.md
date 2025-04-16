# Portfolio Optimization Web Application

A modern Flask-based web application for portfolio optimization using Monte Carlo simulation. This project enables users to analyze and optimize investment portfolios, visualize the efficient frontier, and identify optimal asset allocations interactively.

## Features
- **Automated Data Loading:** Loads financial asset price data directly from a GitHub CSV.
- **Monte Carlo Simulation:** Simulates thousands of random portfolios to estimate returns, risk, and Sharpe ratios.
- **Efficient Frontier Visualization:** Interactive charts showing risk vs. return for all simulated portfolios.
- **Optimal Portfolio Identification:** Highlights portfolios with maximum Sharpe ratio and minimum variance.
- **Asset Allocation:** Pie charts for optimal portfolio weights.
- **User Input:** Configure risk-free rate and number of simulations.
- **Error Handling:** User-friendly error messages and input validation.
- **Performance:** Efficient calculations, supports large datasets.
- **Responsive Frontend:** Clean, mobile-friendly UI with Bootstrap styling.
- **Comprehensive Testing:** Unit, integration, and edge case tests using pytest.

## Usage Instructions

### 1. Clone or Download the Project
Copy or clone the repository to your local machine.

### 2. Create and Activate a Virtual Environment (Windows)
```sh
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```sh
pip install -r requirements.txt
```
Or with uv:
```sh
uv pip install -r requirements.txt
```

### 4. Run the Application
```sh
python app.py
```
Visit [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in your browser.

### 5. Using the App
- Enter your desired risk-free rate (%) and number of simulations (1,000–20,000 recommended).
- Click **Optimize Portfolio**.
- View the efficient frontier, optimal portfolio metrics, and asset allocation charts on the results page.
- Use the **Back to Main Page** button to run new scenarios.

### 6. Run the Test Suite
```sh
pytest
```
All tests should pass if the app is set up correctly.

### Troubleshooting
- Ensure your virtual environment is activated before running or testing the app.
- If you encounter dependency issues, re-run the install command or check `pyproject.toml`.
- For large datasets, increase available memory or reduce the number of simulations.

## Project Architecture

### Data Source Configuration
- **Where to Update Data Link:**
  - The financial data source URL is set in the `DATA_URL` constant at the top of [`app.py`](app.py).
  - To use a different dataset, edit the `DATA_URL` value in `app.py`.
  - The data loading logic is implemented in the `load_data` function in the same file.

### Frontend
- **HTML Templates (`templates/`):**
  - `index.html`: Main page with user input form. This template is rendered by the Flask route `/` (see `app.py`). When users visit the site, the Flask backend serves `index.html`, displaying the form for risk-free rate and simulation count. When the form is submitted, the data is sent to the backend, which processes the input and redirects to the results page (`/optimize` route).
  - `results.html`: Results display with charts and metrics, rendered after optimization is completed.
- **Static Assets (`static/`):**
  - `css/style.css`: Custom responsive styling.
  - `js/script.js`: Client-side form validation and UI enhancements.
- **User Experience:** Responsive, accessible, and visually clear interface using Bootstrap.

### Testing
- **Test Suite (`tests/test_app.py`):**
  - Unit tests for backend logic
  - Route and integration tests
  - Edge case and frontend validation tests
- **Fixtures:** Sample data for isolated, repeatable tests

### Directory Structure
```
flasksim/
├── app.py
├── requirements.txt
├── pyproject.toml
├── README.md
├── templates/
│   ├── index.html
│   └── results.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
└── tests/
    └── test_app.py
```

## Author & Credits
- Project created by [Your Name]
- Dataset from [gahoccode/Datasets](https://github.com/gahoccode/Datasets)

For further customization, deployment, or support, please contact the author or open an issue.

## Notes
- Data source: https://raw.githubusercontent.com/gahoccode/Datasets/main/myport2.csv
- All dependencies are pinned for reproducibility.

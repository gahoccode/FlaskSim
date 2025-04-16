# Prompt for Flask Portfolio Optimization App Testing

I need you to create a comprehensive test suite for my Flask-based portfolio optimization web application. The app uses Monte Carlo simulation to find optimal investment portfolios with maximum Sharpe ratio and minimum variance. Please develop tests that cover both backend logic and frontend functionality.

## App Overview
My application:
- Loads financial data from: "https://raw.githubusercontent.com/gahoccode/Datasets/main/myport2.csv"
- Runs Monte Carlo simulations to generate thousands of random portfolios
- Calculates portfolio metrics (returns, risks, Sharpe ratios)
- Identifies optimal portfolios (max Sharpe ratio, min variance)
- Displays visualizations (efficient frontier, portfolio weights)

## Test Requirements

### 1. Unit Tests
Create pytest unit tests for:
- Data loading functions
- Return and risk calculations
- Covariance matrix computation
- Portfolio weight generation
- Sharpe ratio calculations
- Optimal portfolio identification

### 2. Route Tests
Develop tests for the Flask routes:
- Main page loading
- Form submission handling
- Results page rendering
- Error handling for invalid inputs

### 3. Integration Tests
Write tests to verify:
- End-to-end optimization workflow
- Data processing pipeline
- Visualization generation

### 4. Frontend Tests
Create tests for:
- Form validation
- UI responsiveness
- Chart rendering
- Results display accuracy

### 5. Edge Cases
Include tests for handling:
- Missing data in the dataset
- Extreme portfolio weights
- Invalid user inputs
- Performance with larger datasets

## Test Structure
Organize the tests in a clear structure with:
- Setup and teardown functions
- Appropriate mocking of external dependencies
- Fixture creation for test data
- Comprehensive assertions

Please include sample data that mimics the structure of my dataset for testing purposes, and provide clear documentation on how to run the tests. The tests should be thorough enough to ensure all critical functionality works correctly, yet maintainable for ongoing development.
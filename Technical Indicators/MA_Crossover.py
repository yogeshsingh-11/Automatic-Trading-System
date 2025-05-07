import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import matplotlib.pyplot as plt
from sklearn.model_selection import ParameterGrid

# Fetch historical OHLC price data for an asset
def fetch_data(ticker, start, end):
    data = yf.download(ticker, start=start, end=end)
    data = data[['Open', 'High', 'Low', 'Close']]
    return data

# Calculate moving averages
def calculate_moving_averages(data, short_window, long_window):
    data['Short_MA'] = data['Close'].rolling(window=short_window).mean()
    data['Long_MA'] = data['Close'].rolling(window=long_window).mean()
    return data

# Implement moving average crossover strategy
def implement_strategy(data):
    data['Signal'] = 0
    data.loc[data['Short_MA'] > data['Long_MA'], 'Signal'] = 1
    data.loc[data['Short_MA'] <= data['Long_MA'], 'Signal'] = -1
    data['Position'] = data['Signal'].shift(1)  # Shift to avoid lookahead bias
    return data

# Backtest the strategy
def backtest(data):
    if 'Position' not in data.columns:
        raise KeyError("'Position' column not found. Ensure the strategy is implemented before backtesting.")

    data['Daily_Return'] = data['Close'].pct_change()
    data['Strategy_Return'] = data['Position'] * data['Daily_Return']

    # Fill missing values in Strategy_Return if any
    data['Strategy_Return'].fillna(0, inplace=True)

    # Performance metrics
    total_return = np.exp(data['Strategy_Return'].sum()) - 1
    sharpe_ratio = data['Strategy_Return'].mean() / data['Strategy_Return'].std() * np.sqrt(252) if data['Strategy_Return'].std() != 0 else 0
    cumulative_returns = (1 + data['Strategy_Return']).cumprod()
    max_drawdown = (cumulative_returns / cumulative_returns.cummax() - 1).min()

    return total_return, sharpe_ratio, max_drawdown


# Visualization
def plot_results(data):
    plt.figure(figsize=(14, 7))
    plt.plot(data['Close'], label='Close Price', alpha=0.5)
    plt.plot(data['Short_MA'], label='Short-term MA', alpha=0.75)
    plt.plot(data['Long_MA'], label='Long-term MA', alpha=0.75)
    plt.legend()
    plt.title('Moving Average Crossover Strategy')
    plt.show()

    # Check if Strategy_Return exists to avoid KeyError
    if 'Strategy_Return' in data.columns:
        # Strategy performance
        plt.figure(figsize=(14, 7))
        (1 + data['Strategy_Return']).cumprod().plot(label='Strategy', alpha=0.75)
        (1 + data['Daily_Return']).cumprod().plot(label='Buy & Hold', alpha=0.75)
        plt.legend()
        plt.title('Cumulative Returns')
        plt.show()
    else:
        print("Error: 'Strategy_Return' column not found in data.")

# Main script
if __name__ == "__main__":
    # Parameters
    ticker = "AAPL"  
    # ticker = "RELIANCE.NS"

    start_date = "2016-01-01"
    end_date = datetime.now().strftime('%Y-%m-%d')
    short_range = range(1, 50)  # Example range for short moving average
    long_range = range(10, 250)  # Example range for long moving average

    # Find the best Sharpe Ratio
    best_params, best_sharpe = optimize_sharpe_ratio(ticker, start_date, end_date, short_range, long_range)
    print(f"Best Parameters: Short Window = {best_params[0]}, Long Window = {best_params[1]}")
    print(f"Best Sharpe Ratio: {best_sharpe:.2f}")

    # Fetch data and plot results for the best parameters
    data = fetch_data(ticker, start_date, end_date)
    data = calculate_moving_averages(data, best_params[0], best_params[1])
    data = implement_strategy(data)

    # Backtest the strategy
    try:
        total_return, sharpe_ratio, max_drawdown = backtest(data)
        print(f"Sharpe Ratio: {sharpe_ratio: .3}")
        print(f"Total Return: {total_return:.2%}")
        print(f"Maximum Drawdown: {max_drawdown:.2%}")
    except KeyError as e:
        print(f"Error during backtesting: {e}")

    plot_results(data)


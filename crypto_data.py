# Step 1: Install Required Libraries
# In  terminal
# pip install requests pandas scikit-learn openpyxl

# File: crypto_data.py
import requests
import pandas as pd
from datetime import datetime, timedelta

# Step 2: Set Up API and Fetch Data
# API Research and Selection
# Let's use CoinGecko API, which is free and reliable for cryptocurrency data.
BASE_URL = "https://api.coingecko.com/api/v3"

# Function to fetch historical data for cryptocurrency pairs
def fetch_crypto_data(crypto_pair, start_date):
    """
    Fetch historical daily data for a given cryptocurrency pair.
    :param crypto_pair: Cryptocurrency pair (e.g., "bitcoin/usd").
    :param start_date: Start date in 'YYYY-MM-DD' format.
    :return: Pandas DataFrame with date, open, high, low, and close columns.
    """
    try:
        crypto_id, vs_currency = crypto_pair.lower().split('/')
        start_date_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
        to_date_ts = int(datetime.now().timestamp())

        # Limit the date range to avoid unauthorized errors
        max_days = 14 * 86400  # Fetching data for the last 14 days
        if (to_date_ts - start_date_ts) > max_days:
            start_date_ts = to_date_ts - max_days

        # Fetch the data from the API
        response = requests.get(f"{BASE_URL}/coins/{crypto_id}/market_chart/range",
                                params={
                                    "vs_currency": vs_currency,
                                    "from": start_date_ts,
                                    "to": to_date_ts
                                })
        response.raise_for_status()
        data = response.json()

        # Prepare DataFrame
        df = pd.DataFrame(data['prices'], columns=['Date', 'Close'])
        df['Date'] = pd.to_datetime(df['Date'], unit='ms')
        df['Open'] = df['Close'].shift(1)
        df['High'] = df['Close'].rolling(window=2).max()
        df['Low'] = df['Close'].rolling(window=2).min()
        df = df.dropna().tail(14)  # Ensure we only keep the last 14 days of data
        return df[['Date', 'Open', 'High', 'Low', 'Close']]

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as e:
        print(f"Error retrieving data: {e}")
    return pd.DataFrame()

# Step 3: Calculate Metrics
# Function to calculate various historical and future metrics
def calculate_metrics(data, variable1=7, variable2=5):
    """
    Calculate various metrics for historical and future price analysis.
    :param data: DataFrame containing historical data.
    :param variable1: Look-back period for historical high/low metrics.
    :param variable2: Look-forward period for future high/low metrics.
    :return: DataFrame with new calculated metrics.
    """
    data = data.copy()
    # Historical High and Low Prices
    data[f'High_Last_{variable1}_Days'] = data['High'].rolling(window=variable1, min_periods=1).max()
    data[f'Low_Last_{variable1}_Days'] = data['Low'].rolling(window=variable1, min_periods=1).min()
    
    # Days Since High/Low
    data[f'Days_Since_High_Last_{variable1}_Days'] = data['High'].rolling(window=variable1, min_periods=1).apply(lambda x: len(x) - 1 - x[::-1].argmax()).astype(int)
    data[f'Days_Since_Low_Last_{variable1}_Days'] = data['Low'].rolling(window=variable1, min_periods=1).apply(lambda x: len(x) - 1 - x[::-1].argmin()).astype(int)
    
    # Future High and Low Prices
    data[f'High_Next_{variable2}_Days'] = data['High'].shift(-variable2).rolling(window=variable2, min_periods=1).max()
    data[f'Low_Next_{variable2}_Days'] = data['Low'].shift(-variable2).rolling(window=variable2, min_periods=1).min()

    # Percentage Difference Metrics
    data[f'%_Diff_From_High_Last_{variable1}_Days'] = ((data['Close'] - data[f'High_Last_{variable1}_Days']) / data[f'High_Last_{variable1}_Days']) * 100
    data[f'%_Diff_From_Low_Last_{variable1}_Days'] = ((data['Close'] - data[f'Low_Last_{variable1}_Days']) / data[f'Low_Last_{variable1}_Days']) * 100
    data[f'%_Diff_From_High_Next_{variable2}_Days'] = ((data['Close'] - data[f'High_Next_{variable2}_Days']) / data[f'High_Next_{variable2}_Days']) * 100
    data[f'%_Diff_From_Low_Next_{variable2}_Days'] = ((data['Close'] - data[f'Low_Next_{variable2}_Days']) / data[f'Low_Next_{variable2}_Days']) * 100

    return data

# Step 4: Save Data to Excel
def save_to_excel(data, filename="crypto_data_analysis.xlsx"):
    """
    Save the DataFrame to an Excel workbook.
    :param data: DataFrame containing the data.
    :param filename: The name of the output Excel file.
    """
    try:
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            data.to_excel(writer, index=False, sheet_name='CryptoData')
            workbook = writer.book
            worksheet = writer.sheets['CryptoData']

            # Set the width for each column
            for col in worksheet.columns:
                max_length = max(len(str(cell.value)) for cell in col) + 2
                worksheet.column_dimensions[col[0].column_letter].width = max_length

        print(f"Data successfully saved to {filename}")
    except Exception as e:
        print(f"Error saving data to Excel: {e}")

# Usage example
if __name__ == "__main__":
    # Example: Generate Excel from fetched and calculated data
    crypto_pair = "bitcoin/usd"
    start_date = "2023-01-01"
    df = fetch_crypto_data(crypto_pair, start_date)
    if not df.empty:
        metrics_df = calculate_metrics(df, variable1=7, variable2=5)
        # Save the DataFrame to an external Excel workbook
        save_to_excel(metrics_df, filename="Crypto_Historical_Data.xlsx")

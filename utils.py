import pandas as pd
import os

def load_data():
    """Load expense data from CSV file"""
    if not os.path.exists('data'):
        os.makedirs('data')

    try:
        if os.path.exists('data/expenses.csv'):
            df = pd.read_csv('data/expenses.csv')
            df['Date'] = pd.to_datetime(df['Date']).dt.date
            # Set default currency for old data if needed
            if 'Currency' not in df.columns:
                df['Currency'] = 'USD'
            return df
        return pd.DataFrame(columns=['Date', 'Amount', 'Category', 'Description', 'Currency'])
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame(columns=['Date', 'Amount', 'Category', 'Description', 'Currency'])

def save_data(df):
    """Save expense data to CSV file"""
    try:
        df.to_csv('data/expenses.csv', index=False)
    except Exception as e:
        print(f"Error saving data: {e}")

def calculate_budget_status(total_spent, budget):
    """Calculate budget status and return appropriate message"""
    remaining = budget - total_spent
    if remaining < 0:
        return "over", abs(remaining)
    elif remaining < (0.2 * budget):
        return "warning", remaining
    return "under", remaining
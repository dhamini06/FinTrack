import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from utils import load_data, save_data, calculate_budget_status

# Page config
st.set_page_config(
    page_title="FinTrack - Student Finance Manager",
    page_icon="💰",
    layout="wide"
)

# Initialize session state
if 'monthly_budget' not in st.session_state:
    st.session_state.monthly_budget = 1000.0
if 'currency' not in st.session_state:
    st.session_state.currency = 'USD'
if 'balance' not in st.session_state:
    st.session_state.balance = 1000.0

# Currency symbols
currency_symbols = {
    'USD': '$',
    'EUR': '€',
    'GBP': '£',
    'JPY': '¥',
    'INR': '₹'
}

# Main title
st.title("💰 FinTrack - Student Finance Manager")

# Sidebar
with st.sidebar:
    st.header("Budget Settings")

    # Currency selection
    st.session_state.currency = st.selectbox(
        "Select Currency",
        options=list(currency_symbols.keys()),
        index=list(currency_symbols.keys()).index(st.session_state.currency)
    )

    symbol = currency_symbols[st.session_state.currency]

    # Budget and initial balance setting
    st.session_state.monthly_budget = st.number_input(
        f"Set Monthly Budget ({symbol})",
        min_value=0.0,
        value=st.session_state.monthly_budget,
        step=50.0
    )

    if 'balance_initialized' not in st.session_state:
        st.session_state.balance = st.number_input(
            f"Set Initial Balance ({symbol})",
            min_value=0.0,
            value=st.session_state.balance,
            step=50.0
        )
        if st.button("Confirm Initial Balance"):
            st.session_state.balance_initialized = True
            st.success("Initial balance set!")

    st.markdown("---")
    st.markdown("""
    ### Categories
    - 📚 Education
    - 🍔 Food
    - 🏠 Housing
    - 🚌 Transportation
    - 🎮 Entertainment
    - 📱 Utilities
    - 🛍️ Shopping
    - 📝 Other
    """)

# Load existing data
df = load_data()

# Input section
st.header("📝 Add New Expense")
with st.form("expense_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        amount = st.number_input(f"Amount ({symbol})", min_value=0.0, step=0.01)

    with col2:
        category = st.selectbox(
            "Category",
            ["Education", "Food", "Housing", "Transportation", 
             "Entertainment", "Utilities", "Shopping", "Other"]
        )

    with col3:
        date = st.date_input("Date", datetime.now())

    description = st.text_input("Description")
    submitted = st.form_submit_button("Add Expense")

  st.header("📝 Add New Expense")

with st.form("expense_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        amount = st.number_input(f"Amount ({symbol})", min_value=0.0, step=0.01)

    with col2:
        category = st.selectbox(
            "Category",
            ["Education", "Food", "Housing", "Transportation",
             "Entertainment", "Utilities", "Shopping", "Other"]
        )

    with col3:
        date = st.date_input("Date", datetime.now())

    description = st.text_input("Description")
    submitted = st.form_submit_button("Add Expense")

# ✅ Make sure this part is at the same indentation level as `with st.form()`
if submitted and amount > 0:
    # Update balance
    st.session_state.balance -= amount

    new_expense = pd.DataFrame([{
        'Date': date,
        'Amount': amount,
        'Category': category,
        'Description': description,
        'Currency': st.session_state.currency
    }])

    # Load the latest data and add the new expense
    df = load_data()
    df = pd.concat([df, new_expense], ignore_index=True)
    save_data(df)

    # Show success message
    st.success("Expense added successfully! ✅")

    # Use session state to trigger refresh instead of st.experimental_rerun()
    st.session_state.expense_added = True

# ✅ This should be at the **same indentation level** as `st.header()`
if 'expense_added' in st.session_state and st.session_state.expense_added:
    st.session_state.expense_added = False
    st.experimental_rerun()

# Dashboard
st.header("📊 Expense Dashboard")

# Calculate current month's expenses
current_month = datetime.now().month
current_year = datetime.now().year
monthly_mask = (pd.to_datetime(df['Date']).dt.month == current_month) & \
               (pd.to_datetime(df['Date']).dt.year == current_year)
monthly_expenses = df[monthly_mask]
total_spent = monthly_expenses['Amount'].sum()

# Budget status
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Current Balance", f"{symbol}{st.session_state.balance:.2f}")
with col2:
    st.metric("Total Spent", f"{symbol}{total_spent:.2f}")
with col3:
    st.metric("Monthly Budget", f"{symbol}{st.session_state.monthly_budget:.2f}")
with col4:
    remaining = st.session_state.monthly_budget - total_spent
    status = "🟢 Under Budget" if remaining >= 0 else "🔴 Over Budget!"
    st.metric("Remaining Budget", f"{symbol}{remaining:.2f}", status)

# Alert for overspending
if remaining < 0:
    st.error(f"⚠️ Alert: You have exceeded your monthly budget by {symbol}{abs(remaining):.2f}!")
elif remaining < (0.2 * st.session_state.monthly_budget):
    st.warning("⚠️ Warning: You are close to exceeding your monthly budget!")

# Visualizations
col1, col2 = st.columns(2)

with col1:
    st.subheader("Category Distribution")
    if not monthly_expenses.empty:
        category_data = monthly_expenses.groupby('Category')['Amount'].sum().reset_index()
        fig = px.pie(category_data, values='Amount', names='Category', hole=0.4)
        fig.update_layout(title=f"Total Spent: {symbol}{total_spent:.2f}")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No expenses recorded this month.")

with col2:
    st.subheader("Daily Expenses")
    if not monthly_expenses.empty:
        daily_expenses = monthly_expenses.groupby('Date')['Amount'].sum().reset_index()
        fig = px.line(daily_expenses, x='Date', y='Amount', markers=True)
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title=f"Amount ({symbol})",
            title=f"Daily Spending Pattern"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No expenses recorded this month.")

# Expense History
st.header("📜 Expense History")
if not df.empty:
    st.dataframe(
        df.sort_values('Date', ascending=False),
        column_config={
            "Date": st.column_config.DateColumn("Date"),
            "Amount": st.column_config.NumberColumn(f"Amount ({symbol})", format=f"{symbol}%.2f"),
            "Category": "Category",
            "Description": "Description",
            "Currency": "Currency"
        },
        hide_index=True
    )
else:
    st.info("No expenses recorded yet. Start by adding your first expense!")

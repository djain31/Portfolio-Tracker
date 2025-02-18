import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import yfinance as yf
from datetime import datetime

# --- Authentication Setup ---
credentials = {
    "usernames": {
        "fund_manager": {"email": "manager@example.com", "name": "Fund Manager", "password": "hashed_password"},
        "user": {"email": "you@example.com", "name": "You", "password": "hashed_password"}
    }
}

authenticator = stauth.Authenticate(credentials, "app_cookie", "random_key", cookie_expiry_days=1)
name, auth_status, username = authenticator.login("Login", "main")

if auth_status:
    st.sidebar.success(f"Welcome, {name}!")
    authenticator.logout("Logout", "sidebar")
    
    # --- Portfolio Tracking ---
    st.title("📈 Portfolio Dashboard")
    
    # Sample transaction data (Replace with DB storage)
    transactions = pd.DataFrame([
        {"Date": "2024-02-01", "Stock": "AAPL", "Type": "Buy", "Price": 150, "Quantity": 10},
        {"Date": "2024-02-05", "Stock": "AAPL", "Type": "Sell", "Price": 160, "Quantity": 5},
        {"Date": "2024-02-10", "Stock": "TSLA", "Type": "Buy", "Price": 700, "Quantity": 2},
    ])
    
    # Display transactions
    st.subheader("💼 Transaction History")
    st.dataframe(transactions)
    
    # Get unique stocks
    stocks = transactions["Stock"].unique()
    
    # Fetch live stock prices
    def get_live_prices(stocks):
        prices = {}
        for stock in stocks:
            ticker = yf.Ticker(stock)
            prices[stock] = ticker.history(period="1d")["Close"].iloc[-1]
        return prices
    
    live_prices = get_live_prices(stocks)
    
    # Calculate portfolio value
    st.subheader("📊 Portfolio Summary")
    portfolio = transactions.groupby("Stock").agg({"Quantity": "sum", "Price": "mean"}).reset_index()
    portfolio["Live Price"] = portfolio["Stock"].map(live_prices)
    portfolio["Value"] = portfolio["Quantity"] * portfolio["Live Price"]
    st.dataframe(portfolio)
    
    # Add a new transaction
    st.sidebar.subheader("➕ Add Transaction")
    stock = st.sidebar.text_input("Stock Symbol")
    trans_type = st.sidebar.selectbox("Transaction Type", ["Buy", "Sell"])
    price = st.sidebar.number_input("Price", min_value=1.0)
    quantity = st.sidebar.number_input("Quantity", min_value=1)
    
    if st.sidebar.button("Submit Transaction"):
        new_trans = pd.DataFrame([{ "Date": datetime.today().strftime('%Y-%m-%d'), "Stock": stock, "Type": trans_type, "Price": price, "Quantity": quantity }])
        transactions = pd.concat([transactions, new_trans], ignore_index=True)
        st.sidebar.success("Transaction Added!")

elif auth_status is False:
    st.error("Incorrect username or password")
elif auth_status is None:
    st.warning("Please enter your credentials.")

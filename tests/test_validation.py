import pytest
import pandas as pd
import numpy as np
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.validation_utils import DataValidator

@pytest.fixture
def mock_transaction_df():
    """
    Returns a dummy transaction DataFrame with predefined errors for testing.
    """
    data = [
        {
            "Transaction_ID": "TXN-001",
            "Customer_ID": "CUST-1001",
            "Date": "2023-01-01",
            "Time": "12:00:00",
            "Month": 1,
            "Quarter": 1,
            "Year": 2023,
            "Week_Number": 1,
            "Day": 1,
            "Day_of_Week": "Sunday",
            "Weekend": "Yes",
            "Category": "Groceries",
            "Sub_Category": "Supermarket Groceries",
            "Description": "Weekly groc buy",
            "Merchant": "Whole Foods",
            "Merchant_Category": "Groceries",
            "Transaction_Type": "Expense",
            "Amount": 150.00,
            "Currency": "INR",
            "Payment_Mode": "Credit Card",
            "Account_Type": "Credit Card",
            "City": "New York",
            "State": "NY",
            "Country": "USA",
            "Latitude": 40.7128,
            "Longitude": -74.0060,
            "Budget_Category": "Groceries",
            "Income_Source": "None",
            "Expense_Tag": "Essential",
            "Recurring": "No",
            "Salary_Week": "No",
            "Holiday": "No",
            "Notes": "Ok"
        },
        # Duplicate ID check
        {
            "Transaction_ID": "TXN-001",
            "Customer_ID": "CUST-1001",
            "Date": "2023-01-02",
            "Time": "12:00:00",
            "Month": 1,
            "Quarter": 1,
            "Year": 2023,
            "Week_Number": 1,
            "Day": 2,
            "Day_of_Week": "Monday",
            "Weekend": "No",
            "Category": "Food",
            "Sub_Category": "Dining Out",
            "Description": "Lunch",
            "Merchant": "Chipotle",
            "Merchant_Category": "Food",
            "Transaction_Type": "Expense",
            "Amount": 15.00,
            "Currency": "INR",
            "Payment_Mode": "Credit Card",
            "Account_Type": "Credit Card",
            "City": "New York",
            "State": "NY",
            "Country": "USA",
            "Latitude": 40.7128,
            "Longitude": -74.0060,
            "Budget_Category": "Food & Dining",
            "Income_Source": "None",
            "Expense_Tag": "Discretionary",
            "Recurring": "No",
            "Salary_Week": "No",
            "Holiday": "No",
            "Notes": "Ok"
        },
        # Invalid amount <= 0
        {
            "Transaction_ID": "TXN-003",
            "Customer_ID": "CUST-1001",
            "Date": "2023-01-03",
            "Time": "12:00:00",
            "Month": 1,
            "Quarter": 1,
            "Year": 2023,
            "Week_Number": 1,
            "Day": 3,
            "Day_of_Week": "Tuesday",
            "Weekend": "No",
            "Category": "Groceries",
            "Sub_Category": "Supermarket Groceries",
            "Description": "Invalid amount",
            "Merchant": "Whole Foods",
            "Merchant_Category": "Groceries",
            "Transaction_Type": "Expense",
            "Amount": -50.00,
            "Currency": "INR",
            "Payment_Mode": "Credit Card",
            "Account_Type": "Credit Card",
            "City": "New York",
            "State": "NY",
            "Country": "USA",
            "Latitude": 40.7128,
            "Longitude": -74.0060,
            "Budget_Category": "Groceries",
            "Income_Source": "None",
            "Expense_Tag": "Essential",
            "Recurring": "No",
            "Salary_Week": "No",
            "Holiday": "No",
            "Notes": "Ok"
        },
        # Invalid Currency
        {
            "Transaction_ID": "TXN-004",
            "Customer_ID": "CUST-1001",
            "Date": "2023-01-04",
            "Time": "12:00:00",
            "Month": 1,
            "Quarter": 1,
            "Year": 2023,
            "Week_Number": 1,
            "Day": 4,
            "Day_of_Week": "Wednesday",
            "Weekend": "No",
            "Category": "Groceries",
            "Sub_Category": "Supermarket Groceries",
            "Description": "Invalid Currency",
            "Merchant": "Whole Foods",
            "Merchant_Category": "Groceries",
            "Transaction_Type": "Expense",
            "Amount": 50.00,
            "Currency": "EUR",
            "Payment_Mode": "Credit Card",
            "Account_Type": "Credit Card",
            "City": "New York",
            "State": "NY",
            "Country": "USA",
            "Latitude": 40.7128,
            "Longitude": -74.0060,
            "Budget_Category": "Groceries",
            "Income_Source": "None",
            "Expense_Tag": "Essential",
            "Recurring": "No",
            "Salary_Week": "No",
            "Holiday": "No",
            "Notes": "Ok"
        }
    ]
    return pd.DataFrame(data)

def test_duplicate_validation(mock_transaction_df):
    validator = DataValidator(mock_transaction_df)
    stats = validator.validate_all()
    assert stats["duplicate_transaction_ids"] == 1

def test_invalid_amount_validation(mock_transaction_df):
    validator = DataValidator(mock_transaction_df)
    stats = validator.validate_all()
    assert stats["invalid_amounts"] == 1

def test_invalid_currency_validation(mock_transaction_df):
    validator = DataValidator(mock_transaction_df)
    stats = validator.validate_all()
    assert stats["invalid_currency"] == 1

def test_quality_score_calculation(mock_transaction_df):
    validator = DataValidator(mock_transaction_df)
    stats = validator.validate_all()
    # Should be less than 100 due to errors
    assert stats["data_quality_score"] < 100.0

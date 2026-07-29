import os
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings
from utils.logging_utils import get_logger

logger = get_logger("data_generator")

def generate_raw_transactions(num_records=12500, seed=42):
    """
    Generates a realistic corporate-grade transactional dataset representing an end-user ledger.
    Includes time intelligence, geographical elements, and quality defects for validation testing.
    """
    logger.info(f"Starting data generation for {num_records} records...")
    random.seed(seed)
    np.random.seed(seed)
    
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2025, 12, 31)
    date_range_days = (end_date - start_date).days
    
    customers = ["CUST-1001", "CUST-1002", "CUST-1003"]
    transactions = []
    
    # 1. Generate core scheduled recurring entries per customer
    current_date = start_date
    while current_date <= end_date:
        year = current_date.year
        month = current_date.month
        day = current_date.day
        
        # Determine holiday flag based on major US holidays
        is_holiday = (month, day) in [
            (1, 1),   # New Year
            (7, 4),   # Independence Day
            (11, 24), (11, 25), # Thanksgiving range
            (12, 24), (12, 25), # Christmas range
            (12, 31)  # New Year's Eve
        ]
        holiday_str = "Yes" if is_holiday else "No"
        
        # Salary Week indicator (26th of month to 2nd of next month)
        is_salary_week = "Yes" if (day >= 26 or day <= 2) else "No"
        
        for cust in customers:
            # Salary payout (monthly on the 26th)
            if day == 26:
                salary_amount = 7500.00 if cust == "CUST-1001" else (5000.00 if cust == "CUST-1002" else 9000.00)
                transactions.append({
                    "Customer_ID": cust,
                    "Date": current_date.strftime("%Y-%m-%d"),
                    "Time": "09:00:00",
                    "Category": "Salary",
                    "Sub_Category": "Tech Corp Salary",
                    "Description": f"Salary Payout from Tech Corp for {cust}",
                    "Merchant": "Google Inc." if cust == "CUST-1001" else "Meta Platforms",
                    "Merchant_Category": "Employment",
                    "Transaction_Type": "Income",
                    "Amount": salary_amount,
                    "Currency": "USD",
                    "Payment_Mode": "Net Banking",
                    "Account_Type": "Savings Account",
                    "City": "San Francisco",
                    "State": "CA",
                    "Country": "USA",
                    "Budget_Category": "Income",
                    "Income_Source": "Primary Job",
                    "Expense_Tag": "None",
                    "Recurring": "Yes",
                    "Salary_Week": "Yes",
                    "Holiday": holiday_str,
                    "Notes": "Auto-credited monthly payroll"
                })
                
            # Rent payment (monthly on the 1st)
            if day == 1:
                rent_amount = 2200.00 if cust == "CUST-1001" else (1800.00 if cust == "CUST-1002" else 2600.00)
                transactions.append({
                    "Customer_ID": cust,
                    "Date": current_date.strftime("%Y-%m-%d"),
                    "Time": "00:05:00",
                    "Category": "Rent",
                    "Sub_Category": "Apartment Rent",
                    "Description": f"Rent Payment for apartment leasing - {cust}",
                    "Merchant": "Metropolitan Leasing",
                    "Merchant_Category": "Real Estate",
                    "Transaction_Type": "Expense",
                    "Amount": rent_amount,
                    "Currency": "USD",
                    "Payment_Mode": "Net Banking",
                    "Account_Type": "Current Account",
                    "City": "San Francisco" if cust == "CUST-1001" else ("New York" if cust == "CUST-1002" else "Seattle"),
                    "State": "CA" if cust == "CUST-1001" else ("NY" if cust == "CUST-1002" else "WA"),
                    "Country": "USA",
                    "Budget_Category": "Housing",
                    "Income_Source": "None",
                    "Expense_Tag": "Fixed",
                    "Recurring": "Yes",
                    "Salary_Week": "Yes",
                    "Holiday": holiday_str,
                    "Notes": "Auto-debit residential rent"
                })
                
            # SIP investment on the 28th
            if day == 28:
                transactions.append({
                    "Customer_ID": cust,
                    "Date": current_date.strftime("%Y-%m-%d"),
                    "Time": "10:30:00",
                    "Category": "Investment",
                    "Sub_Category": "Mutual Fund SIP",
                    "Description": f"Mutual Fund Systemic Investment Plan - {cust}",
                    "Merchant": "Vanguard Funds",
                    "Merchant_Category": "Financial Services",
                    "Transaction_Type": "Expense",
                    "Amount": 1000.00 if cust == "CUST-1002" else 1500.00,
                    "Currency": "USD",
                    "Payment_Mode": "Net Banking",
                    "Account_Type": "Savings Account",
                    "City": "New York",
                    "State": "NY",
                    "Country": "USA",
                    "Budget_Category": "Investments & Savings",
                    "Income_Source": "None",
                    "Expense_Tag": "Savings",
                    "Recurring": "Yes",
                    "Salary_Week": "Yes",
                    "Holiday": holiday_str,
                    "Notes": "Monthly mutual fund SIP accumulation"
                })

        current_date += timedelta(days=1)
        
    # 2. Daily random transactions to complete target records
    remaining_records = num_records - len(transactions)
    logger.info(f"Generating {remaining_records} random daily transactions...")
    
    random_dates = [start_date + timedelta(days=random.randint(0, date_range_days)) for _ in range(remaining_records)]
    random_dates.sort()
    
    for dt in random_dates:
        cust = random.choice(customers)
        day = dt.day
        month = dt.month
        is_weekend = dt.weekday() in [5, 6]
        
        is_holiday = (month, day) in [
            (1, 1), (7, 4), (11, 24), (11, 25), (12, 24), (12, 25), (12, 31)
        ]
        holiday_str = "Yes" if is_holiday else "No"
        is_salary_week = "Yes" if (day >= 26 or day <= 2) else "No"
        
        # Pick category
        rand_val = random.random()
        if rand_val < 0.06:
            # Freelancing Income
            category = "Freelancing"
            sub_category = random.choice(settings.INCOME_CATEGORIES[category])
            amount = round(random.uniform(200, 2000), 2)
            trans_type = "Income"
            payment_mode = random.choice(["Net Banking", "UPI"])
            merchant = random.choice(settings.MERCHANTS[category])
            city = random.choice(list(settings.GEOGRAPHY.keys()))
            desc = f"Freelance project work - {sub_category}"
            income_source = "Freelance"
            expense_tag = "None"
            notes = "Freelance invoice payout"
        elif rand_val < 0.08:
            # Dividends or refunds
            category = random.choice(["Investment", "Refund", "Interest"])
            sub_category = random.choice(settings.INCOME_CATEGORIES[category])
            amount = round(random.uniform(10, 400), 2)
            trans_type = "Income"
            payment_mode = "Net Banking" if category != "Refund" else "Credit Card"
            merchant = random.choice(settings.MERCHANTS[category])
            city = "New York"
            desc = f"{category} statement credit"
            income_source = category
            expense_tag = "None"
            notes = "Statement payout"
        else:
            # Regular expenses
            trans_type = "Expense"
            income_source = "None"
            
            choices = ["Food", "Groceries", "Shopping", "Fuel", "Transport", "Entertainment", "Travel", "Healthcare", "Education", "Miscellaneous"]
            weights = [0.35, 0.25, 0.15, 0.08, 0.08, 0.05, 0.01, 0.01, 0.01, 0.01]
            if is_weekend:
                weights = [0.40, 0.15, 0.22, 0.05, 0.05, 0.08, 0.02, 0.01, 0.01, 0.01]
                
            category = random.choices(choices, weights=weights)[0]
            sub_category = random.choice(settings.EXPENSE_CATEGORIES[category])
            
            if category == "Food":
                amount = round(random.uniform(5, 15), 2) if "Coffee" in sub_category else round(random.uniform(15, 120), 2)
                payment_mode = random.choice(["Credit Card", "UPI", "Debit Card", "Cash"])
                expense_tag = "Discretionary"
            elif category == "Groceries":
                amount = round(random.uniform(15, 250), 2)
                payment_mode = random.choice(["Credit Card", "Debit Card", "UPI"])
                expense_tag = "Essential"
            elif category == "Shopping":
                amount = round(random.uniform(10, 500), 2)
                payment_mode = random.choice(["Credit Card", "UPI", "Debit Card"])
                expense_tag = "Discretionary"
            elif category == "Fuel":
                amount = round(random.uniform(30, 80), 2)
                payment_mode = random.choice(["Credit Card", "Debit Card"])
                expense_tag = "Essential"
            elif category == "Transport":
                amount = round(random.uniform(5, 50), 2)
                payment_mode = random.choice(["Credit Card", "UPI", "Debit Card"])
                expense_tag = "Essential"
            elif category == "Entertainment":
                amount = round(random.uniform(10, 100), 2)
                payment_mode = random.choice(["Credit Card", "UPI"])
                expense_tag = "Discretionary"
            elif category == "Travel":
                amount = round(random.uniform(100, 1200), 2)
                payment_mode = random.choice(["Credit Card", "Net Banking"])
                expense_tag = "Discretionary"
            else:
                amount = round(random.uniform(10, 200), 2)
                payment_mode = random.choice(["Credit Card", "Debit Card", "UPI", "Cash"])
                expense_tag = "Discretionary"
                
            merchant = random.choice(settings.MERCHANTS[category])
            city = random.choice(list(settings.GEOGRAPHY.keys()))
            desc = f"Purchase at {merchant} - {sub_category}"
            notes = "Leisure POS swipe" if is_weekend else "Routine purchase"

        # Map geographical details from city settings
        geo_info = settings.GEOGRAPHY[city]
        state = geo_info["state"]
        country = geo_info["country"]
        
        # Payment card mapping
        if trans_type == "Income":
            account_type = "Savings Account"
        else:
            account_type = "Credit Card" if payment_mode == "Credit Card" else random.choice(["Savings Account", "Current Account"])
            
        # Determine budget mappings
        budget_mapping = {
            "Rent": "Housing", "Food": "Food & Dining", "Groceries": "Groceries",
            "Fuel": "Transportation", "Transport": "Transportation", "Shopping": "Shopping",
            "Healthcare": "Healthcare", "Insurance": "Insurance & Taxes", "Electricity": "Utilities",
            "Water Bill": "Utilities", "Internet": "Utilities", "Entertainment": "Entertainment",
            "Travel": "Travel", "Education": "Education & Self-Care", "Subscriptions": "Entertainment",
            "EMI": "Debt Service", "Investment": "Investments & Savings", "Taxes": "Insurance & Taxes",
            "Miscellaneous": "Miscellaneous", "Salary": "Income", "Freelancing": "Income",
            "Investment (Income)": "Income", "Interest": "Income", "Bonus": "Income",
            "Rental Income": "Income", "Refund": "Income", "Gift": "Income"
        }
        budget_cat = budget_mapping.get(category, "Miscellaneous")
        
        # Time string
        t_hour = random.randint(7, 22)
        t_min = random.randint(0, 59)
        t_sec = random.randint(0, 59)
        time_str = f"{t_hour:02d}:{t_min:02d}:{t_sec:02d}"
        
        transactions.append({
            "Customer_ID": cust,
            "Date": dt.strftime("%Y-%m-%d"),
            "Time": time_str,
            "Category": category,
            "Sub_Category": sub_category,
            "Description": desc,
            "Merchant": merchant,
            "Merchant_Category": category,
            "Transaction_Type": trans_type,
            "Amount": amount,
            "Currency": "USD",
            "Payment_Mode": payment_mode,
            "Account_Type": account_type,
            "City": city,
            "State": state,
            "Country": country,
            "Budget_Category": budget_cat,
            "Income_Source": income_source,
            "Expense_Tag": expense_tag,
            "Recurring": "No",
            "Salary_Week": is_salary_week,
            "Holiday": holiday_str,
            "Notes": notes
        })

    # 3. Add spelling inconsistencies to categories for data cleaning tests (approx 1.5% contamination)
    for tx in transactions:
        if random.random() < 0.015:
            if tx["Category"] == "Groceries":
                tx["Category"] = "Grocries"
            elif tx["Category"] == "Food":
                tx["Category"] = "Foodd"
            elif tx["Category"] == "Entertainment":
                tx["Category"] = "Entertainement"
            elif tx["Category"] == "Subscriptions":
                tx["Category"] = "Subs"
                
        # Randomly set descriptions to null (1.0% contamination)
        if random.random() < 0.01:
            tx["Description"] = np.nan
            
    # 4. Insert negative amounts to validate failure flagging
    for _ in range(5):
        corrupt_txn = random.choice(transactions)
        corrupt_txn["Amount"] = -abs(corrupt_txn["Amount"])

    # Convert to DataFrame
    df = pd.DataFrame(transactions)
    
    # Coordinates mapping
    def set_coords(row):
        city = row["City"]
        coords = settings.GEOGRAPHY[city]
        lat = round(coords["lat"][0] + np.random.normal(0, coords["lat"][1]), 6)
        lon = round(coords["lon"][0] + np.random.normal(0, coords["lon"][1]), 6)
        return pd.Series([lat, lon])
        
    df[["Latitude", "Longitude"]] = df.apply(set_coords, axis=1)
    
    # Shuffle and generate unique Transaction IDs
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)
    df.insert(0, "Transaction_ID", [f"TXN-{100000 + i}" for i in range(len(df))])
    
    # Sort date components
    df["Date"] = pd.to_datetime(df["Date"])
    df["Month"] = df["Date"].dt.month
    df["Quarter"] = df["Date"].dt.quarter
    df["Year"] = df["Date"].dt.year
    df["Week_Number"] = df["Date"].dt.isocalendar().week
    df["Day"] = df["Date"].dt.day
    df["Day_of_Week"] = df["Date"].dt.day_name()
    df["Weekend"] = df["Date"].dt.weekday.isin([5, 6]).map({True: "Yes", False: "No"})
    
    # Format dates back to string for raw representation
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
    
    # Re-order columns to spec
    columns_order = [
        "Transaction_ID", "Customer_ID", "Date", "Time", "Month", "Quarter", "Year",
        "Week_Number", "Day", "Day_of_Week", "Weekend", "Category", "Sub_Category",
        "Description", "Merchant", "Merchant_Category", "Transaction_Type", "Amount",
        "Currency", "Payment_Mode", "Account_Type", "City", "State", "Country",
        "Latitude", "Longitude", "Budget_Category", "Income_Source", "Expense_Tag",
        "Recurring", "Salary_Week", "Holiday", "Notes"
    ]
    df = df[columns_order]
    
    df.to_csv(settings.RAW_DATA_PATH, index=False)
    logger.info(f"Successfully generated raw transactions CSV at {settings.RAW_DATA_PATH} with {len(df)} rows.")
    return df

if __name__ == "__main__":
    generate_raw_transactions()

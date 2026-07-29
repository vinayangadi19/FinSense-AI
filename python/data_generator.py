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

def get_festival_season(date_val):
    """
    Checks if a given date falls within major Indian festival periods.
    """
    month = date_val.month
    day = date_val.day
    
    # 1. Ugadi (typically late March or April)
    if (month == 3 and day >= 25) or (month == 4 and day <= 5):
        return "Ugadi"
    # 2. Ganesh Chaturthi (typically late August or September)
    if (month == 8 and day >= 25) or (month == 9 and day <= 10):
        return "Ganesh Chaturthi"
    # 3. Diwali (typically late October or November)
    if (month == 10 and day >= 25) or (month == 11 and day <= 15):
        return "Diwali"
    # 4. Christmas / Year End
    if month == 12 and day >= 24:
        return "Christmas & New Year"
    if month == 1 and day <= 2:
        return "New Year"
        
    return None

def generate_raw_transactions(num_records=12500, seed=42):
    """
    Generates a realistic corporate-grade transactional dataset representing an Indian end-user ledger.
    Includes time intelligence, geographical elements, and quality defects for validation testing.
    """
    logger.info(f"Starting Indianized data generation for {num_records} records...")
    random.seed(seed)
    np.random.seed(seed)
    
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2025, 12, 31)
    date_range_days = (end_date - start_date).days
    
    customers = list(settings.CUSTOMER_PROFILES.keys())
    transactions = []
    
    # 1. Generate core scheduled recurring entries per customer
    current_date = start_date
    while current_date <= end_date:
        year = current_date.year
        month = current_date.month
        day = current_date.day
        
        # Determine holiday flag based on major Indian national holidays and festivals
        is_national_holiday = (month, day) in [
            (1, 26),   # Republic Day
            (8, 15),   # Independence Day
            (10, 2),   # Gandhi Jayanti
        ]
        festival = get_festival_season(current_date)
        is_holiday = is_national_holiday or (festival is not None)
        holiday_str = "Yes" if is_holiday else "No"
        
        # Salary Week indicator (26th of month to 2nd of next month)
        is_salary_week = "Yes" if (day >= 26 or day <= 2) else "No"
        
        for cust in customers:
            # Salary payout (monthly on the 26th)
            if day == 26:
                salary_amount = settings.CUSTOMER_PROFILES[cust]["monthly_income"]
                sal_cat = settings.CUSTOMER_PROFILES[cust]["salary_category"]
                sal_subcat = settings.CUSTOMER_PROFILES[cust]["salary_sub_category"]
                sal_merchant = settings.CUSTOMER_PROFILES[cust]["salary_merchant"]
                city = settings.CUSTOMER_PROFILES[cust]["city"]
                state = settings.GEOGRAPHY[city]["state"]
                transactions.append({
                    "Customer_ID": cust,
                    "Date": current_date.strftime("%Y-%m-%d"),
                    "Time": "09:00:00",
                    "Category": sal_cat,
                    "Sub_Category": sal_subcat,
                    "Description": f"Monthly Salary Credit - {cust}",
                    "Merchant": sal_merchant,
                    "Merchant_Category": "Employment",
                    "Transaction_Type": "Income",
                    "Amount": salary_amount,
                    "Currency": "INR",
                    "Payment_Mode": "Net Banking",
                    "Account_Type": "Savings Account",
                    "City": city,
                    "State": state,
                    "Country": "India",
                    "Budget_Category": "Income",
                    "Income_Source": "Primary Job",
                    "Expense_Tag": "None",
                    "Recurring": "Yes",
                    "Salary_Week": "Yes",
                    "Holiday": holiday_str,
                    "Notes": "Auto-credited monthly salary payroll"
                })
                
            # Rent payment (monthly on the 1st)
            if day == 1:
                rent_amount = settings.CUSTOMER_PROFILES[cust]["rent_amount"]
                city = settings.CUSTOMER_PROFILES[cust]["city"]
                state = settings.GEOGRAPHY[city]["state"]
                transactions.append({
                    "Customer_ID": cust,
                    "Date": current_date.strftime("%Y-%m-%d"),
                    "Time": "00:05:00",
                    "Category": "Rent",
                    "Sub_Category": "Apartment Rent",
                    "Description": f"Rent Payment for Apartment - {cust}",
                    "Merchant": "Local Landlord Deposit",
                    "Merchant_Category": "Real Estate",
                    "Transaction_Type": "Expense",
                    "Amount": rent_amount,
                    "Currency": "INR",
                    "Payment_Mode": "Net Banking",
                    "Account_Type": "Savings Account",
                    "City": city,
                    "State": state,
                    "Country": "India",
                    "Budget_Category": "Housing",
                    "Income_Source": "None",
                    "Expense_Tag": "Fixed",
                    "Recurring": "Yes",
                    "Salary_Week": "Yes",
                    "Holiday": holiday_str,
                    "Notes": "Auto-debit monthly house rent"
                })
                
            # SIP investment on the 28th
            if day == 28:
                sip_amount = settings.CUSTOMER_PROFILES[cust]["sip_amount"]
                city = settings.CUSTOMER_PROFILES[cust]["city"]
                state = settings.GEOGRAPHY[city]["state"]
                transactions.append({
                    "Customer_ID": cust,
                    "Date": current_date.strftime("%Y-%m-%d"),
                    "Time": "10:30:00",
                    "Category": "Mutual Fund SIP",
                    "Sub_Category": "HDFC Index Fund SIP",
                    "Description": f"Mutual Fund Systemic Investment Plan - {cust}",
                    "Merchant": "Groww Direct Mutual Fund",
                    "Merchant_Category": "Financial Services",
                    "Transaction_Type": "Expense",
                    "Amount": sip_amount,
                    "Currency": "INR",
                    "Payment_Mode": "Net Banking",
                    "Account_Type": "Savings Account",
                    "City": city,
                    "State": state,
                    "Country": "India",
                    "Budget_Category": "Investments & Savings",
                    "Income_Source": "None",
                    "Expense_Tag": "Savings",
                    "Recurring": "Yes",
                    "Salary_Week": "Yes",
                    "Holiday": holiday_str,
                    "Notes": "Monthly mutual fund SIP accumulation"
                })
                
            # Bills on the 5th (Electricity, Broadband, Mobile Recharge)
            if day == 5:
                income_val = settings.CUSTOMER_PROFILES[cust]["monthly_income"]
                scale = income_val / 150000.0
                city = settings.CUSTOMER_PROFILES[cust]["city"]
                state = settings.GEOGRAPHY[city]["state"]
                
                # Electricity Bill
                elec_amount = float(random.randint(1200, 4000)) * scale
                transactions.append({
                    "Customer_ID": cust,
                    "Date": current_date.strftime("%Y-%m-%d"),
                    "Time": "11:00:00",
                    "Category": "Electricity",
                    "Sub_Category": "Monthly Electricity Bill",
                    "Description": f"Electricity Bill Payment - {cust}",
                    "Merchant": random.choice(["TATA Power Bill", "BESCOM Bill", "MSEDCL Bill"]),
                    "Merchant_Category": "Utilities",
                    "Transaction_Type": "Expense",
                    "Amount": round(elec_amount, 2),
                    "Currency": "INR",
                    "Payment_Mode": "UPI",
                    "Account_Type": "Savings Account",
                    "City": city,
                    "State": state,
                    "Country": "India",
                    "Budget_Category": "Utilities",
                    "Income_Source": "None",
                    "Expense_Tag": "Essential",
                    "Recurring": "Yes",
                    "Salary_Week": "No",
                    "Holiday": holiday_str,
                    "Notes": "Monthly power bill"
                })
                
                # Broadband internet bill
                bb_amount = float(random.randint(599, 1299)) * scale
                transactions.append({
                    "Customer_ID": cust,
                    "Date": current_date.strftime("%Y-%m-%d"),
                    "Time": "11:30:00",
                    "Category": "Broadband",
                    "Sub_Category": "Airtel Fiber Broadband",
                    "Description": f"Broadband Subscription Payment - {cust}",
                    "Merchant": random.choice(["Airtel Xtream Fiber", "JioFiber Broadband", "ACT Fibernet Subscription"]),
                    "Merchant_Category": "Utilities",
                    "Transaction_Type": "Expense",
                    "Amount": round(bb_amount, 2),
                    "Currency": "INR",
                    "Payment_Mode": "UPI",
                    "Account_Type": "Savings Account",
                    "City": city,
                    "State": state,
                    "Country": "India",
                    "Budget_Category": "Utilities",
                    "Income_Source": "None",
                    "Expense_Tag": "Essential",
                    "Recurring": "Yes",
                    "Salary_Week": "No",
                    "Holiday": holiday_str,
                    "Notes": "Monthly internet bill"
                })
                
            # EMI on the 10th
            if day == 10:
                emi_map = {"CUST-1001": 0.0, "CUST-1002": 20000.0, "CUST-1003": 65000.0, "CUST-1004": 120000.0, "CUST-1005": 5000.0}
                emi_amount = emi_map.get(cust, 0.0)
                if emi_amount > 0:
                    city = settings.CUSTOMER_PROFILES[cust]["city"]
                    state = settings.GEOGRAPHY[city]["state"]
                    transactions.append({
                        "Customer_ID": cust,
                        "Date": current_date.strftime("%Y-%m-%d"),
                        "Time": "08:00:00",
                        "Category": "EMI",
                        "Sub_Category": "Home Loan EMI" if cust in ["CUST-1003", "CUST-1004"] else "Car Loan EMI",
                        "Description": f"Loan EMI Installment - {cust}",
                        "Merchant": random.choice(["HDFC Housing Loan EMI", "ICICI Car Loan EMI"]),
                        "Merchant_Category": "Financial Services",
                        "Transaction_Type": "Expense",
                        "Amount": emi_amount,
                        "Currency": "INR",
                        "Payment_Mode": "Net Banking",
                        "Account_Type": "Savings Account",
                        "City": city,
                        "State": state,
                        "Country": "India",
                        "Budget_Category": "Debt Service",
                        "Income_Source": "None",
                        "Expense_Tag": "Fixed",
                        "Recurring": "Yes",
                        "Salary_Week": "No",
                        "Holiday": holiday_str,
                        "Notes": "Monthly Loan Installment Auto-debit"
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
        
        is_national_holiday = (month, day) in [(1, 26), (8, 15), (10, 2)]
        festival = get_festival_season(dt)
        is_holiday = is_national_holiday or (festival is not None)
        holiday_str = "Yes" if is_holiday else "No"
        is_salary_week = "Yes" if (day >= 26 or day <= 2) else "No"
        
        income_val = settings.CUSTOMER_PROFILES[cust]["monthly_income"]
        scale = income_val / 150000.0
        expense_scale = scale * 0.70  # Scale down random expenses to ensure positive cash flow
        
        # Pick category
        rand_val = random.random()
        if rand_val < 0.05:
            # Freelancing Income
            category = "Freelancing"
            sub_category = random.choice(settings.INCOME_CATEGORIES[category])
            amount = round(random.uniform(5000, 35000), 2) * scale
            trans_type = "Income"
            payment_mode = random.choice(["Net Banking", "UPI"])
            merchant = random.choice(settings.MERCHANTS[category])
            city = settings.CUSTOMER_PROFILES[cust]["city"]
            desc = f"Freelance project work - {sub_category}"
            income_source = "Freelance"
            expense_tag = "None"
            notes = "Freelance invoice payment"
        elif rand_val < 0.07:
            # Dividends or refunds
            category = random.choice(["Investment", "Refund", "Interest"])
            sub_category = random.choice(settings.INCOME_CATEGORIES[category])
            amount = round(random.uniform(500, 8000), 2) * scale
            trans_type = "Income"
            payment_mode = "Net Banking" if category != "Refund" else "Credit Card"
            merchant = random.choice(settings.MERCHANTS[category])
            city = settings.CUSTOMER_PROFILES[cust]["city"]
            desc = f"{category} statement credit"
            income_source = category
            expense_tag = "None"
            notes = "Statement payout"
        else:
            # Regular expenses
            trans_type = "Expense"
            income_source = "None"
            
            # Categories choices
            choices = ["Food", "Groceries", "Vegetables", "Milk", "Fuel", "Broadband", "Mobile Recharge", "UPI Payments", "Medical", "Travel", "Dining", "Shopping", "Entertainment", "Gold", "Investments", "Miscellaneous"]
            weights = [0.12, 0.12, 0.08, 0.08, 0.08, 0.02, 0.02, 0.08, 0.06, 0.08, 0.08, 0.10, 0.06, 0.03, 0.04, 0.03]
            
            # Boost shopping & travel during festivals
            if festival:
                weights = list(weights)
                weights[11] = 0.25 # boost shopping
                weights[9] = 0.18 # boost travel
                total_w = sum(weights)
                weights = [w / total_w for w in weights]
            elif is_weekend:
                # Boost dining and entertainment on weekends
                weights = list(weights)
                weights[10] = 0.18 # boost dining
                weights[12] = 0.12 # boost entertainment
                total_w = sum(weights)
                weights = [w / total_w for w in weights]
                
            category = random.choices(choices, weights=weights)[0]
            sub_category = random.choice(settings.EXPENSE_CATEGORIES[category])
            
            # Set realistic amounts in INR
            if category in ["Food", "Dining"]:
                amount = round(random.uniform(50, 400), 2) if "Coffee" in sub_category else round(random.uniform(200, 2000), 2)
                amount *= expense_scale
                payment_mode = random.choice(["Credit Card", "UPI", "Debit Card", "Cash"])
                expense_tag = "Discretionary"
            elif category == "Groceries":
                amount = round(random.uniform(300, 3000), 2) * expense_scale
                payment_mode = random.choice(["Credit Card", "Debit Card", "UPI"])
                expense_tag = "Essential"
            elif category in ["Vegetables", "Milk"]:
                amount = round(random.uniform(50, 500), 2) * expense_scale
                payment_mode = random.choice(["UPI", "Cash"])
                expense_tag = "Essential"
            elif category == "Shopping":
                amount = round(random.uniform(500, 8000), 2) * expense_scale
                payment_mode = random.choice(["Credit Card", "UPI", "Debit Card"])
                expense_tag = "Discretionary"
                if festival:
                    amount *= random.uniform(1.5, 2.5) # festival shopping boost
            elif category == "Fuel":
                amount = round(random.uniform(500, 3000), 2) * expense_scale
                payment_mode = random.choice(["Credit Card", "Debit Card", "UPI"])
                expense_tag = "Essential"
            elif category == "Travel":
                amount = round(random.uniform(1000, 15000), 2) * expense_scale
                payment_mode = random.choice(["Credit Card", "Net Banking", "UPI"])
                expense_tag = "Discretionary"
                if festival:
                    amount *= random.uniform(1.3, 2.0) # festival travel boost
            elif category == "Entertainment":
                amount = round(random.uniform(100, 2500), 2) * expense_scale
                payment_mode = random.choice(["Credit Card", "UPI"])
                expense_tag = "Discretionary"
            elif category in ["Gold", "Investments"]:
                amount = round(random.uniform(3000, 20000), 2) * expense_scale
                payment_mode = random.choice(["Net Banking", "UPI"])
                expense_tag = "Savings"
            elif category == "Medical":
                amount = round(random.uniform(100, 5000), 2) * expense_scale
                payment_mode = random.choice(["Credit Card", "Debit Card", "UPI"])
                expense_tag = "Essential"
            else:
                amount = round(random.uniform(100, 2000), 2) * expense_scale
                payment_mode = random.choice(["Credit Card", "Debit Card", "UPI", "Cash"])
                expense_tag = "Discretionary"
                
            merchant = random.choice(settings.MERCHANTS[category])
            city = settings.CUSTOMER_PROFILES[cust]["city"]
            desc = f"Purchase at {merchant} - {sub_category}"
            notes = "Leisure POS swipe" if is_weekend else ("Festival purchase" if festival else "Routine purchase")
            if festival:
                notes = f"{festival} festival spend"
                
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
        budget_cat = settings.BUDGET_MAPPING.get(category, "Miscellaneous")
        
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
            "Amount": round(amount, 2),
            "Currency": "INR",
            "Payment_Mode": payment_mode,
            "Account_Type": account_type,
            "City": city,
            "State": state,
            "Country": country,
            "Budget_Category": budget_cat,
            "Income_Source": income_source,
            "Expense_Tag": expense_tag,
            "Recurring": "Yes" if category in ["Rent", "EMI", "Mutual Fund SIP"] else "No",
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

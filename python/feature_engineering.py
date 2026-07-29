import os
import pandas as pd
import numpy as np
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings
from utils.logging_utils import get_logger

logger = get_logger("feature_engineering")

def engineer_all_features() -> pd.DataFrame:
    """
    Advanced Feature Engineering Pipeline.
    Computes time series, customer cash flows, rolling indicators, and financial health ratios.
    Calculates features on a per-customer basis.
    """
    logger.info("Executing advanced feature engineering pipeline...")
    
    if not os.path.exists(settings.PROCESSED_DATA_PATH):
        raise FileNotFoundError(f"Processed CSV not found at {settings.PROCESSED_DATA_PATH}. Run processor first.")
        
    df = pd.read_csv(settings.PROCESSED_DATA_PATH)
    df["Date"] = pd.to_datetime(df["Date"])
    
    # 1. Sort values sequentially per customer to calculate running totals
    df = df.sort_values(by=["Customer_ID", "Date", "Time", "Transaction_ID"]).reset_index(drop=True)
    
    # Create helper columns
    df["Income_Amt"] = np.where(df["Transaction_Type"] == "Income", df["Amount"], 0.0)
    df["Expense_Amt"] = np.where(df["Transaction_Type"] == "Expense", df["Amount"], 0.0)
    
    # 2. Cumulative Income/Expenses and Running Balance per Customer
    logger.info("Computing running balances and cumulative totals per customer...")
    df["Cumulative_Income"] = df.groupby("Customer_ID")["Income_Amt"].cumsum().round(2)
    df["Cumulative_Expenses"] = df.groupby("Customer_ID")["Expense_Amt"].cumsum().round(2)
    
    # Define starting balances in INR representing realistic savings for each persona
    initial_balances = {
        "CUST-1001": 80000.0,     # Rohan Mehta (Student)
        "CUST-1002": 500000.0,    # Ananya Iyer (Software Engineer)
        "CUST-1003": 1200000.0,   # Dr. Vikram Adiga (Doctor)
        "CUST-1004": 6500000.0,   # Rajesh Bansal (Business Owner)
        "CUST-1005": 3000000.0    # Devendra Shastri (Retired Government Employee)
    }
    df["Starting_Balance"] = df["Customer_ID"].map(initial_balances).fillna(0.0)
    df["Running_Balance"] = (df["Starting_Balance"] + df["Cumulative_Income"] - df["Cumulative_Expenses"]).round(2)
    
    # 3. Monthly aggregations per Customer
    logger.info("Computing monthly income and expense metrics...")
    monthly_agg = df.groupby(["Customer_ID", "Year", "Month"]).agg(
        Monthly_Income=("Income_Amt", "sum"),
        Monthly_Expense=("Expense_Amt", "sum")
    ).reset_index()
    
    # Add net savings and ratios
    monthly_agg["Net_Savings"] = (monthly_agg["Monthly_Income"] - monthly_agg["Monthly_Expense"]).round(2)
    monthly_agg["Savings_Rate"] = np.where(
        monthly_agg["Monthly_Income"] > 0,
        ((monthly_agg["Net_Savings"] / monthly_agg["Monthly_Income"]) * 100).round(2),
        0.0
    )
    monthly_agg["Expense_Ratio"] = np.where(
        monthly_agg["Monthly_Income"] > 0,
        ((monthly_agg["Monthly_Expense"] / monthly_agg["Monthly_Income"]) * 100).round(2),
        0.0
    )
    monthly_agg["Cash_Flow"] = monthly_agg["Net_Savings"]
    
    # Month over Month growth rates
    monthly_agg = monthly_agg.sort_values(by=["Customer_ID", "Year", "Month"]).reset_index(drop=True)
    monthly_agg["Prev_Income"] = monthly_agg.groupby("Customer_ID")["Monthly_Income"].shift(1)
    monthly_agg["Prev_Expense"] = monthly_agg.groupby("Customer_ID")["Monthly_Expense"].shift(1)
    monthly_agg["Prev_Net_Savings"] = monthly_agg.groupby("Customer_ID")["Net_Savings"].shift(1).fillna(0.0)
    
    monthly_agg["Income_Growth"] = np.where(
        monthly_agg["Prev_Income"] > 0,
        (((monthly_agg["Monthly_Income"] - monthly_agg["Prev_Income"]) / monthly_agg["Prev_Income"]) * 100).round(2),
        0.0
    )
    monthly_agg["Expense_Growth"] = np.where(
        monthly_agg["Prev_Expense"] > 0,
        (((monthly_agg["Monthly_Expense"] - monthly_agg["Prev_Expense"]) / monthly_agg["Prev_Expense"]) * 100).round(2),
        0.0
    )
    monthly_agg["Cashflow_Trend"] = (monthly_agg["Net_Savings"] - monthly_agg["Prev_Net_Savings"]).round(2)
    
    # Burn Rate (3-month rolling expense average)
    monthly_agg["Burn_Rate"] = monthly_agg.groupby("Customer_ID")["Monthly_Expense"].transform(
        lambda x: x.rolling(window=3, min_periods=1).mean().round(2)
    )
    
    # 3b. Advanced Ratio Features at Monthly Level
    logger.info("Computing advanced ratio metrics...")
    
    # Monthly EMI / Debt Service
    monthly_debt = df[df["Budget_Category"] == "Debt Service"].groupby(["Customer_ID", "Year", "Month"])["Amount"].sum().reset_index().rename(columns={"Amount": "Monthly_EMI"})
    monthly_agg = monthly_agg.merge(monthly_debt, on=["Customer_ID", "Year", "Month"], how="left").fillna({"Monthly_EMI": 0.0})
    monthly_agg["Debt_to_Income_Ratio"] = np.where(
        monthly_agg["Monthly_Income"] > 0,
        (monthly_agg["Monthly_EMI"] / monthly_agg["Monthly_Income"]).round(4),
        0.0
    )
    
    # Monthly Investments
    monthly_inv = df[df["Budget_Category"] == "Investments & Savings"].groupby(["Customer_ID", "Year", "Month"])["Amount"].sum().reset_index().rename(columns={"Amount": "Monthly_Investment"})
    monthly_agg = monthly_agg.merge(monthly_inv, on=["Customer_ID", "Year", "Month"], how="left").fillna({"Monthly_Investment": 0.0})
    monthly_agg["Investment_Ratio"] = np.where(
        monthly_agg["Monthly_Income"] > 0,
        (monthly_agg["Monthly_Investment"] / monthly_agg["Monthly_Income"]).round(4),
        0.0
    )
    
    # UPI transaction ratio
    upi_stats = df.groupby(["Customer_ID", "Year", "Month"]).agg(
        UPI_Count=("Payment_Mode", lambda x: (x == "UPI").sum()),
        Total_Txns=("Payment_Mode", "count")
    ).reset_index()
    upi_stats["UPI_Transaction_Ratio"] = np.where(
        upi_stats["Total_Txns"] > 0,
        (upi_stats["UPI_Count"] / upi_stats["Total_Txns"]).round(4),
        0.0
    )
    monthly_agg = monthly_agg.merge(upi_stats[["Customer_ID", "Year", "Month", "UPI_Transaction_Ratio"]], on=["Customer_ID", "Year", "Month"], how="left")
    
    # Lifestyle Score (Discretionary spending / Monthly expense)
    # Discretionary categories: Food & Dining, Shopping, Travel, Entertainment
    discret_spend = df[df["Budget_Category"].isin(["Food & Dining", "Shopping", "Travel", "Entertainment"])].groupby(["Customer_ID", "Year", "Month"])["Amount"].sum().reset_index().rename(columns={"Amount": "Discretionary_Spend"})
    monthly_agg = monthly_agg.merge(discret_spend, on=["Customer_ID", "Year", "Month"], how="left").fillna({"Discretionary_Spend": 0.0})
    monthly_agg["Lifestyle_Score"] = np.where(
        monthly_agg["Monthly_Expense"] > 0,
        ((monthly_agg["Discretionary_Spend"] / monthly_agg["Monthly_Expense"]) * 100).round(2),
        0.0
    )
    
    # Drop intermediate monthly cols
    monthly_agg_clean = monthly_agg.drop(columns=["Prev_Income", "Prev_Expense", "Prev_Net_Savings", "Monthly_EMI", "Monthly_Investment", "Discretionary_Spend"])
    
    # Merge monthly aggregates back
    df = df.merge(monthly_agg_clean, on=["Customer_ID", "Year", "Month"], how="left")
    
    # 4. Quarterly Savings per Customer
    logger.info("Computing quarterly savings...")
    quarter_agg = df.groupby(["Customer_ID", "Year", "Quarter"]).agg(
        Q_Income=("Income_Amt", "sum"),
        Q_Expense=("Expense_Amt", "sum")
    ).reset_index()
    quarter_agg["Quarterly_Savings"] = (quarter_agg["Q_Income"] - quarter_agg["Q_Expense"]).round(2)
    
    df = df.merge(quarter_agg[["Customer_ID", "Year", "Quarter", "Quarterly_Savings"]], on=["Customer_ID", "Year", "Quarter"], how="left")
    
    # 5. Category Budget Utilization
    logger.info("Computing category budget utilization rates...")
    cat_monthly_spend = df[df["Transaction_Type"] == "Expense"].groupby(
        ["Customer_ID", "Year", "Month", "Budget_Category"]
    )["Amount"].sum().reset_index().rename(columns={"Amount": "Cat_Monthly_Spend"})
    
    df = df.merge(cat_monthly_spend, on=["Customer_ID", "Year", "Month", "Budget_Category"], how="left").fillna({"Cat_Monthly_Spend": 0.0})
    df["Budget_Limit"] = df["Budget_Category"].map(settings.BUDGET_LIMITS).fillna(5000.0)
    df["Budget_Utilization"] = ((df["Cat_Monthly_Spend"] / df["Budget_Limit"]) * 100).round(2)
    
    # 6. Rolling averages (7-Day and 30-Day moving averages of expenses)
    logger.info("Computing moving averages...")
    
    # Compute rolling averages per customer on a daily timeline
    daily_spend = df.groupby(["Customer_ID", "Date"]).agg(
        Daily_Expense=("Expense_Amt", "sum")
    ).reset_index()
    
    daily_spend = daily_spend.sort_values(by=["Customer_ID", "Date"])
    daily_spend["Rolling_7_Day_Average"] = daily_spend.groupby("Customer_ID")["Daily_Expense"].transform(
        lambda x: x.rolling(window=7, min_periods=1).mean().round(2)
    )
    daily_spend["Rolling_30_Day_Average"] = daily_spend.groupby("Customer_ID")["Daily_Expense"].transform(
        lambda x: x.rolling(window=30, min_periods=1).mean().round(2)
    )
    daily_spend["Moving_Average"] = daily_spend["Rolling_30_Day_Average"]
    
    df = df.merge(daily_spend[["Customer_ID", "Date", "Rolling_7_Day_Average", "Rolling_30_Day_Average", "Moving_Average"]], on=["Customer_ID", "Date"], how="left")
    
    # 7. Emergency Fund Estimate (months of expenses covered)
    df["Emergency_Fund_Estimate"] = np.where(
        df["Monthly_Expense"] > 0,
        (df["Running_Balance"] / df["Monthly_Expense"]).round(2),
        0.0
    )
    df["Emergency_Fund_Estimate"] = df["Emergency_Fund_Estimate"].clip(lower=0.0) # Avoid negative runway
    
    # 8. Financial Health / Wellness Score & Risk Score (0-100) per Customer
    # Risk Score points:
    # - Debt-to-income > 40%: +30 pts
    # - Savings Rate < 15%: +25 pts
    # - Emergency Fund Estimate < 3 months: +25 pts
    # - Budget Utilization > 100%: +20 pts
    logger.info("Computing risk and financial wellness scores...")
    
    dti_risk = np.where(df["Debt_to_Income_Ratio"] > 0.40, 30.0, 0.0)
    savings_risk = np.where(df["Savings_Rate"] < 15.0, 25.0, 0.0)
    runway_risk = np.where(df["Emergency_Fund_Estimate"] < 3.0, 25.0, 0.0)
    budget_risk = np.where(df["Budget_Utilization"] > 100.0, 20.0, 0.0)
    
    df["Risk_Score"] = (dti_risk + savings_risk + runway_risk + budget_risk).clip(0.0, 100.0).round().astype(int)
    df["Financial_Wellness_Score"] = (100 - df["Risk_Score"]).astype(int)
    
    # Backwards compatibility: map Wellness Score to Financial_Health_Score
    df["Financial_Health_Score"] = df["Financial_Wellness_Score"]
    
    # 9. Miscellaneous indicators
    df["High_Spending_Flag"] = np.where(
        (df["Transaction_Type"] == "Expense") & (df["Amount"] > (df.groupby("Customer_ID")["Amount"].transform("median") * 2.5)),
        "Yes", "No"
    )
    
    df["Salary_Week_Indicator"] = df["Salary_Week"]
    df["Holiday_Indicator"] = df["Holiday"]
    df["Weekend_Indicator"] = df["Weekend"]
    df["Recurring_Expense_Flag"] = df["Recurring"]
    
    # Spending Category Score (Percentage share of category spend within customer total expense)
    logger.info("Calculating category spending velocities...")
    cust_total_exp = df[df["Transaction_Type"] == "Expense"].groupby("Customer_ID")["Amount"].transform("sum")
    df["Spending_Category_Score"] = np.where(
        df["Transaction_Type"] == "Expense",
        ((df["Amount"] / cust_total_exp) * 100).round(4),
        0.0
    )
    
    # Spending Velocity: Average daily transaction count of the customer in the current week
    df["Spending_Velocity"] = df.groupby(["Customer_ID", "Year", "Week_Number"])["Amount"].transform("count") / 7.0
    df["Spending_Velocity"] = df["Spending_Velocity"].round(2)
    
    # Drop temp columns
    df = df.drop(columns=["Income_Amt", "Expense_Amt", "Cat_Monthly_Spend", "Budget_Limit"])
    
    logger.info(f"Feature engineering pipeline complete. Shape: {df.shape}")
    df.to_csv(settings.PROCESSED_DATA_PATH, index=False)
    logger.info(f"Overwrote processed CSV at {settings.PROCESSED_DATA_PATH}")
    return df

if __name__ == "__main__":
    engineer_all_features()

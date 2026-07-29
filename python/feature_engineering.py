import os
import pandas as pd
import numpy as np
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings
from utils.logging_utils import get_logger

logger = get_logger("feature_engineering")

# Budgets from settings
from config.settings import EXPENSE_CATEGORIES

# We will use category budget thresholds to compute budget utilization
BUDGET_LIMITS = {
    "Housing": 2500.0,
    "Food & Dining": 600.0,
    "Groceries": 500.0,
    "Transportation": 300.0,
    "Shopping": 500.0,
    "Healthcare": 300.0,
    "Insurance & Taxes": 1000.0,
    "Utilities": 400.0,
    "Entertainment": 400.0,
    "Travel": 800.0,
    "Education & Self-Care": 400.0,
    "Debt Service": 500.0,
    "Investments & Savings": 2000.0,
    "Miscellaneous": 200.0
}

def engineer_all_features() -> pd.DataFrame:
    """
    Advanced Feature Engineering Pipeline.
    Computes time series, customer cash flows, rolling indicators, and financial health.
    Calculates features on a per-customer basis.
    """
    logger.info("Executing feature engineering pipeline...")
    
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
    df["Running_Balance"] = (df["Cumulative_Income"] - df["Cumulative_Expenses"]).round(2)
    
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
    
    # Burn Rate (3-month rolling expense average)
    monthly_agg["Burn_Rate"] = monthly_agg.groupby("Customer_ID")["Monthly_Expense"].transform(
        lambda x: x.rolling(window=3, min_periods=1).mean().round(2)
    )
    
    # Merge monthly aggregates back
    df = df.merge(monthly_agg.drop(columns=["Prev_Income", "Prev_Expense"]), on=["Customer_ID", "Year", "Month"], how="left")
    
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
    df["Budget_Limit"] = df["Budget_Category"].map(BUDGET_LIMITS).fillna(200.0)
    df["Budget_Utilization"] = ((df["Cat_Monthly_Spend"] / df["Budget_Limit"]) * 100).round(2)
    
    # 6. Rolling averages (7-Day and 30-Day moving averages of expenses)
    logger.info("Computing moving averages...")
    
    # Compute rolling averages per customer on a daily timeline
    daily_spend = df.groupby(["Customer_ID", "Date"]).agg(
        Daily_Expense=("Expense_Amt", "sum")
    ).reset_index()
    
    # Set Date as index, compute rolling average grouped by customer, then join back
    daily_spend = daily_spend.sort_values(by=["Customer_ID", "Date"])
    daily_spend["Rolling_7_Day_Average"] = daily_spend.groupby("Customer_ID")["Daily_Expense"].transform(
        lambda x: x.rolling(window=7, min_periods=1).mean().round(2)
    )
    daily_spend["Rolling_30_Day_Average"] = daily_spend.groupby("Customer_ID")["Daily_Expense"].transform(
        lambda x: x.rolling(window=30, min_periods=1).mean().round(2)
    )
    daily_spend["Moving_Average"] = daily_spend["Rolling_30_Day_Average"]
    
    df = df.merge(daily_spend[["Customer_ID", "Date", "Rolling_7_Day_Average", "Rolling_30_Day_Average", "Moving_Average"]], on=["Customer_ID", "Date"], how="left")
    
    # 7. Financial Health Score (0-100) per Customer
    # Computed as a function of Savings_Rate (40%), Emergency Fund (30%), and Budget Utilization (30%)
    logger.info("Computing financial health indices...")
    df["Emergency_Fund_Estimate"] = np.where(
        df["Monthly_Expense"] > 0,
        (df["Running_Balance"] / df["Monthly_Expense"]).round(2),
        0.0
    )
    df["Emergency_Fund_Estimate"] = df["Emergency_Fund_Estimate"].clip(lower=0.0) # Avoid negative runway
    
    # Normalise components
    # 6 months covered gives full 30 points
    emergency_score = np.minimum(df["Emergency_Fund_Estimate"] * 5.0, 30.0)
    # 40%+ savings rate gives full 40 points
    savings_score = np.minimum(np.maximum(df["Savings_Rate"] * 1.0, 0.0), 40.0)
    # Utilization below 100% gives full 30 points, drops off as it goes over
    budget_score = np.maximum(30.0 - np.maximum(df["Budget_Utilization"] - 100.0, 0.0) * 0.2, 0.0)
    
    df["Financial_Health_Score"] = (savings_score + emergency_score + budget_score).round().astype(int)
    
    # 8. Miscellaneous indicators
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

import os
import pandas as pd
import numpy as np
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings
from utils.logging_utils import get_logger
from utils.validation_utils import DataValidator

logger = get_logger("data_processor")

def process_and_clean_data() -> pd.DataFrame:
    """
    Data Cleaning Pipeline.
    Loads raw CSV, executes validation report, fixes categories, caps outliers,
    standardizes types, and outputs processed CSV.
    """
    logger.info("Executing data processing and cleaning pipeline...")
    
    if not os.path.exists(settings.RAW_DATA_PATH):
        raise FileNotFoundError(f"Raw transaction dataset not found at {settings.RAW_DATA_PATH}. Run generator first.")
        
    df = pd.read_csv(settings.RAW_DATA_PATH)
    logger.info(f"Loaded raw dataset with shape: {df.shape}")
    
    # 1. Run Data Validation and Save Validation Report
    validator = DataValidator(df)
    validator.validate_all()
    validator.save_report()
    
    # 2. Duplicate Removal
    duplicates = df.duplicated(subset=["Transaction_ID"]).sum()
    if duplicates > 0:
        df = df.drop_duplicates(subset=["Transaction_ID"], keep="first")
        logger.info(f"Removed {duplicates} duplicate transaction rows.")
    else:
        logger.info("No duplicate transaction IDs detected.")
        
    # 3. Invalid Transaction Removal (amounts must be positive)
    invalid_amt_mask = df["Amount"] <= 0
    invalid_amt_count = invalid_amt_mask.sum()
    if invalid_amt_count > 0:
        df = df[~invalid_amt_mask].reset_index(drop=True)
        logger.info(f"Dropped {invalid_amt_count} invalid negative or zero amount records.")
        
    # 4. Handle Missing Values
    missing_desc = df["Description"].isnull().sum()
    if missing_desc > 0:
        df["Description"] = df["Description"].fillna("Transaction at " + df["Merchant"])
        logger.info(f"Imputed {missing_desc} missing descriptions with Merchant defaults.")
        
    # 5. Category Normalization
    category_mappings = {
        "Grocries": "Groceries",
        "Foodd": "Food",
        "Entertainement": "Entertainment",
        "Subs": "Subscriptions"
    }
    inconsistent_cats = df["Category"].isin(category_mappings.keys()).sum()
    if inconsistent_cats > 0:
        df["Category"] = df["Category"].replace(category_mappings)
        logger.info(f"Corrected {inconsistent_cats} spelling errors in Category column.")
        
    # Standardize string fields
    str_cols = ["Category", "Sub_Category", "Description", "Transaction_Type", "Payment_Mode", "Merchant", "City", "State", "Country", "Account_Type", "Budget_Category"]
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip()
        
    # 6. Date Parsing & Casing Types
    df["Date"] = pd.to_datetime(df["Date"])
    df["Amount"] = df["Amount"].astype(float)
    df["Month"] = df["Month"].astype(int)
    df["Quarter"] = df["Quarter"].astype(int)
    df["Year"] = df["Year"].astype(int)
    df["Day"] = df["Day"].astype(int)
    df["Week_Number"] = df["Week_Number"].astype(int)
    
    # 7. Outlier Treatment (Capping at 99th percentile for expenses to avoid model skewing)
    expenses_mask = df["Transaction_Type"] == "Expense"
    cap_value = df.loc[expenses_mask, "Amount"].quantile(0.99)
    outliers_to_cap = (df.loc[expenses_mask, "Amount"] > cap_value).sum()
    
    if outliers_to_cap > 0:
        df.loc[expenses_mask & (df["Amount"] > cap_value), "Amount"] = cap_value
        logger.info(f"Capped {outliers_to_cap} expense values at the 99th percentile (${cap_value:.2f}).")
        
    # Save cleaned file
    os.makedirs(os.path.dirname(settings.PROCESSED_DATA_PATH), exist_ok=True)
    df.to_csv(settings.PROCESSED_DATA_PATH, index=False)
    logger.info(f"Saved processed dataset with shape {df.shape} to {settings.PROCESSED_DATA_PATH}")
    return df

if __name__ == "__main__":
    process_and_clean_data()

import os
import sqlite3
import pandas as pd
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings
from utils.logging_utils import get_logger

logger = get_logger("db_seeder")

def seed_database():
    """
    Initializes SQLite DB, creates tables, normalizes columns into Star Schema,
    and batch inserts dimensions and facts.
    """
    logger.info("Initializing SQLite database seeder...")
    
    if not os.path.exists(settings.PROCESSED_DATA_PATH):
        raise FileNotFoundError(f"Processed CSV not found at {settings.PROCESSED_DATA_PATH}")
        
    df = pd.read_csv(settings.PROCESSED_DATA_PATH)
    
    # 1. Connect to DB and run schema DDL
    conn = sqlite3.connect(settings.DATABASE_PATH)
    cursor = conn.cursor()
    
    schema_path = os.path.join(settings.BASE_DIR, "sql", "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
        
    cursor.executescript(schema_sql)
    conn.commit()
    logger.info("Star schema structure created successfully.")
    
    # 2. Seed dim_customer
    logger.info("Seeding dim_customer...")
    customer_info = [
        ("CUST-1001", "Alex Carter", "Premium"),
        ("CUST-1002", "Jordan Smith", "Standard"),
        ("CUST-1003", "Taylor Davis", "VIP")
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO dim_customer (customer_id, customer_name, segment)
        VALUES (?, ?, ?)
    """, customer_info)
    conn.commit()
    
    # 3. Seed dim_date
    logger.info("Seeding dim_date...")
    dates_df = df[["Date", "Day", "Month", "Quarter", "Year", "Week_Number", "Day_of_Week", "Weekend", "Holiday"]].drop_duplicates().reset_index(drop=True)
    dates_df.columns = ["date", "day", "month", "quarter", "year", "week_number", "day_of_week", "weekend", "holiday"]
    
    cursor.executemany("""
        INSERT OR IGNORE INTO dim_date (date, day, month, quarter, year, week_number, day_of_week, weekend, holiday)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [tuple(x) for x in dates_df.values])
    conn.commit()
    
    # 4. Seed dim_merchant
    logger.info("Seeding dim_merchant...")
    merch_df = df[["Merchant", "Merchant_Category", "Latitude", "Longitude"]].drop_duplicates().reset_index(drop=True)
    merch_df.columns = ["merchant_name", "merchant_category", "latitude", "longitude"]
    
    for _, row in merch_df.iterrows():
        cursor.execute("""
            INSERT OR IGNORE INTO dim_merchant (merchant_name, merchant_category, latitude, longitude)
            VALUES (?, ?, ?, ?)
        """, (row["merchant_name"], row["merchant_category"], row["latitude"], row["longitude"]))
    conn.commit()
    
    cursor.execute("SELECT merchant_id, merchant_name, merchant_category FROM dim_merchant")
    merch_map = {(name, cat): idx for idx, name, cat in cursor.fetchall()}
    
    # 5. Seed dim_payment
    logger.info("Seeding dim_payment...")
    pay_df = df[["Payment_Mode", "Account_Type", "Currency"]].drop_duplicates().reset_index(drop=True)
    pay_df.columns = ["payment_mode", "account_type", "currency"]
    
    for _, row in pay_df.iterrows():
        cursor.execute("""
            INSERT OR IGNORE INTO dim_payment (payment_mode, account_type, currency)
            VALUES (?, ?, ?)
        """, (row["payment_mode"], row["account_type"], row["currency"]))
    conn.commit()
    
    cursor.execute("SELECT payment_id, payment_mode, account_type, currency FROM dim_payment")
    pay_map = {(mode, acct, curr): idx for idx, mode, acct, curr in cursor.fetchall()}
    
    # 6. Seed dim_category
    logger.info("Seeding dim_category...")
    cat_df = df[["Category", "Sub_Category", "Budget_Category"]].drop_duplicates().reset_index(drop=True)
    cat_df.columns = ["category_name", "sub_category", "budget_category"]
    
    for _, row in cat_df.iterrows():
        cursor.execute("""
            INSERT OR IGNORE INTO dim_category (category_name, sub_category, budget_category)
            VALUES (?, ?, ?)
        """, (row["category_name"], row["sub_category"], row["budget_category"]))
    conn.commit()
    
    cursor.execute("SELECT category_id, category_name, sub_category FROM dim_category")
    cat_map = {(name, sub): idx for idx, name, sub in cursor.fetchall()}
    
    # 7. Seed dim_geography
    logger.info("Seeding dim_geography...")
    geo_df = df[["City", "State", "Country"]].drop_duplicates().reset_index(drop=True)
    geo_df.columns = ["city", "state", "country"]
    
    for _, row in geo_df.iterrows():
        cursor.execute("""
            INSERT OR IGNORE INTO dim_geography (city, state, country)
            VALUES (?, ?, ?)
        """, (row["city"], row["state"], row["country"]))
    conn.commit()
    
    cursor.execute("SELECT geography_id, city, state, country FROM dim_geography")
    geo_map = {(city, state, country): idx for idx, city, state, country in cursor.fetchall()}
    
    # 8. Seed fact_transactions
    logger.info("Mapping dimension foreign keys onto facts...")
    df["merchant_id"] = df.apply(lambda r: merch_map[(r["Merchant"], r["Merchant_Category"])], axis=1)
    df["payment_id"] = df.apply(lambda r: pay_map[(r["Payment_Mode"], r["Account_Type"], r["Currency"])], axis=1)
    df["category_id"] = df.apply(lambda r: cat_map[(r["Category"], r["Sub_Category"])], axis=1)
    df["geography_id"] = df.apply(lambda r: geo_map[(r["City"], r["State"], r["Country"])], axis=1)
    
    # Fill any empty fields in df
    df["Anomaly_Flag"] = df.get("Anomaly_Flag", "No").fillna("No")
    
    fact_cols = [
        "Transaction_ID", "Customer_ID", "Date", "merchant_id", "payment_id",
        "category_id", "geography_id", "Time", "Transaction_Type", "Amount",
        "Recurring", "Salary_Week", "Notes", "Cumulative_Income", "Cumulative_Expenses",
        "Running_Balance", "Monthly_Income", "Monthly_Expense", "Net_Savings", "Savings_Rate",
        "Expense_Ratio", "Cash_Flow", "Income_Growth", "Expense_Growth", "Burn_Rate",
        "Quarterly_Savings", "Budget_Utilization", "Rolling_7_Day_Average", "Rolling_30_Day_Average",
        "Moving_Average", "Emergency_Fund_Estimate", "Financial_Health_Score", "High_Spending_Flag",
        "Salary_Week_Indicator", "Holiday_Indicator", "Weekend_Indicator", "Recurring_Expense_Flag",
        "Spending_Category_Score", "Spending_Velocity", "Anomaly_Flag"
    ]
    
    # Casing mappings for SQL column insert matching DDL
    fact_df = df[fact_cols].copy()
    fact_df = fact_df.rename(columns={"Time": "time", "Anomaly_Flag": "anomaly_flag"})
    
    # Correct columns names list
    sql_cols = [c if c not in ["Time", "Anomaly_Flag"] else ("time" if c == "Time" else "anomaly_flag") for c in fact_cols]
    
    # Clear facts
    cursor.execute("DELETE FROM fact_transactions")
    conn.commit()
    
    logger.info("Executing bulk insert for fact table...")
    placeholders = ", ".join(["?"] * len(sql_cols))
    insert_sql = f"""
        INSERT INTO fact_transactions ({", ".join(sql_cols)})
        VALUES ({placeholders})
    """
    
    # Executemany
    records = [tuple(x) for x in fact_df.values]
    cursor.executemany(insert_sql, records)
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM fact_transactions")
    cnt = cursor.fetchone()[0]
    logger.info(f"Database seed complete. Inserted {cnt} facts successfully.")
    
    conn.close()

if __name__ == "__main__":
    seed_database()

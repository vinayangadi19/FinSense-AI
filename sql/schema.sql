-- Star Schema Data Warehouse DDL for Personal Finance Analytics Platform
PRAGMA foreign_keys = ON;

-- 1. Dimension Table: Customer
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    segment TEXT NOT NULL DEFAULT 'Standard'
);

-- 2. Dimension Table: Date
CREATE TABLE IF NOT EXISTS dim_date (
    date TEXT PRIMARY KEY,
    day INTEGER NOT NULL,
    month INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    year INTEGER NOT NULL,
    week_number INTEGER NOT NULL,
    day_of_week TEXT NOT NULL,
    weekend TEXT CHECK(weekend IN ('Yes', 'No')) NOT NULL,
    holiday TEXT CHECK(holiday IN ('Yes', 'No')) NOT NULL
);

-- 3. Dimension Table: Merchant
CREATE TABLE IF NOT EXISTS dim_merchant (
    merchant_id INTEGER PRIMARY KEY AUTOINCREMENT,
    merchant_name TEXT NOT NULL,
    merchant_category TEXT NOT NULL,
    latitude REAL,
    longitude REAL,
    UNIQUE(merchant_name, merchant_category)
);

-- 4. Dimension Table: Payment
CREATE TABLE IF NOT EXISTS dim_payment (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    payment_mode TEXT NOT NULL,
    account_type TEXT NOT NULL,
    currency TEXT NOT NULL DEFAULT 'USD',
    UNIQUE(payment_mode, account_type, currency)
);

-- 5. Dimension Table: Category
CREATE TABLE IF NOT EXISTS dim_category (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL,
    sub_category TEXT NOT NULL,
    budget_category TEXT NOT NULL,
    UNIQUE(category_name, sub_category)
);

-- 6. Dimension Table: Geography
CREATE TABLE IF NOT EXISTS dim_geography (
    geography_id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    country TEXT NOT NULL,
    UNIQUE(city, state, country)
);

-- 7. Fact Table: Transactions
CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    date TEXT NOT NULL,
    merchant_id INTEGER NOT NULL,
    payment_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    geography_id INTEGER NOT NULL,
    time TEXT NOT NULL,
    transaction_type TEXT CHECK(transaction_type IN ('Income', 'Expense')) NOT NULL,
    amount REAL NOT NULL CHECK(amount > 0),
    recurring TEXT NOT NULL,
    salary_week TEXT NOT NULL,
    notes TEXT,
    
    -- Feature Engineered Columns
    cumulative_income REAL,
    cumulative_expenses REAL,
    running_balance REAL,
    monthly_income REAL,
    monthly_expense REAL,
    net_savings REAL,
    savings_rate REAL,
    expense_ratio REAL,
    cash_flow REAL,
    income_growth REAL,
    expense_growth REAL,
    burn_rate REAL,
    quarterly_savings REAL,
    budget_utilization REAL,
    rolling_7_day_average REAL,
    rolling_30_day_average REAL,
    moving_average REAL,
    emergency_fund_estimate REAL,
    financial_health_score INTEGER,
    high_spending_flag TEXT NOT NULL,
    salary_week_indicator TEXT NOT NULL,
    holiday_indicator TEXT NOT NULL,
    weekend_indicator TEXT NOT NULL,
    recurring_expense_flag TEXT NOT NULL,
    spending_category_score REAL,
    spending_velocity REAL,
    anomaly_flag TEXT CHECK(anomaly_flag IN ('Yes', 'No')) NOT NULL DEFAULT 'No',
    
    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY (date) REFERENCES dim_date(date),
    FOREIGN KEY (merchant_id) REFERENCES dim_merchant(merchant_id),
    FOREIGN KEY (payment_id) REFERENCES dim_payment(payment_id),
    FOREIGN KEY (category_id) REFERENCES dim_category(category_id),
    FOREIGN KEY (geography_id) REFERENCES dim_geography(geography_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_fact_date ON fact_transactions(date);
CREATE INDEX IF NOT EXISTS idx_fact_customer ON fact_transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_fact_category ON fact_transactions(category_id);
CREATE INDEX IF NOT EXISTS idx_fact_merchant ON fact_transactions(merchant_id);
CREATE INDEX IF NOT EXISTS idx_fact_geography ON fact_transactions(geography_id);
CREATE INDEX IF NOT EXISTS idx_fact_type ON fact_transactions(transaction_type);

-- Analytical Views
-- View: Monthly Wallet Insights
CREATE VIEW IF NOT EXISTS view_monthly_wallet_summary AS
SELECT 
    t.customer_id,
    d.year,
    d.month,
    t.monthly_income,
    t.monthly_expense,
    t.net_savings,
    t.savings_rate,
    t.expense_ratio,
    t.financial_health_score
FROM fact_transactions t
JOIN dim_date d ON t.date = d.date
GROUP BY t.customer_id, d.year, d.month;


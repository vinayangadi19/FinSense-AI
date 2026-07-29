-- Advanced SQL Queries for Normalized Data Warehouse Star Schema

-- 1. Monthly Financial KPI Summary per Customer (CTEs & Joins)
-- Extracts total income, total expense, savings, and savings rate by joining dim_customer and fact_transactions.
WITH Monthly_Totals AS (
    SELECT 
        c.customer_name AS Customer_Name,
        d.year AS Year_Val,
        d.month AS Month_Val,
        SUM(CASE WHEN t.transaction_type = 'Income' THEN t.amount ELSE 0 END) AS Total_Income,
        SUM(CASE WHEN t.transaction_type = 'Expense' THEN t.amount ELSE 0 END) AS Total_Expense
    FROM fact_transactions t
    JOIN dim_customer c ON t.customer_id = c.customer_id
    JOIN dim_date d ON t.date = d.date
    GROUP BY Customer_Name, Year_Val, Month_Val
)
SELECT 
    Customer_Name,
    Year_Val || '-' || printf('%02d', Month_Val) AS Month_Period,
    ROUND(Total_Income, 2) AS Income,
    ROUND(Total_Expense, 2) AS Expense,
    ROUND(Total_Income - Total_Expense, 2) AS Savings,
    ROUND(
        ((Total_Income - Total_Expense) / NULLIF(Total_Income, 0)) * 100, 
        2
    ) AS Savings_Percentage
FROM Monthly_Totals
ORDER BY Customer_Name, Month_Period DESC;


-- 2. Customer Spending Velocity and Window Rolling Averages
-- Uses Window functions to track the 3-transaction rolling average expense per customer.
SELECT 
    t.transaction_id AS Txn_ID,
    c.customer_name AS Customer,
    t.date AS Date_Val,
    cat.category_name AS Category,
    t.amount AS Amount,
    ROUND(
        AVG(t.amount) OVER (
            PARTITION BY t.customer_id 
            ORDER BY t.date, t.time 
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ), 
        2
    ) AS Rolling_3Txn_Average_Expense
FROM fact_transactions t
JOIN dim_customer c ON t.customer_id = c.customer_id
JOIN dim_category cat ON t.category_id = cat.category_id
WHERE t.transaction_type = 'Expense'
LIMIT 15;


-- 3. Top Spending Merchants Rank per Customer segment (Ranking Window Function)
-- Ranks merchants by total expense within each customer segment.
WITH Merchant_Ranks AS (
    SELECT 
        c.segment AS Customer_Segment,
        m.merchant_name AS Merchant,
        m.merchant_category AS Merchant_Category,
        ROUND(SUM(t.amount), 2) AS Total_Spent,
        DENSE_RANK() OVER (
            PARTITION BY c.segment 
            ORDER BY SUM(t.amount) DESC
        ) AS Merchant_Rank
    FROM fact_transactions t
    JOIN dim_customer c ON t.customer_id = c.customer_id
    JOIN dim_merchant m ON t.merchant_id = m.merchant_id
    WHERE t.transaction_type = 'Expense'
    GROUP BY Customer_Segment, Merchant
)
SELECT * 
FROM Merchant_Ranks
WHERE Merchant_Rank <= 5;


-- 4. Geographic Expense Distribution Analysis
-- Aggregates spending totals, counts, and averages by city and state.
SELECT 
    g.city AS City,
    g.state AS State,
    COUNT(t.transaction_id) AS Transaction_Count,
    ROUND(SUM(t.amount), 2) AS Total_Spent,
    ROUND(AVG(t.amount), 2) AS Average_Transaction_Value
FROM fact_transactions t
JOIN dim_geography g ON t.geography_id = g.geography_id
WHERE t.transaction_type = 'Expense'
GROUP BY City, State
ORDER BY Total_Spent DESC;


-- 5. MoM Expense Growth Rate (Lead/Lag Window Functions)
-- Uses LAG to calculate month-over-month expense trends.
WITH Monthly_Expenses AS (
    SELECT 
        c.customer_name AS Customer,
        d.year AS Year_Val,
        d.month AS Month_Val,
        SUM(t.amount) AS Current_Month_Expense
    FROM fact_transactions t
    JOIN dim_customer c ON t.customer_id = c.customer_id
    JOIN dim_date d ON t.date = d.date
    WHERE t.transaction_type = 'Expense'
    GROUP BY Customer, Year_Val, Month_Val
),
Expense_Lags AS (
    SELECT 
        Customer,
        Year_Val || '-' || printf('%02d', Month_Val) AS Period,
        Current_Month_Expense,
        LAG(Current_Month_Expense, 1) OVER (
            PARTITION BY Customer 
            ORDER BY Year_Val, Month_Val
        ) AS Previous_Month_Expense
    FROM Monthly_Expenses
)
SELECT 
    Customer,
    Period,
    ROUND(Current_Month_Expense, 2) AS Spent,
    ROUND(Previous_Month_Expense, 2) AS Prev_Spent,
    ROUND(
        ((Current_Month_Expense - Previous_Month_Expense) / NULLIF(Previous_Month_Expense, 0)) * 100, 
        2
    ) AS MoM_Growth_Rate_Pct
FROM Expense_Lags
ORDER BY Customer, Period ASC;


-- 6. Category-wise Budget Breach Warnings
-- Flags instances where monthly spending on a category exceeds the predefined limits.
SELECT 
    c.customer_name AS Customer,
    d.year || '-' || printf('%02d', d.month) AS Period,
    cat.budget_category AS Budget_Category,
    ROUND(SUM(t.amount), 2) AS Total_Spent,
    t.budget_utilization AS Budget_Utilization_Pct
FROM fact_transactions t
JOIN dim_customer c ON t.customer_id = c.customer_id
JOIN dim_date d ON t.date = d.date
JOIN dim_category cat ON t.category_id = cat.category_id
WHERE t.transaction_type = 'Expense' AND t.budget_utilization > 100
GROUP BY Customer, Period, Budget_Category
ORDER BY Budget_Utilization_Pct DESC
LIMIT 10;

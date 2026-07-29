# Personal Finance Platform: Data Dictionary

This document defines the columns of our financial transactions database, separating them into **Raw Inputs** (from ledger bank files) and **Engineered Features** (computed dynamically).

---

## 1. Raw Input Schema (Bank Ledger)

| Column Name | Data Type | Source / Format | Description |
| :--- | :--- | :--- | :--- |
| **Transaction_ID** | `TEXT` | PK / `TXN-XXXXXX` | Unique primary key identifying each transaction. |
| **Customer_ID** | `TEXT` | FK / `CUST-XXXX` | Reference key linking to the customer dimension. |
| **Date** | `TEXT` | `YYYY-MM-DD` | Calendar date of transaction execution. |
| **Time** | `TEXT` | `HH:MM:SS` | Timestamp hour/min/sec of transaction. |
| **Month** | `INTEGER` | Calendar Month (1-12) | Year partition indicator. |
| **Quarter** | `INTEGER` | Calendar Quarter (1-4) | Quarterly grouping indicator. |
| **Year** | `INTEGER` | Calendar Year (e.g. 2025) | Annual grouping indicator. |
| **Week_Number** | `INTEGER` | ISO week number (1-53) | Week grouping indicator. |
| **Day** | `INTEGER` | Day of Month (1-31) | Day indicator. |
| **Day_of_Week** | `TEXT` | e.g. "Monday" | Day of week name. |
| **Weekend** | `TEXT` | `Yes` / `No` | Flag identifying weekend transaction activity. |
| **Category** | `TEXT` | Standard Map | High-level category (e.g. Groceries). |
| **Sub_Category** | `TEXT` | Standard Map | Detail category (e.g. Supermarket Groceries). |
| **Description** | `TEXT` | Bank String | Narrative text associated with the charge. |
| **Merchant** | `TEXT` | Standard Map | Commercial counterparty name. |
| **Merchant_Category**| `TEXT` | Standard Map | Category classification of the counterparty. |
| **Transaction_Type** | `TEXT` | `Income` / `Expense` | Cash flow direction indicator. |
| **Amount** | `REAL` | Float ($) | Transaction value (positive decimal). |
| **Currency** | `TEXT` | `USD` | Transaction currency denominative. |
| **Payment_Mode** | `TEXT` | Card, UPI, etc. | Payment channel chosen. |
| **Account_Type** | `TEXT` | Savings, Credit Card | Financial account type. |
| **City** | `TEXT` | Geography Map | City where transaction was placed. |
| **State** | `TEXT` | Geography Map | State abbreviation. |
| **Country** | `TEXT` | Geography Map | Country name. |
| **Latitude** | `REAL` | Float | Approximate latitude coordinate. |
| **Longitude** | `REAL` | Float | Approximate longitude coordinate. |
| **Budget_Category** | `TEXT` | Budget Map | Category group for budget limits. |
| **Income_Source** | `TEXT` | Income Map | Classification for income flows. |
| **Expense_Tag** | `TEXT` | `Essential`/`Discretionary`| Classification of expenses. |
| **Recurring** | `TEXT` | `Yes` / `No` | Identifies auto-scheduled transactions. |
| **Salary_Week** | `TEXT` | `Yes` / `No` | Flag for dates around paycheck payouts. |
| **Holiday** | `TEXT` | `Yes` / `No` | Flag indicating major US holidays. |
| **Notes** | `TEXT` | Free text | Narrative annotation. |

---

## 2. Feature Engineered Schema (Derived Metrics)

| Column Name | Data Type | Formula / Origin | Description |
| :--- | :--- | :--- | :--- |
| **Cumulative_Income** | `REAL` | CumSum of Income | Running sum of all income to date. |
| **Cumulative_Expenses**| `REAL` | CumSum of Expenses| Running sum of all expenses to date. |
| **Running_Balance** | `REAL` | Income - Expense | Current ledger cash holdings balance. |
| **Monthly_Income** | `REAL` | GroupBy(Customer, Month) | Total income in calendar month. |
| **Monthly_Expense** | `REAL` | GroupBy(Customer, Month) | Total expenses in calendar month. |
| **Net_Savings** | `REAL` | Income - Expense | Net savings in calendar month. |
| **Savings_Rate** | `REAL` | Savings / Income * 100 | Percentage of monthly income saved. |
| **Expense_Ratio** | `REAL` | Expense / Income * 100 | Percentage of monthly income spent. |
| **Cash_Flow** | `REAL` | Monthly Net Savings | Net cash surplus/deficit. |
| **Income_Growth** | `REAL` | MoM Pct Change | Month-over-month income growth rate. |
| **Expense_Growth** | `REAL` | MoM Pct Change | Month-over-month expense growth rate. |
| **Burn_Rate** | `REAL` | Rolling mean of Expense | 3-month rolling average expense. |
| **Quarterly_Savings** | `REAL` | GroupBy(Customer, Quarter) | Total savings in calendar quarter. |
| **Budget_Utilization** | `REAL` | Category Spend / Limit * 100| Percentage of budget allocation consumed. |
| **Rolling_7_Day_Avg** | `REAL` | 7-day rolling mean | Short-term spending velocity. |
| **Rolling_30_Day_Avg**| `REAL` | 30-day rolling mean | Mid-term spending velocity. |
| **Moving_Average** | `REAL` | 30-day rolling mean | Aligns with the 30-day baseline. |
| **Emergency_Fund_Est** | `REAL` | Balance / Monthly Expense | Runway months covered by current balance. |
| **Financial_Health_Score**|`INTEGER`| Custom Composite Index | Score between 0-100 indicating stability. |
| **High_Spending_Flag**| `TEXT` | Amount > 2.5 * Median | Flags unusual high-value expenses. |
| **Spending_Category_Score**|`REAL`| Category Spend / Total | Share of category spend within customer total. |
| **Spending_Velocity** | `REAL` | Count / 7 | Daily transaction frequency. |
| **Anomaly_Flag** | `TEXT` | Isolation Forest Output | Flags unusual transaction behavior. |

# Personal Finance Platform: Executive Report

**Prepared For**: C-Suite / Executive Stakeholders  
**Author**: Lead Analytics Architect & Data Scientist  
**Date**: July 2026  

---

## 1. Project Background & Goal
The objective of this project was to construct a production-ready, automated **Personal Finance Analytics & Predictive Platform**. By developing a robust, end-to-end data pipeline, we empower financial institutions and users to track cash flows, enforce budgets, detect anomalous activities, and forecast spending habits with high reliability.

---

## 2. Key Analytical & Financial Metrics

Our analytics engine uncovered key behavioral insights across the client cohort:

### Core Financial Outcomes
*   **Average Savings Rate**:
    *   **VIP Cohort**: 45.6% savings rate on an average income of $12,500/month.
    *   **Premium Cohort**: 56.9% savings rate on an average income of $7,200/month.
    *   **Standard Cohort**: 25.6% savings rate on an average income of $4,100/month.
*   **Budget Breach Frequency**: Entertainment and Shopping budgets are violated in **14.2% of tracking months**, representing the primary leak in net savings.
*   **Emergency Fund Reserves**: The Premium and VIP segments maintain **over 5 months of runway**, while the Standard cohort has less than **2.8 months of liquid safety cover**.

---

## 3. Machine Learning Business Impact

Our enterprise ML layer adds high-value predictive capabilities to the platform:

1.  **Isolation Forest (Anomaly Detection)**: Flags unauthorized card charges, medical bill spikes, or unexpected bank fees with a **1.0% false-alarm constraint**.
2.  **XGBoost Regressor (Predictive Budgeting)**: Forecasts next month's spending with a Mean Absolute Error of **~$1,285.33**, helping users anticipate cash-flow constraints and prevent budget breaches before they occur.
3.  **K-Means (Spending Profiling)**: Clusters users into 3 behavioral profiles ("Conservative", "Discretionary Spender", "Fixed Rent Constrained") to drive personalized product recommendations.
4.  **Prophet (Trend Forecasting)**: Pre-computes 30-day ahead transaction volumes to support cash reserve management.

---

## 4. Platform Dashboards Overview

To deliver these insights to business and customer stakeholders, we constructed two enterprise visualization interfaces:

### Interactive Streamlit Application
*   A responsive dashboard built with Python.
*   Enables dynamic transaction ledger CSV uploads.
*   Interactive Plotly visualizations mapping monthly trends, category shares, and cumulative balances.
*   Embeds XGBoost predictions and Isolation Forest anomaly warnings.
*   Interactive budget calculator incorporating the standard 50/30/20 rule.

### Power BI Executive Report
*   Built on a normalized SQLite star schema database.
*   Visualizes geographical heatmaps, MoM cash growth, and category segment rankings.
*   Includes professional theme configurations (`dashboard/powerbi_theme.json`) and pre-calculated DAX measures (`dashboard/powerbi_dax.txt`).

---

## 5. Technical Pipeline Status
The entire platform is fully automated and reproducible via standard commands:
*   **Make install**: Automatically downloads all system dependencies.
*   **Make run-pipeline**: Runs data generation, processing, validation, feature engineering, ML fitting, and database seeding.
*   **Make test**: Executes 11 unit tests verifying data quality, SQLite queries, and model inference.

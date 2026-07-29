import os
import nbformat as nbf

def create_notebook():
    """
    Programmatically builds notebooks/eda_and_modeling.ipynb with complete code
    for EDA visualizations (matplotlib/seaborn/plotly) and ML modeling.
    Uses joblib instead of pickle to load model pipelines.
    """
    nb = nbf.v4.new_notebook()
    
    # Title Markdown
    cells = [
        nbf.v4.new_markdown_cell(
            "# Enterprise Personal Finance Analytics\n"
            "### Exploratory Data Analysis & Machine Learning Pipeline\n"
            "This notebook walks through the data analysis, visualization, and machine learning models for the Personal Finance project.\n"
            "We will explore spending patterns, verify correlations, segment behavior, detect transaction anomalies, and forecast future cash flows."
        )
    ]
    
    # Imports code
    cells.append(nbf.v4.new_code_cell(
        "import os\n"
        "import pandas as pd\n"
        "import numpy as np\n"
        "import matplotlib.pyplot as plt\n"
        "import seaborn as sns\n"
        "import plotly.express as px\n"
        "import plotly.graph_objects as go\n"
        "import sqlite3\n"
        "import joblib\n"
        "from datetime import datetime\n"
        "\n"
        "# Set styling\n"
        "plt.style.use('ggplot')\n"
        "sns.set_theme(style='whitegrid')\n"
        "pd.set_option('display.max_columns', None)\n"
        "print('Imports complete. Environment ready.')"
    ))
    
    # Load data code
    cells.append(nbf.v4.new_code_cell(
        "processed_csv_path = '../data/processed/transactions_processed.csv'\n"
        "df = pd.read_csv(processed_csv_path)\n"
        "df['Date'] = pd.to_datetime(df['Date'])\n"
        "print(f'Loaded cleaned dataset with {len(df)} records and {df.shape[1]} columns.')\n"
        "df.head(2)"
    ))
    
    # Portfolio Summary Markdown
    cells.append(nbf.v4.new_markdown_cell(
        "## Part 1: Executive Portfolio Summary\n"
        "Let's compute our key financial performance indicators (KPIs):\n"
        "1. **Total Income**\n"
        "2. **Total Expenses**\n"
        "3. **Net Savings**\n"
        "4. **Savings Rate (%)**\n"
        "5. **Average Monthly Income & Expense**"
    ))
    
    # Summary calculation code
    cells.append(nbf.v4.new_code_cell(
        "# High-level stats\n"
        "total_income = df[df['Transaction_Type'] == 'Income']['Amount'].sum()\n"
        "total_expense = df[df['Transaction_Type'] == 'Expense']['Amount'].sum()\n"
        "net_savings = total_income - total_expense\n"
        "savings_rate = (net_savings / total_income) * 100\n"
        "\n"
        "print('=== OVERALL PORTFOLIO METRICS ===')\n"
        "print(f'Total Income: ${total_income:,.2f}')\n"
        "print(f'Total Expense: ${total_expense:,.2f}')\n"
        "print(f'Net Savings: ${net_savings:,.2f}')\n"
        "print(f'Savings Rate: {savings_rate:.2f}%')\n"
        "\n"
        "# Monthly averages\n"
        "monthly_totals = df.groupby(['Year', 'Month', 'Transaction_Type'])['Amount'].sum().unstack(fill_value=0)\n"
        "avg_monthly_income = monthly_totals['Income'].mean()\n"
        "avg_monthly_expense = monthly_totals['Expense'].mean()\n"
        "print(f'Average Monthly Income: ${avg_monthly_income:,.2f}')\n"
        "print(f'Average Monthly Expense: ${avg_monthly_expense:,.2f}')"
    ))
    
    # Financial Trends Markdown
    cells.append(nbf.v4.new_markdown_cell(
        "## Part 2: Spending and Cash Flow Trends\n"
        "We'll visualize our monthly income vs monthly expenses and see how the net wallet balance has grown over time."
    ))
    
    # Trend plots code
    cells.append(nbf.v4.new_code_cell(
        "# Aggregate monthly cash flows\n"
        "monthly_flow = df.groupby(['Year', 'Month'])[['Monthly_Income', 'Monthly_Expense', 'Net_Savings']].first().reset_index()\n"
        "monthly_flow['Period'] = pd.to_datetime(monthly_flow.apply(lambda r: f'{int(r[\"Year\"])}-{int(r[\"Month\"])}-01', axis=1))\n"
        "monthly_flow = monthly_flow.sort_values(by='Period').reset_index(drop=True)\n"
        "\n"
        "# Plotting Income vs Expense Over Time\n"
        "plt.figure(figsize=(14, 6))\n"
        "plt.plot(monthly_flow['Period'], monthly_flow['Monthly_Income'], label='Monthly Income', color='#2ecc71', linewidth=2.5, marker='o')\n"
        "plt.plot(monthly_flow['Period'], monthly_flow['Monthly_Expense'], label='Monthly Expense', color='#e74c3c', linewidth=2.5, marker='o')\n"
        "plt.fill_between(monthly_flow['Period'], monthly_flow['Monthly_Income'], monthly_flow['Monthly_Expense'], \n"
        "                 where=(monthly_flow['Monthly_Income'] > monthly_flow['Monthly_Expense']), facecolor='#2ecc71', alpha=0.15)\n"
        "plt.title('Monthly Income vs Expense Trend', fontsize=16, fontweight='bold')\n"
        "plt.xlabel('Date', fontsize=12)\n"
        "plt.ylabel('Amount ($)', fontsize=12)\n"
        "plt.legend(frameon=True)\n"
        "plt.tight_layout()\n"
        "plt.show()\n"
        "\n"
        "# Running Balance (Wallet Size Progression)\n"
        "plt.figure(figsize=(14, 5))\n"
        "plt.fill_between(df['Date'], df['Running_Balance'], color='#3498db', alpha=0.3, label='Wallet Balance')\n"
        "plt.plot(df['Date'], df['Running_Balance'], color='#2980b9', linewidth=2)\n"
        "plt.title('Running Net Worth / Balance Progression', fontsize=16, fontweight='bold')\n"
        "plt.xlabel('Date', fontsize=12)\n"
        "plt.ylabel('Running Balance ($)', fontsize=12)\n"
        "plt.legend()\n"
        "plt.tight_layout()\n"
        "plt.show()"
    ))
    
    # Category / Merchant Breakdown Markdown
    cells.append(nbf.v4.new_markdown_cell(
        "## Part 3: Expense Category & Merchant Analysis\n"
        "Let's identify where the money is actually going. We'll show the top categories and the top merchants by total spent."
    ))
    
    # Category plots code
    cells.append(nbf.v4.new_code_cell(
        "# Category Breakdown\n"
        "cat_spend = df[df['Transaction_Type'] == 'Expense'].groupby('Category')['Amount'].sum().reset_index().sort_values(by='Amount', ascending=False)\n"
        "\n"
        "# Donut chart for Category distribution using Plotly\n"
        "fig_donut = px.pie(cat_spend, values='Amount', names='Category', hole=0.5, \n"
        "                   title='Overall Expense Distribution by Category',\n"
        "                   color_discrete_sequence=px.colors.qualitative.Pastel)\n"
        "fig_donut.update_traces(textposition='inside', textinfo='percent+label')\n"
        "fig_donut.show()\n"
        "\n"
        "# Top Merchants\n"
        "merch_spend = df[df['Transaction_Type'] == 'Expense'].groupby('Merchant')['Amount'].sum().reset_index().sort_values(by='Amount', ascending=False).head(10)\n"
        "plt.figure(figsize=(12, 5))\n"
        "sns.barplot(data=merch_spend, x='Amount', y='Merchant', palette='rocket')\n"
        "plt.title('Top 10 Merchants by Total Spending', fontsize=16, fontweight='bold')\n"
        "plt.xlabel('Total Spending ($)', fontsize=12)\n"
        "plt.ylabel('Merchant', fontsize=12)\n"
        "plt.tight_layout()\n"
        "plt.show()"
    ))
    
    # Weekend vs Weekday Markdown
    cells.append(nbf.v4.new_markdown_cell(
        "## Part 4: Weekend Spend Analysis & Payment Modes\n"
        "Do spending habits shift on weekends? Let's check the distributions of transaction values on weekends vs weekdays, and see which payment modes are used most."
    ))
    
    # Weekend / Payment code
    cells.append(nbf.v4.new_code_cell(
        "# Filter for expenses\n"
        "expenses = df[df['Transaction_Type'] == 'Expense']\n"
        "\n"
        "# Boxplot/Violin plot for transaction amount distribution\n"
        "plt.figure(figsize=(10, 5))\n"
        "sns.violinplot(data=expenses, x='Weekend', y='Amount', palette='Set2', inner='quartile')\n"
        "plt.yscale('log') # Log scale since amounts range from $4 to $1,500\n"
        "plt.title('Transaction Value Distribution: Weekdays vs Weekends', fontsize=15, fontweight='bold')\n"
        "plt.xlabel('Is Weekend?', fontsize=12)\n"
        "plt.ylabel('Transaction Value (Log Scale, $)', fontsize=12)\n"
        "plt.tight_layout()\n"
        "plt.show()\n"
        "\n"
        "# Payment Mode Distribution\n"
        "payment_counts = expenses['Payment_Mode'].value_counts().reset_index()\n"
        "fig_pie = px.pie(payment_counts, values='count', names='Payment_Mode', \n"
        "                 title='Payment Mode Utilization (Frequency)',\n"
        "                 color_discrete_sequence=px.colors.sequential.RdBu)\n"
        "fig_pie.show()"
    ))
    
    # Correlation & Volatility Markdown
    cells.append(nbf.v4.new_markdown_cell(
        "## Part 5: Correlation Matrix & Statistical Heatmaps\n"
        "Let's look at the correlation between numeric variables such as transaction amounts, monthly budget utilization, rolling average spending, and time variables."
    ))
    
    # Correlation code
    cells.append(nbf.v4.new_code_cell(
        "# Correlation Matrix on numeric features\n"
        "numeric_cols = ['Amount', 'Month', 'Year', 'Week_Number', 'Running_Balance', \n"
        "                'Monthly_Income', 'Monthly_Expense', 'Net_Savings', \n"
        "                'Budget_Utilization', 'Rolling_30_Day_Average']\n"
        "\n"
        "corr = df[numeric_cols].corr()\n"
        "\n"
        "plt.figure(figsize=(10, 8))\n"
        "sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', square=True, linewidths=0.5)\n"
        "plt.title('Correlation Heatmap of Financial Features', fontsize=15, fontweight='bold')\n"
        "plt.tight_layout()\n"
        "plt.show()"
    ))
    
    # KMeans Segmentation Markdown
    cells.append(nbf.v4.new_markdown_cell(
        "## Part 6: Machine Learning - KMeans Spending Segmentation\n"
        "We'll load the saved K-Means model to segment our months and print their profiles."
    ))
    
    # KMeans profiling code
    cells.append(nbf.v4.new_code_cell(
        "kmeans_model = joblib.load('../models/kmeans_model.joblib')\n"
        "kmeans_scaler = joblib.load('../models/kmeans_scaler.joblib')\n"
        "\n"
        "print('K-Means Model successfully loaded.')\n"
        "# Create the same feature vectors we trained on\n"
        "monthly_cat_spend = df[df['Transaction_Type'] == 'Expense'].groupby(['Customer_ID', 'Year', 'Month', 'Category'])['Amount'].sum().unstack(fill_value=0.0).reset_index()\n"
        "feature_cols = [c for c in monthly_cat_spend.columns if c not in ['Customer_ID', 'Year', 'Month']]\n"
        "X_clust = monthly_cat_spend[feature_cols]\n"
        "\n"
        "scaled_features = kmeans_scaler.transform(X_clust)\n"
        "monthly_cat_spend['Cluster'] = kmeans_model.predict(scaled_features)\n"
        "\n"
        "# Profiling\n"
        "cluster_profiles = monthly_cat_spend.groupby('Cluster')[feature_cols].mean().round(2)\n"
        "print(cluster_profiles)"
    ))
    
    # Isolation Forest Markdown
    cells.append(nbf.v4.new_markdown_cell(
        "## Part 7: Machine Learning - Anomaly Detection\n"
        "We can check which transactions are flagged as anomalies. Outlier transactions are typically large medical expenses, large vacations, or massive inheritances."
    ))
    
    # Anomaly code
    cells.append(nbf.v4.new_code_cell(
        "anomalies = df[df['Anomaly_Flag'] == 'Yes']\n"
        "print(f'Total Anomalies Flagged: {len(anomalies)} ({len(anomalies)/len(df)*100:.2f}%)')\n"
        "\n"
        "# Let's display the top 10 largest anomalous transactions\n"
        "anomalies.sort_values(by='Amount', ascending=False)[['Date', 'Category', 'Merchant', 'Amount', 'Description', 'Notes']].head(10)"
    ))
    
    # Time Series Forecasting Markdown
    cells.append(nbf.v4.new_markdown_cell(
        "## Part 8: Machine Learning - Time Series Forecasting\n"
        "Let's load the trained XGBoost model and forecast the next month's spending based on the last 3 months."
    ))
    
    # Forecasting code
    cells.append(nbf.v4.new_code_cell(
        "xgboost_model = joblib.load('../models/xgboost_model.joblib')\n"
        "\n"
        "# Let's prepare a sample feature vector representing the last 3 months of historical data\n"
        "# Suppose: \n"
        "# - Lag 1 (last month's expense) = $4200\n"
        "# - Lag 2 (2 months ago) = $4400\n"
        "# - Lag 3 (3 months ago) = $4100\n"
        "# - Rolling 3-Month Mean = $4233\n"
        "# - Month Number (e.g. August) = 8\n"
        "\n"
        "sample_features = pd.DataFrame([{\n"
        "    'Lag_1': 4200.0,\n"
        "    'Lag_2': 4400.0,\n"
        "    'Lag_3': 4100.0,\n"
        "    'Rolling_Mean_3M': 4233.33,\n"
        "    'Month_Num': 8\n"
        "}])\n"
        "\n"
        "predicted_expense = xgboost_model.predict(sample_features)[0]\n"
        "print(f'Forecasted Expense for the next month: ${predicted_expense:,.2f}')"
    ))
    
    # Business Insights Markdown
    cells.append(nbf.v4.new_markdown_cell(
        "## Part 9: Key Business Insights\n"
        "1. **Discretionary vs Essential Spending**: Discretionary expenses (Dining out, travel, shopping) accounts for a large percentage of total expenses. These are prime areas for budget trimming.\n"
        "2. **Savings Cushion**: The average monthly savings rate is healthy, but emergency funds should be set aside to smooth out outlier expenses (e.g. unexpected medical or large travel payments).\n"
        "3. **Credit Card Risk**: Credit cards represent the most frequent payment channel, requiring close attention to avoid rolling over revolving credit balances."
    ))
    
    # Set cells in notebook
    nb['cells'] = cells
    
    # Create notebooks folder if it doesn't exist
    os.makedirs("../notebooks", exist_ok=True)
    notebook_path = "../notebooks/eda_and_modeling.ipynb"
    
    with open(notebook_path, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
        
    print(f"Notebook successfully created at: {notebook_path}")

if __name__ == "__main__":
    create_notebook()

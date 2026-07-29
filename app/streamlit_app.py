import os
import sys
import joblib
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Set page layout to wide and title
st.set_page_config(
    page_title="Enterprise Personal Finance Analytics",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark glassmorphism styling
st.markdown("""
<style>
    .reportview-container {
        background: #0d1117;
    }
    .metric-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.15);
    }
    .metric-value-income {
        color: #00E676;
        font-size: 32px;
        font-weight: bold;
    }
    .metric-value-expense {
        color: #FF5252;
        font-size: 32px;
        font-weight: bold;
    }
    .metric-value-savings {
        color: #29B6F6;
        font-size: 32px;
        font-weight: bold;
    }
    .metric-value-percent {
        color: #FFD700;
        font-size: 32px;
        font-weight: bold;
    }
    .metric-title {
        color: #8b949e;
        font-size: 14px;
        text-transform: uppercase;
        margin-bottom: 5px;
        font-weight: 600;
    }
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Outfit', 'Inter', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to get paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "transactions_processed.csv")
MODELS_DIR = os.path.join(BASE_DIR, "models")
SHAP_IMAGE_PATH = os.path.join(BASE_DIR, "images", "shap_summary.png")

@st.cache_data
def load_data(file_path):
    if not os.path.exists(file_path):
        return None
    df = pd.read_csv(file_path)
    df["Date"] = pd.to_datetime(df["Date"])
    return df

# Load initial data
df = load_data(PROCESSED_DATA_PATH)

# Sidebar branding
st.sidebar.markdown("<h1 style='text-align: center; color: #00E676;'>💰 Antigravity Finance</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; color: #8b949e;'>Enterprise Analytics & Prediction</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

# CSV File Uploader
uploaded_file = st.sidebar.file_uploader("Upload Transaction Ledger (CSV)", type=["csv"])
if uploaded_file is not None:
    try:
        df_uploaded = pd.read_csv(uploaded_file)
        df_uploaded["Date"] = pd.to_datetime(df_uploaded["Date"])
        df = df_uploaded
        st.sidebar.success("Custom ledger uploaded successfully!")
    except Exception as e:
        st.sidebar.error(f"Error loading CSV: {e}")

if df is None:
    st.error("No dataset found. Please run data generator pipeline first, or upload transaction CSV.")
    st.stop()

# Sidebar Filters
st.sidebar.subheader("Filters")
min_date = df["Date"].min().to_pydatetime()
max_date = df["Date"].max().to_pydatetime()

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Extract and validate range
if len(date_range) == 2:
    start_dt, end_dt = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
else:
    start_dt, end_dt = pd.to_datetime(min_date), pd.to_datetime(max_date)

# Customer ID Selection
customers = sorted(df["Customer_ID"].dropna().unique().tolist())
selected_customer = st.sidebar.selectbox("Select Customer Profile", customers)

categories = ["All"] + sorted(df["Category"].dropna().unique().tolist())
selected_category = st.sidebar.selectbox("Category Filter", categories)

payment_modes = ["All"] + sorted(df["Payment_Mode"].dropna().unique().tolist())
selected_payment = st.sidebar.selectbox("Payment Method", payment_modes)

# Apply filters
filtered_df = df[
    (df["Date"] >= start_dt) & 
    (df["Date"] <= end_dt) &
    (df["Customer_ID"] == selected_customer)
]

if selected_category != "All":
    filtered_df = filtered_df[filtered_df["Category"] == selected_category]

if selected_payment != "All":
    filtered_df = filtered_df[filtered_df["Payment_Mode"] == selected_payment]

# Main tabs
tab_dash, tab_budget, tab_ml, tab_health = st.tabs([
    "📊 Financial Analytics",
    "🎯 Budget Planner & Optimizer",
    "🔮 ML Prediction & Explainers",
    "🛡️ Financial Health Meter"
])

# -------------------------------------------------------------
# TAB 1: FINANCIAL ANALYTICS
# -------------------------------------------------------------
with tab_dash:
    st.title(f"Financial Insights: {selected_customer}")
    st.write(f"Analyzing ledger from **{start_dt.strftime('%b %d, %Y')}** to **{end_dt.strftime('%b %d, %Y')}**")
    
    # Calculate KPIs
    inc_df = filtered_df[filtered_df["Transaction_Type"] == "Income"]
    exp_df = filtered_df[filtered_df["Transaction_Type"] == "Expense"]
    
    total_income = inc_df["Amount"].sum()
    total_expense = exp_df["Amount"].sum()
    savings = total_income - total_expense
    savings_rate = (savings / total_income * 100) if total_income > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Income</div>
            <div class="metric-value-income">${total_income:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Expenses</div>
            <div class="metric-value-expense">${total_expense:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Net Savings</div>
            <div class="metric-value-savings">${savings:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Savings Rate</div>
            <div class="metric-value-percent">{savings_rate:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Monthly Income vs Expense Trend")
        monthly_trend = filtered_df.groupby([filtered_df["Date"].dt.to_period("M"), "Transaction_Type"])["Amount"].sum().unstack(fill_value=0).reset_index()
        monthly_trend["Date"] = monthly_trend["Date"].dt.to_timestamp()
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=monthly_trend["Date"], y=monthly_trend.get("Income", np.zeros(len(monthly_trend))), name="Income", line=dict(color="#00E676", width=3)))
        fig_trend.add_trace(go.Scatter(x=monthly_trend["Date"], y=monthly_trend.get("Expense", np.zeros(len(monthly_trend))), name="Expense", line=dict(color="#FF5252", width=3)))
        fig_trend.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#ECEFF1"),
            xaxis=dict(gridcolor="#30363D"),
            yaxis=dict(gridcolor="#30363D"),
            margin=dict(l=10, r=10, t=30, b=10)
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        
    with col_chart2:
        st.subheader("Expense Share by Category")
        category_spend = exp_df.groupby("Category")["Amount"].sum().reset_index()
        fig_pie = px.pie(
            category_spend, 
            values="Amount", 
            names="Category",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Dark24
        )
        fig_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            legend=dict(font=dict(color="#ECEFF1")),
            font=dict(color="#ECEFF1"),
            margin=dict(l=10, r=10, t=30, b=10)
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
    st.markdown("---")
    
    col_chart3, col_chart4 = st.columns(2)
    
    with col_chart3:
        st.subheader("Spending Concentration: Top 10 Merchants")
        merchant_spend = exp_df.groupby("Merchant")["Amount"].sum().reset_index().sort_values(by="Amount", ascending=False).head(10)
        fig_merch = px.bar(
            merchant_spend, 
            x="Amount", 
            y="Merchant", 
            orientation="h",
            color="Amount",
            color_continuous_scale="reds"
        )
        fig_merch.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#ECEFF1"),
            xaxis=dict(gridcolor="#30363D"),
            yaxis=dict(gridcolor="#30363D", categoryorder="total ascending"),
            margin=dict(l=10, r=10, t=30, b=10)
        )
        st.plotly_chart(fig_merch, use_container_width=True)
        
    with col_chart4:
        st.subheader("Cumulative Account Value Growth")
        fig_bal = px.area(
            filtered_df,
            x="Date",
            y="Running_Balance",
            color_discrete_sequence=["#29B6F6"]
        )
        fig_bal.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#ECEFF1"),
            xaxis=dict(gridcolor="#30363D"),
            yaxis=dict(gridcolor="#30363D"),
            margin=dict(l=10, r=10, t=30, b=10)
        )
        st.plotly_chart(fig_bal, use_container_width=True)

# -------------------------------------------------------------
# TAB 2: BUDGET PLANNER & OPTIMIZER
# -------------------------------------------------------------
with tab_budget:
    st.title("Budget Allocation & Recommender Engine")
    
    # Calculate average income from the customer ledger
    cust_df = df[df["Customer_ID"] == selected_customer]
    avg_monthly_income = cust_df[cust_df["Transaction_Type"] == "Income"].groupby(["Year", "Month"])["Amount"].sum().mean()
    if pd.isna(avg_monthly_income):
        avg_monthly_income = 5000.0
        
    st.subheader("Automated Monthly Budget Recommender")
    st.write(f"Based on historical data for **{selected_customer}**, your average monthly income is **${avg_monthly_income:,.2f}**.")
    
    user_income = st.number_input("Input Post-Tax Income ($) to calculate custom budgets", value=float(round(avg_monthly_income, 2)))
    
    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        st.info(f"**Needs / Essentials (50%)**\n\nAllocated: **${user_income * 0.50:,.2f}**\n\n*Covers: Rent, Groceries, Fuel, Utilities, Insurance.*")
    with col_b2:
        st.warning(f"**Wants / Discretionary (30%)**\n\nAllocated: **${user_income * 0.30:,.2f}**\n\n*Covers: Dining out, Travel, Shopping, Entertainment.*")
    with col_b3:
        st.success(f"**Savings & Investments (20%)**\n\nAllocated: **${user_income * 0.20:,.2f}**\n\n*Covers: Stock purchase, Mutual Fund SIP, Cash Savings.*")
        
    st.markdown("---")
    
    # Current month's utilization
    st.subheader("Active Category Budgets Utilization")
    latest_year = cust_df["Year"].max()
    latest_month = cust_df[cust_df["Year"] == latest_year]["Month"].max()
    
    month_exp = cust_df[(cust_df["Year"] == latest_year) & (cust_df["Month"] == latest_month) & (cust_df["Transaction_Type"] == "Expense")]
    month_budget_spend = month_exp.groupby("Budget_Category")["Amount"].sum().reset_index()
    
    from feature_engineering import BUDGET_LIMITS
    
    budget_comp = pd.DataFrame(list(BUDGET_LIMITS.items()), columns=["Budget_Category", "Limit"])
    budget_comp = budget_comp.merge(month_budget_spend, on="Budget_Category", how="left").fillna(0.0)
    budget_comp = budget_comp.rename(columns={"Amount": "Spent"})
    budget_comp["Utilization (%)"] = (budget_comp["Spent"] / budget_comp["Limit"] * 100).round(2)
    
    fig_bud = go.Figure()
    fig_bud.add_trace(go.Bar(
        y=budget_comp["Budget_Category"],
        x=budget_comp["Limit"],
        name="Limit",
        orientation="h",
        marker=dict(color="rgba(139, 148, 158, 0.3)")
    ))
    fig_bud.add_trace(go.Bar(
        y=budget_comp["Budget_Category"],
        x=budget_comp["Spent"],
        name="Actual Spend",
        orientation="h",
        marker=dict(color="#FF5252")
    ))
    fig_bud.update_layout(
        barmode='overlay',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#ECEFF1"),
        xaxis=dict(gridcolor="#30363D"),
        yaxis=dict(gridcolor="#30363D", categoryorder="total descending"),
        margin=dict(l=10, r=10, t=30, b=10)
    )
    st.plotly_chart(fig_bud, use_container_width=True)

# -------------------------------------------------------------
# TAB 3: MACHINE LEARNING PREDICTION & EXPLAINERS
# -------------------------------------------------------------
with tab_ml:
    st.title("Predictive Analytics & Model Explainers")
    
    col_ml1, col_ml2 = st.columns(2)
    
    with col_ml1:
        st.subheader("Monthly Spend Regression Forecast")
        st.write("Using our trained XGBoost Regressor to predict next month's spending based on historical rolling lags.")
        
        xgb_path = os.path.join(MODELS_DIR, "xgboost_model.joblib")
        if os.path.exists(xgb_path):
            xgbr = joblib.load(xgb_path)
            
            # Fetch last 3 months expenses for customer
            monthly_sums = cust_df[cust_df["Transaction_Type"] == "Expense"].groupby(["Year", "Month"])["Amount"].sum().reset_index()
            monthly_sums = monthly_sums.sort_values(by=["Year", "Month"]).reset_index(drop=True)
            
            if len(monthly_sums) >= 3:
                lag1 = monthly_sums.iloc[-1]["Amount"]
                lag2 = monthly_sums.iloc[-2]["Amount"]
                lag3 = monthly_sums.iloc[-3]["Amount"]
                roll_mean = np.mean([lag1, lag2, lag3])
                next_month = (datetime.now().month + 1) % 12 or 12
                
                input_df = pd.DataFrame([{
                    "Lag_1": lag1,
                    "Lag_2": lag2,
                    "Lag_3": lag3,
                    "Rolling_Mean_3M": roll_mean,
                    "Month_Num": next_month
                }])
                
                pred_val = xgbr.predict(input_df)[0]
                
                st.metric(
                    label=f"Predicted Spend for Month {next_month}",
                    value=f"${pred_val:,.2f}",
                    delta=f"{((pred_val - lag1)/lag1*100):+.1f}% vs last month"
                )
                
                st.markdown("**Historical Input Lags:**")
                st.write(f"- Month-1: **${lag1:,.2f}** | Month-2: **${lag2:,.2f}** | Month-3: **${lag3:,.2f}**")
                st.write(f"- Rolling 3-Month Mean: **${roll_mean:,.2f}**")
            else:
                st.warning("Insufficient historical transaction history to calculate lags.")
        else:
            st.error("Model files missing. Check pipeline status.")
            
    with col_ml2:
        st.subheader("Model Explainability (SHAP Values)")
        st.write("SHAP values explain how much each feature contributed to the XGBoost model's predicted output value.")
        if os.path.exists(SHAP_IMAGE_PATH):
            st.image(SHAP_IMAGE_PATH, caption="XGBoost SHAP Feature Importance Summary Plot")
        else:
            st.warning("SHAP summary plot image not found.")
            
    st.markdown("---")
    
    # Anomaly warnings
    st.subheader("Isolation Forest Anomaly Warnings")
    anom_tx = filtered_df[filtered_df["Anomaly_Flag"] == "Yes"]
    if not anom_tx.empty:
        st.warning(f"🚨 Isolation Forest flagged {len(anom_tx)} anomalous transactions in the selected date range:")
        st.dataframe(anom_tx[["Date", "Category", "Amount", "Merchant", "Description", "Notes"]], use_container_width=True)
    else:
        st.success("✅ No transactional anomalies detected in this ledger partition.")

# -------------------------------------------------------------
# TAB 4: FINANCIAL HEALTH METER
# -------------------------------------------------------------
with tab_health:
    st.title("Financial Health Meter & Runway Calculator")
    
    # overall metrics
    health_scores = filtered_df["Financial_Health_Score"].dropna()
    if not health_scores.empty:
        score = int(health_scores.iloc[-1])
    else:
        score = 50
        
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        st.subheader("Financial Health Meter")
        
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Health Score (0-100)"},
            gauge = {
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#ECEFF1"},
                'bar': {'color': "#00E676"},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 2,
                'bordercolor': "#30363D",
                'steps': [
                    {'range': [0, 50], 'color': '#FF5252'},
                    {'range': [50, 80], 'color': '#FFD700'},
                    {'range': [80, 100], 'color': '#00E676'}
                ],
            }
        ))
        fig_gauge.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#ECEFF1"),
            margin=dict(l=20, r=20, t=50, b=20)
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
        
    with col_h2:
        st.subheader("Emergency Runway Calculator")
        
        # Balance details
        current_bal = filtered_df["Running_Balance"].iloc[-1] if not filtered_df.empty else 1000.0
        avg_exp = filtered_df[filtered_df["Transaction_Type"] == "Expense"]["Amount"].sum() / 36.0 # over 3 years
        
        st.metric(
            label="Current Ledger Running Balance",
            value=f"${current_bal:,.2f}"
        )
        
        runway = current_bal / avg_exp if avg_exp > 0 else 0
        st.write(f"Your average monthly burn rate is **${avg_exp:,.2f}**.")
        st.write(f"Your emergency reserve represents **{runway:.1f} months** of expenses runway.")
        
        # Recommendations
        st.subheader("Actionable Recommendations")
        if score >= 80:
            st.success("🌟 Favorable portfolio allocation. Consider committing excess cash reserves to long-term brokerage assets.")
        elif score >= 50:
            st.warning("⚠️ Fair. Optimize want/discretionary categories to reach a 20%+ savings rate benchmark.")
        else:
            st.error("🚨 Low cash safety reserves. Implement immediate strict budget capping and construct a 3-month emergency fund.")
            
    st.subheader("Download Detailed Transaction Report")
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Partition CSV Report",
        data=csv_data,
        file_name="financial_ledger_report.csv",
        mime="text/csv"
    )

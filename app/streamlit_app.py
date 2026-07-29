import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "python"))

import joblib
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from config.settings import BUDGET_LIMITS, BUDGET_MAPPING, CUSTOMER_PROFILES

# Set page layout to wide and title
st.set_page_config(
    page_title="FinSense AI: Enterprise Indian Personal Finance Platform",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark glassmorphism styling and Outfit font
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
    /* Font style overrides */
    html, body, [class*="css"], .stMarkdown, p, span, label, td, th {
        font-family: 'Outfit', sans-serif !important;
    }
    .reportview-container, .main {
        background: #0d1117;
    }
    /* Glassmorphism card component */
    .metric-card {
        background: rgba(22, 27, 34, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: rgba(0, 230, 118, 0.4);
    }
    .metric-title {
        color: #8b949e;
        font-size: 14px;
        text-transform: uppercase;
        margin-bottom: 8px;
        font-weight: 600;
        letter-spacing: 0.8px;
    }
    .metric-value-income {
        color: #00E676;
        font-size: 32px;
        font-weight: 700;
        text-shadow: 0 0 10px rgba(0, 230, 118, 0.2);
    }
    .metric-value-expense {
        color: #FF5252;
        font-size: 32px;
        font-weight: 700;
        text-shadow: 0 0 10px rgba(255, 82, 82, 0.2);
    }
    .metric-value-savings {
        color: #29B6F6;
        font-size: 32px;
        font-weight: 700;
        text-shadow: 0 0 10px rgba(41, 182, 246, 0.2);
    }
    .metric-value-percent {
        color: #FFD700;
        font-size: 32px;
        font-weight: 700;
        text-shadow: 0 0 10px rgba(255, 215, 0, 0.2);
    }
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to get paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "transactions_processed.csv")
MODELS_DIR = os.path.join(BASE_DIR, "models")
SHAP_IMAGE_PATH = os.path.join(BASE_DIR, "images", "shap_summary.png")

def format_indian_currency(amount, show_decimals=False):
    """
    Formats numbers into the standard Indian numbering system (e.g. ₹1,50,000.00).
    """
    if amount is None or pd.isna(amount):
        return "₹0"
    sign = "-" if amount < 0 else ""
    amount = abs(amount)
    s = f"{amount:.2f}" if show_decimals else f"{amount:.0f}"
    parts = s.split(".")
    integer_part = parts[0]
    decimal_part = "." + parts[1] if len(parts) > 1 and show_decimals else ""
    
    if len(integer_part) <= 3:
        return f"{sign}₹{integer_part}{decimal_part}"
    
    last_three = integer_part[-3:]
    other_parts = integer_part[:-3]
    
    grouped = []
    while len(other_parts) > 0:
        grouped.append(other_parts[-2:])
        other_parts = other_parts[:-2]
    grouped.reverse()
    
    formatted = ",".join(grouped) + "," + last_three
    return f"{sign}₹{formatted}{decimal_part}"

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
st.sidebar.markdown("<h1 style='text-align: center; color: #00E676;'>💰 FinSense AI</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; color: #8b949e;'>AI-Powered Indian Personal Finance Platform</p>", unsafe_allow_html=True)
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

# Customer ID Selection with Indian Names Mapping
customers = sorted(df["Customer_ID"].dropna().unique().tolist())
customer_names = {k: f"{v['name']} ({v['occupation']})" for k, v in CUSTOMER_PROFILES.items()}

selected_customer = st.sidebar.selectbox(
    "Select Customer Profile",
    customers,
    format_func=lambda x: customer_names.get(x, x)
)

# Display Customer Profile Card
if selected_customer in CUSTOMER_PROFILES:
    prof = CUSTOMER_PROFILES[selected_customer]
    st.sidebar.markdown(f"""
    <div style="background: rgba(22, 27, 34, 0.65); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 16px; margin-bottom: 20px;">
        <h4 style="margin-top: 0; color: #00E676; font-size: 16px; margin-bottom: 8px;">👤 {prof['name']}</h4>
        <p style="margin: 4px 0; font-size: 13px; color: #ECEFF1;"><b>Age:</b> {prof['age']} | <b>City:</b> {prof['city']}</p>
        <p style="margin: 4px 0; font-size: 13px; color: #ECEFF1;"><b>Occupation:</b> {prof['occupation']}</p>
        <p style="margin: 4px 0; font-size: 13px; color: #ECEFF1;"><b>Monthly Income:</b> {format_indian_currency(prof['monthly_income'])}</p>
        <p style="margin: 4px 0; font-size: 13px; color: #ECEFF1;"><b>Credit Score:</b> <span style="color: #FFD700; font-weight: bold;">{prof['credit_score']}</span></p>
        <p style="margin: 4px 0; font-size: 13px; color: #ECEFF1;"><b>Risk Profile:</b> {prof['risk_profile']}</p>
        <p style="margin: 4px 0; font-size: 13px; color: #ECEFF1;"><b>Savings Goal:</b> {prof['savings_goal']}</p>
        <p style="margin: 4px 0; font-size: 13px; color: #ECEFF1;"><b>Investment Style:</b> {prof['investment_style']}</p>
        <p style="margin: 4px 0; font-size: 13px; color: #ECEFF1;"><b>Emergency Goal:</b> {format_indian_currency(prof['emergency_fund_goal'])}</p>
    </div>
    """, unsafe_allow_html=True)

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
tab_exec, tab_dash, tab_budget, tab_ml, tab_health = st.tabs([
    "👑 Executive Dashboard",
    "📊 Financial Analytics",
    "🎯 Budget Planner & Optimizer",
    "🔮 ML Prediction & Diagnostics",
    "🛡️ Financial Health Meter"
])

def render_kpi_card(title, current, previous, is_expense=False, is_percent=False):
    diff = current - previous
    pct = (diff / previous * 100) if previous > 0 else (100.0 if diff > 0 else 0.0)
    
    # Direction arrow and color
    if diff > 0:
        arrow = "↑"
        if is_expense:
            color = "#FF5252" # bad for expenses
            bg_color = "rgba(255, 82, 82, 0.1)"
        else:
            color = "#00E676" # good for income/savings
            bg_color = "rgba(0, 230, 118, 0.1)"
    elif diff < 0:
        arrow = "↓"
        if is_expense:
            color = "#00E676" # good for expenses
            bg_color = "rgba(0, 230, 118, 0.1)"
        else:
            color = "#FF5252" # bad for income/savings
            bg_color = "rgba(255, 82, 82, 0.1)"
    else:
        arrow = "→"
        color = "#8b949e"
        bg_color = "rgba(139, 148, 158, 0.1)"
        
    val_str = f"{current:.1f}%" if is_percent else format_indian_currency(current)
    diff_str = f"{abs(diff):.1f}%" if is_percent else format_indian_currency(abs(diff))
    pct_str = f"{pct:+.1f}%" if previous > 0 else "+100.0%" if diff > 0 else "0.0%"
    
    return f"""
    <div class="metric-card" style="border-left: 5px solid {color}; text-align: left; padding: 16px;">
        <div class="metric-title" style="margin-bottom: 4px; font-size: 12px; color: #8b949e;">{title}</div>
        <div style="font-size: 24px; font-weight: 700; color: #ffffff; margin-bottom: 8px;">{val_str}</div>
        <div style="font-size: 12px; font-weight: 600; color: {color}; background: {bg_color}; padding: 2px 6px; border-radius: 4px; display: inline-block;">
            {arrow} {diff_str} ({pct_str})
        </div>
    </div>
    """

# -------------------------------------------------------------
# TAB 1: EXECUTIVE DASHBOARD
# -------------------------------------------------------------
with tab_exec:
    st.title("👑 Executive Wealth Dashboard")
    st.write("Overview of latest monthly performance and portfolio health diagnostics.")
    
    # Calculate latest month and prior month for the selected customer
    cust_all_df = df[df["Customer_ID"] == selected_customer]
    latest_yr = cust_all_df["Year"].max()
    latest_m = cust_all_df[cust_all_df["Year"] == latest_yr]["Month"].max()
    
    # Current month data
    cur_m_df = cust_all_df[(cust_all_df["Year"] == latest_yr) & (cust_all_df["Month"] == latest_m)]
    cur_inc = cur_m_df[cur_m_df["Transaction_Type"] == "Income"]["Amount"].sum()
    cur_exp = cur_m_df[cur_m_df["Transaction_Type"] == "Expense"]["Amount"].sum()
    cur_sav = cur_inc - cur_exp
    cur_sav_rate = (cur_sav / cur_inc * 100) if cur_inc > 0 else 0
    
    # Prior month data
    if latest_m == 1:
        prev_m = 12
        prev_yr = latest_yr - 1
    else:
        prev_m = latest_m - 1
        prev_yr = latest_yr
        
    prev_m_df = cust_all_df[(cust_all_df["Year"] == prev_yr) & (cust_all_df["Month"] == prev_m)]
    prev_inc = prev_m_df[prev_m_df["Transaction_Type"] == "Income"]["Amount"].sum()
    prev_exp = prev_m_df[prev_m_df["Transaction_Type"] == "Expense"]["Amount"].sum()
    prev_sav = prev_inc - prev_exp
    prev_sav_rate = (prev_sav / prev_inc * 100) if prev_inc > 0 else 0
    
    # Render KPI grid for latest month
    col_k1, col_k2, col_k3, col_k4 = st.columns(4)
    with col_k1:
        st.markdown(render_kpi_card("Monthly Income", cur_inc, prev_inc), unsafe_allow_html=True)
    with col_k2:
        st.markdown(render_kpi_card("Monthly Expenses", cur_exp, prev_exp, is_expense=True), unsafe_allow_html=True)
    with col_k3:
        st.markdown(render_kpi_card("Net Savings", cur_sav, prev_sav), unsafe_allow_html=True)
    with col_k4:
        st.markdown(render_kpi_card("Savings Rate", cur_sav_rate, prev_sav_rate, is_percent=True), unsafe_allow_html=True)
        
    st.markdown("---")
    
    col_exec1, col_exec2 = st.columns([2, 1])
    
    with col_exec1:
        st.subheader("🎯 Executive Summary & Diagnostic Insights")
        
        # Determine dynamic summaries
        # 1. Largest Expense Category
        cur_expenses = cur_m_df[cur_m_df["Transaction_Type"] == "Expense"]
        if not cur_expenses.empty:
            cat_totals = cur_expenses.groupby("Category")["Amount"].sum().reset_index()
            largest_cat = cat_totals.sort_values(by="Amount", ascending=False).iloc[0]
            largest_exp_str = f"**{largest_cat['Category']}** ({format_indian_currency(largest_cat['Amount'])})"
        else:
            largest_exp_str = "None"
            
        # 2. Largest Saving Opportunity (discretionary)
        disc_exp = cur_expenses[cur_expenses["Expense_Tag"] == "Discretionary"]
        if not disc_exp.empty:
            disc_totals = disc_exp.groupby("Category")["Amount"].sum().reset_index()
            largest_disc = disc_totals.sort_values(by="Amount", ascending=False).iloc[0]
            largest_opp_str = f"**{largest_disc['Category']}** ({format_indian_currency(largest_disc['Amount'])})"
        else:
            largest_opp_str = "None"
            
        # 3. Budget limits exceeded
        exceeded = []
        for b_cat, limit in BUDGET_LIMITS.items():
            spent = cur_expenses[cur_expenses["Budget_Category"] == b_cat]["Amount"].sum()
            if spent > limit:
                exceeded.append(f"{b_cat} (₹{spent - limit:,.0f} over)")
        if exceeded:
            budget_str = f"⚠️ Overspent in: {', '.join(exceeded)}"
            budget_color = "#FF5252"
        else:
            budget_str = "✅ All budget limits successfully respected."
            budget_color = "#00E676"
            
        # 4. Top Recommendation
        wellness_list = cur_m_df["Financial_Wellness_Score"].dropna()
        well_score = int(wellness_list.iloc[-1]) if not wellness_list.empty else 75
        
        if well_score < 50:
            rec_str = "Emergency funds are low relative to burn rate. Immediately cap Discretionary shopping and dining."
        elif exceeded:
            rec_str = f"Your highest budget breach is in {exceeded[0].split()[0]}. Lower allocations here to restore net savings rate."
        else:
            rec_str = "Excellent financial posture! Set up automated investments for surplus cash into Equity Mutual Fund SIPs."
            
        # Build cards/layout for these
        st.markdown(f"""
        <div style="background: rgba(22, 27, 34, 0.5); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 20px;">
            <table style="width: 100%; border-collapse: collapse; color: #ECEFF1; font-size: 15px;">
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);">
                    <td style="padding: 12px; font-weight: bold; width: 35%;">Largest Expense Category</td>
                    <td style="padding: 12px; color: #FF5252;">{largest_exp_str}</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);">
                    <td style="padding: 12px; font-weight: bold;">Largest Saving Opportunity</td>
                    <td style="padding: 12px; color: #29B6F6;">{largest_opp_str}</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);">
                    <td style="padding: 12px; font-weight: bold;">Budget Thresholds Status</td>
                    <td style="padding: 12px; color: {budget_color}; font-weight: bold;">{budget_str}</td>
                </tr>
                <tr>
                    <td style="padding: 12px; font-weight: bold;">Top AI Diagnostic Recommendation</td>
                    <td style="padding: 12px; color: #00E676; font-weight: bold;">{rec_str}</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
    with col_exec2:
        st.subheader("💡 Quick Metrics & Activity")
        
        # Calculate quick statistics
        upi_tx = cur_m_df[cur_m_df["Payment_Mode"] == "UPI"].shape[0]
        total_tx = cur_m_df.shape[0]
        upi_ratio = (upi_tx / total_tx * 100) if total_tx > 0 else 0
        
        st.markdown(f"- **Total Monthly Transactions**: `{total_tx}` entries processed")
        st.markdown(f"- **UPI Payment Preference**: `{upi_ratio:.1f}%` of transaction count")
        
        # Average transaction value
        avg_txn_val = cur_m_df[cur_m_df["Transaction_Type"] == "Expense"]["Amount"].mean()
        st.markdown(f"- **Average Expense Value**: `{format_indian_currency(avg_txn_val)}` per transaction")
        
        # Recurring commitments ratio
        rec_commit = cur_expenses[cur_expenses["Recurring"] == "Yes"]["Amount"].sum()
        rec_ratio = (rec_commit / cur_exp * 100) if cur_exp > 0 else 0
        st.markdown(f"- **Fixed Commitments Ratio**: `{rec_ratio:.1f}%` of monthly expenses")

# -------------------------------------------------------------
# TAB 2: FINANCIAL ANALYTICS
# -------------------------------------------------------------
with tab_dash:
    st.title(f"Financial Insights: {customer_names.get(selected_customer, selected_customer)}")
    st.write(f"Analyzing ledger from **{start_dt.strftime('%b %d, %Y')}** to **{end_dt.strftime('%b %d, %Y')}**")
    
    # Calculate filtered KPIs
    inc_df = filtered_df[filtered_df["Transaction_Type"] == "Income"]
    exp_df = filtered_df[filtered_df["Transaction_Type"] == "Expense"]
    
    total_income = inc_df["Amount"].sum()
    total_expense = exp_df["Amount"].sum()
    savings = total_income - total_expense
    savings_rate = (savings / total_income * 100) if total_income > 0 else 0
    
    # Period-over-period (PoP) comparison
    range_days = (end_dt - start_dt).days
    prior_start = start_dt - timedelta(days=range_days)
    prior_end = start_dt - timedelta(days=1)
    
    prior_df = df[
        (df["Date"] >= prior_start) &
        (df["Date"] <= prior_end) &
        (df["Customer_ID"] == selected_customer)
    ]
    if selected_category != "All":
        prior_df = prior_df[prior_df["Category"] == selected_category]
    if selected_payment != "All":
        prior_df = prior_df[prior_df["Payment_Mode"] == selected_payment]
        
    prior_income = prior_df[prior_df["Transaction_Type"] == "Income"]["Amount"].sum()
    prior_expense = prior_df[prior_df["Transaction_Type"] == "Expense"]["Amount"].sum()
    prior_savings = prior_income - prior_expense
    prior_savings_rate = (prior_savings / prior_income * 100) if prior_income > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(render_kpi_card("Total Income", total_income, prior_income), unsafe_allow_html=True)
    with col2:
        st.markdown(render_kpi_card("Total Expenses", total_expense, prior_expense, is_expense=True), unsafe_allow_html=True)
    with col3:
        st.markdown(render_kpi_card("Net Savings", savings, prior_savings), unsafe_allow_html=True)
    with col4:
        st.markdown(render_kpi_card("Savings Rate", savings_rate, prior_savings_rate, is_percent=True), unsafe_allow_html=True)
        
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
            yaxis=dict(gridcolor="#30363D", title="Amount (₹)"),
            margin=dict(l=10, r=10, t=30, b=10)
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # Smart Chart Insight
        avg_monthly_exp = monthly_trend.get("Expense", pd.Series([0])).mean()
        st.info(f"💡 **Income/Expense Trend Insight**: Average monthly expense is **{format_indian_currency(avg_monthly_exp)}**. Income vs Expense trend reveals structural savings behavior.")
        
    with col_chart2:
        st.subheader("Expense Share by Category")
        category_spend = exp_df.groupby("Category")["Amount"].sum().reset_index()
        total_exp_val = category_spend["Amount"].sum()
        
        if total_exp_val > 0:
            category_spend["Share"] = category_spend["Amount"] / total_exp_val
            small_cats = category_spend[category_spend["Share"] < 0.03]
            large_cats = category_spend[category_spend["Share"] >= 0.03]
            if not small_cats.empty:
                others_amount = small_cats["Amount"].sum()
                others_row = pd.DataFrame([{"Category": "Others", "Amount": others_amount, "Share": others_amount / total_exp_val}])
                category_spend = pd.concat([large_cats, others_row], ignore_index=True)
                
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
        fig_pie.update_traces(texttemplate='%{percent:.1%}', textposition='inside')
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Smart Pie Insight
        if not category_spend.empty:
            top_cat = category_spend.sort_values(by="Amount", ascending=False).iloc[0]
            st.info(f"💡 **Category Share Insight**: **{top_cat['Category']}** is your largest spend pool, representing **{top_cat['Share']*100:.1f}%** of total expenses.")
        else:
            st.info("💡 **Category Share Insight**: No expenses recorded in the selected period.")
        
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
            xaxis=dict(gridcolor="#30363D", title="Spent (₹)"),
            yaxis=dict(gridcolor="#30363D", categoryorder="total ascending"),
            margin=dict(l=10, r=10, t=30, b=10)
        )
        st.plotly_chart(fig_merch, use_container_width=True)
        
        # Smart Merchant Insight
        top_merch_sum = merchant_spend["Amount"].sum()
        merch_share = (top_merch_sum / total_expense * 100) if total_expense > 0 else 0
        st.info(f"💡 **Merchant Concentration Insight**: Your top 10 merchants account for **{merch_share:.1f}%** of all expenses, representing high spending centralization.")
        
    with col_chart4:
        st.subheader("Cumulative Account Value Growth (INR)")
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
            yaxis=dict(gridcolor="#30363D", title="Running Balance (₹)"),
            margin=dict(l=10, r=10, t=30, b=10)
        )
        st.plotly_chart(fig_bal, use_container_width=True)
        
        # Smart Balance Insight
        bal_start = filtered_df["Running_Balance"].iloc[0] if not filtered_df.empty else 0
        bal_end = filtered_df["Running_Balance"].iloc[-1] if not filtered_df.empty else 0
        bal_change = bal_end - bal_start
        bal_pct = (bal_change / bal_start * 100) if bal_start > 0 else 0
        st.info(f"💡 **Running Balance Insight**: Balance changed from **{format_indian_currency(bal_start)}** to **{format_indian_currency(bal_end)}** ({bal_pct:+.1f}% change).")

# -------------------------------------------------------------
# TAB 2: BUDGET PLANNER & OPTIMIZER
# -------------------------------------------------------------
with tab_budget:
    st.title("Indian Budget Allocation & Optimizer")
    
    # Calculate average income from the customer ledger
    cust_df = df[df["Customer_ID"] == selected_customer]
    avg_monthly_income = cust_df[cust_df["Transaction_Type"] == "Income"].groupby(["Year", "Month"])["Amount"].sum().mean()
    if pd.isna(avg_monthly_income):
        avg_monthly_income = 100000.0
        
    st.subheader("Interactive 50-30-20 Budget Optimizer")
    st.write(f"Based on historical data, your average monthly income is **{format_indian_currency(avg_monthly_income)}**.")
    
    # User input variables for the interactive planner
    col_inp1, col_inp2 = st.columns(2)
    with col_inp1:
        user_income = st.number_input("Input Post-Tax Monthly Income (₹) to calculate custom budgets", value=float(round(avg_monthly_income, 2)))
        user_rent = st.number_input("Your Custom Monthly Rent / Housing Cost (₹)", value=float(round(user_income * 0.25, 2)))
    with col_inp2:
        savings_target_rate = st.slider("Target Monthly Savings Rate (%)", min_value=10, max_value=50, value=20)
        discretionary_rate = 100 - 50 - savings_target_rate # dynamic allocation
    
    st.markdown("##### Custom Recommended Allocations (INR)")
    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        st.info(f"**Needs / Essentials (50%)**\n\nAllocated: **{format_indian_currency(user_income * 0.50)}**\n\n*Covers: Housing (Rent: {format_indian_currency(user_rent)}), Groceries, Fuel, Utilities, Insurance, EMIs.*")
    with col_b2:
        st.warning(f"**Wants / Discretionary ({discretionary_rate}%)**\n\nAllocated: **{format_indian_currency(user_income * (discretionary_rate/100))}**\n\n*Covers: Dining out, Travel, Shopping, Entertainment.*")
    with col_b3:
        st.success(f"**Savings & Investments ({savings_target_rate}%)**\n\nAllocated: **{format_indian_currency(user_income * (savings_target_rate/100))}**\n\n*Covers: Stock investment, Mutual Fund SIP, Digital Gold, Emergency Fund.*")
        
    st.markdown("---")
    
    # Savings Goal Planner
    st.subheader("🎯 Interactive Savings Goal SIP Planner")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        goal_name = st.selectbox("Select Savings Goal Type", ["Dream Home Downpayment", "Luxury Car Purchase", "Higher Education Fund", "Emergency Contingency Fund", "Festival Travel Tour"])
        target_amount = st.number_input("Target Amount Required (₹)", value=1500000.0, step=50000.0)
        target_years = st.slider("Target Duration to Achieve Goal (Years)", min_value=1, max_value=25, value=5)
    with col_s2:
        asset_class = st.selectbox("Expected Investment Class (Returns)", ["Equity Mutual Fund SIP (~12% p.a.)", "Debt Fund / Fixed Deposit (~7% p.a.)", "Savings Bank Account (~4% p.a.)", "Custom Rate"])
        if asset_class == "Equity Mutual Fund SIP (~12% p.a.)":
            ror = 12.0
        elif asset_class == "Debt Fund / Fixed Deposit (~7% p.a.)":
            ror = 7.0
        elif asset_class == "Savings Bank Account (~4% p.a.)":
            ror = 4.0
        else:
            ror = st.number_input("Custom Annual Rate of Return (%)", value=10.0)
            
    # Calculate required monthly SIP: Target = PMT * (((1 + r/12)^(n*12) - 1) / (r/12))
    r_monthly = (ror / 100) / 12
    n_months = target_years * 12
    if r_monthly > 0:
        required_sip = target_amount * r_monthly / (((1 + r_monthly) ** n_months) - 1)
    else:
        required_sip = target_amount / n_months
        
    st.markdown(f"To reach your goal of **{format_indian_currency(target_amount)}** in **{target_years} years** at **{ror}% p.a.** return:")
    st.markdown(f"#### Required Monthly Investment: <span style='color:#00E676'>{format_indian_currency(required_sip)}</span> per month.", unsafe_allow_html=True)
    
    # Compare with actual monthly savings average
    avg_actual_savings = cust_df["Net_Savings"].mean()
    if pd.isna(avg_actual_savings):
        avg_actual_savings = 0.0
    st.write(f"Your historical average monthly net savings is **{format_indian_currency(avg_actual_savings)}**.")
    if avg_actual_savings >= required_sip:
        st.success("🎉 **Status: On Track!** Your historical savings rate covers this SIP requirement. Set up an auto-debit mutual fund SIP to lock it in.")
    else:
        diff = required_sip - avg_actual_savings
        st.error(f"⚠️ **Status: Underfunded!** You need to increase your monthly savings by **{format_indian_currency(diff)}** to meet this goal on time.")
        
    st.markdown("---")
    
    # Current month's utilization
    st.subheader("Active Category Budgets Utilization (Latest Month)")
    latest_year = cust_df["Year"].max()
    latest_month = cust_df[cust_df["Year"] == latest_year]["Month"].max()
    
    month_exp = cust_df[(cust_df["Year"] == latest_year) & (cust_df["Month"] == latest_month) & (cust_df["Transaction_Type"] == "Expense")]
    month_budget_spend = month_exp.groupby("Budget_Category")["Amount"].sum().reset_index()
    
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
        xaxis=dict(gridcolor="#30363D", title="Rupees (₹)"),
        yaxis=dict(gridcolor="#30363D", categoryorder="total ascending"),
        margin=dict(l=10, r=10, t=30, b=10)
    )
    st.plotly_chart(fig_bud, use_container_width=True)

# -------------------------------------------------------------
# TAB 3: MACHINE LEARNING PREDICTION & DIAGNOSTICS
# -------------------------------------------------------------
with tab_ml:
    st.title("Predictive Analytics & Model Explainers")
    
    col_ml1, col_ml2 = st.columns(2)
    
    # Load ML metadata
    metadata_path = os.path.join(MODELS_DIR, "ml_metadata.joblib")
    if os.path.exists(metadata_path):
        ml_metadata = joblib.load(metadata_path)
    else:
        ml_metadata = None
        
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
                
                # Confidence interval calculation
                conf_interval = 1.96 * (ml_metadata["residual_std"] if ml_metadata else 10000.0)
                conf_low = max(0.0, pred_val - conf_interval)
                conf_high = pred_val + conf_interval
                
                st.metric(
                    label=f"Predicted Spend for Month {next_month}",
                    value=format_indian_currency(pred_val),
                    delta=f"{((pred_val - lag1)/lag1*100):+.1f}% vs last month"
                )
                
                st.markdown(f"**95% Confidence Interval**: `{format_indian_currency(conf_low)}` to `{format_indian_currency(conf_high)}`")
                st.markdown("**Historical Input Lags:**")
                st.write(f"- Month-1: **{format_indian_currency(lag1)}** | Month-2: **{format_indian_currency(lag2)}** | Month-3: **{format_indian_currency(lag3)}**")
                st.write(f"- Rolling 3-Month Mean: **{format_indian_currency(roll_mean)}**")
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
    
    # Model evaluation metrics section
    st.subheader("Model Evaluation & Regression Diagnostics")
    if ml_metadata:
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown("##### Multi-Model Regression Performance")
            metrics_dict = ml_metadata["metrics"]
            metrics_df = pd.DataFrame(metrics_dict).T.reset_index().rename(columns={"index": "Model Name"})
            metrics_df["MAE"] = metrics_df["MAE"].apply(lambda x: format_indian_currency(x, show_decimals=True))
            metrics_df["RMSE"] = metrics_df["RMSE"].apply(lambda x: format_indian_currency(x, show_decimals=True))
            metrics_df["R2"] = metrics_df["R2"].round(4)
            st.dataframe(metrics_df, use_container_width=True)
            st.write(f"**XGBoost 5-Fold Cross Validation MAE**: `{format_indian_currency(ml_metadata['avg_cv_mae'], show_decimals=True)}`")
            
            # Feature Importance chart
            st.markdown("##### Feature Importance (Random Forest)")
            rf_imp = ml_metadata["feature_importances"]["Random Forest"]
            rf_imp_df = pd.DataFrame(list(rf_imp.items()), columns=["Feature", "Importance"]).sort_values(by="Importance", ascending=True)
            fig_imp = px.bar(rf_imp_df, x="Importance", y="Feature", orientation="h", color="Importance", color_continuous_scale="greens")
            fig_imp.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#ECEFF1"),
                xaxis=dict(gridcolor="#30363D"),
                yaxis=dict(gridcolor="#30363D"),
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig_imp, use_container_width=True)
            
        with col_m2:
            st.markdown("##### Predicted vs Actual Expenditure (Test Set)")
            actuals = ml_metadata["test_actuals"]
            preds_xgb = ml_metadata["test_predictions"]["XGBoost"]
            
            fig_pred_act = go.Figure()
            fig_pred_act.add_trace(go.Scatter(x=actuals, y=preds_xgb, mode='markers', name='XGBoost Predictions', marker=dict(color='#00E676', opacity=0.7)))
            min_val = min(min(actuals), min(preds_xgb))
            max_val = max(max(actuals), max(preds_xgb))
            fig_pred_act.add_trace(go.Scatter(x=[min_val, max_val], y=[min_val, max_val], mode='lines', name='Ideal Line (Identity)', line=dict(color='#FF5252', dash='dash')))
            fig_pred_act.update_layout(
                xaxis_title="Actual Spend (₹)",
                yaxis_title="Predicted Spend (₹)",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#ECEFF1"),
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig_pred_act, use_container_width=True)
            
            st.markdown("##### Regression Residual Variance")
            residuals = ml_metadata["residuals"]["XGBoost"]
            fig_res = go.Figure()
            fig_res.add_trace(go.Scatter(x=preds_xgb, y=residuals, mode='markers', name='Residuals', marker=dict(color='#29B6F6', opacity=0.7)))
            fig_res.add_trace(go.Scatter(x=[min_val, max_val], y=[0, 0], mode='lines', name='Zero Residual Line', line=dict(color='#8b949e', dash='dash')))
            fig_res.update_layout(
                xaxis_title="Predicted Spend (₹)",
                yaxis_title="Residual (₹)",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#ECEFF1"),
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig_res, use_container_width=True)
    else:
        st.warning("Model metadata diagnostics file not found. Run the pipeline to generate it.")
        
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
    st.title("Financial Health & Wellness Score")
    
    # Fetch financial wellness score from the ledger (computed per customer month)
    health_scores = filtered_df["Financial_Wellness_Score"].dropna()
    if not health_scores.empty:
        score = int(health_scores.iloc[-1])
    else:
        score = 50
        
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        st.subheader("Financial Health Meter Gauge")
        
        # Plotly indicator gauge with color zoning (Poor, Average, Good, Excellent)
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
                    {'range': [0, 40], 'color': '#FF5252'},      # Poor (Red)
                    {'range': [40, 70], 'color': '#FFA726'},     # Average (Orange)
                    {'range': [70, 90], 'color': '#FFD700'},     # Good (Yellow-Green)
                    {'range': [90, 100], 'color': '#00E676'}     # Excellent (Emerald Green)
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
        st.subheader("Emergency Runway & Burn Rate")
        
        # Balance details
        current_bal = filtered_df["Running_Balance"].iloc[-1] if not filtered_df.empty else 10000.0
        
        # calculate average monthly expense over selected date range
        num_months = max(1, (end_dt - start_dt).days // 30)
        total_exp_val = filtered_df[filtered_df["Transaction_Type"] == "Expense"]["Amount"].sum()
        avg_exp = total_exp_val / num_months
        
        st.metric(
            label="Current Ledger Running Balance",
            value=format_indian_currency(current_bal)
        )
        
        runway = current_bal / avg_exp if avg_exp > 0 else 0
        st.write(f"Your average monthly burn rate is **{format_indian_currency(avg_exp)}**.")
        st.write(f"Your emergency reserve represents **{runway:.1f} months** of expenses runway.")
        
        # Recommendations
        st.subheader("Actionable Recommendations")
        if score >= 80:
            st.success("🌟 **Favorable portfolio allocation!** Consider committing excess cash reserves to long-term stock brokerage portfolios or mutual fund SIPs.")
        elif score >= 50:
            st.warning("⚠️ **Fair financial position.** Optimize want/discretionary categories to reach a 20%+ savings rate benchmark.")
        else:
            st.error("🚨 **Low cash safety reserves.** Implement immediate strict budget capping and construct a 3-month emergency fund in high-yield liquid investments.")
            
    # Risk Indicators breakdown
    st.subheader("Portfolio Health Risk Diagnostics Breakdown")
    col_r1, col_r2, col_r3 = st.columns(3)
    
    with col_r1:
        # Savings Rate Risk
        st.markdown("##### Savings Rate Analysis")
        st.write(f"Latest Month Savings Rate: **{savings_rate:.1f}%**")
        if savings_rate >= 20.0:
            st.success("✅ Healthy savings buffer (> 20%). Keep accumulating.")
        else:
            st.error("❌ Underfunded savings buffer (< 20%). Automate salary deductions.")
            
    with col_r2:
        # Debt to income ratio
        st.markdown("##### Debt-to-Income Analysis")
        # Fetch latest month DTI ratio
        latest_dti_df = filtered_df["Debt_to_Income_Ratio"].dropna()
        latest_dti = latest_dti_df.iloc[-1] if not latest_dti_df.empty else 0.0
        st.write(f"Latest Month Debt-to-Income (DTI): **{latest_dti*100:.1f}%**")
        if latest_dti <= 0.40:
            st.success("✅ Manageable debt service obligations (< 40%).")
        else:
            st.error("❌ Heavy debt burden (> 40%). Refinance high-cost debt.")
            
    with col_r3:
        # Runway runway status
        st.markdown("##### Cash Runway Analysis")
        st.write(f"Current Reserve Safety Runway: **{runway:.1f} months**")
        if runway >= 3.0:
            st.success("✅ Secure runway (> 3 months expenses covered).")
        else:
            st.error("❌ Low cash runway (< 3 months). Halt luxury discretionary spend.")
            
    st.markdown("---")
    st.subheader("Download Detailed Transaction Report")
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Partition CSV Report",
        data=csv_data,
        file_name="financial_ledger_report.csv",
        mime="text/csv"
    )

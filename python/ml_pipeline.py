import os
import sys
import joblib
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Sklearn models and metrics
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Advanced ML
import xgboost as xgb
import shap

# Fallback forecast
from statsmodels.tsa.statespace.sarimax import SARIMAX

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings
from utils.logging_utils import get_logger

logger = get_logger("ml_pipeline")

def train_all_models():
    """
    ML training pipeline.
    Executes customer spending profiling, anomaly detection, regression, SHAP explanations,
    and Prophet time series forecasting (with SARIMAX fallback).
    """
    logger.info("Initializing Machine Learning Pipeline...")
    
    if not os.path.exists(settings.PROCESSED_DATA_PATH):
        raise FileNotFoundError(f"Processed CSV not found at {settings.PROCESSED_DATA_PATH}")
        
    df = pd.read_csv(settings.PROCESSED_DATA_PATH)
    df["Date"] = pd.to_datetime(df["Date"])
    
    # Ensure models and images directories exist
    os.makedirs(settings.MODELS_DIR, exist_ok=True)
    os.makedirs(os.path.join(settings.BASE_DIR, "images"), exist_ok=True)
    
    # -------------------------------------------------------------------------
    # 1. CLUSTERING: Customer/Monthly Spending Profiling (K-Means)
    # -------------------------------------------------------------------------
    logger.info("--- 1. Running K-Means Monthly Spending Clustering ---")
    # Group by customer and month/year to get category expense matrix
    monthly_cat = df[df["Transaction_Type"] == "Expense"].groupby(
        ["Customer_ID", "Year", "Month", "Category"]
    )["Amount"].sum().unstack(fill_value=0.0).reset_index()
    
    feature_cols = [c for c in monthly_cat.columns if c not in ["Customer_ID", "Year", "Month"]]
    X_clust = monthly_cat[feature_cols].copy()
    
    scaler = StandardScaler()
    X_clust_scaled = scaler.fit_transform(X_clust)
    
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_clust_scaled)
    monthly_cat["Cluster"] = clusters
    
    # Save models
    joblib.dump(kmeans, os.path.join(settings.MODELS_DIR, "kmeans_model.joblib"))
    joblib.dump(scaler, os.path.join(settings.MODELS_DIR, "kmeans_scaler.joblib"))
    logger.info("K-Means and Scaler saved.")
    
    # -------------------------------------------------------------------------
    # 2. ANOMALY DETECTION: Transaction-Level (Isolation Forest)
    # -------------------------------------------------------------------------
    logger.info("--- 2. Running Isolation Forest Anomaly Detection ---")
    # Features: Amount, Day, Month, and encoded Category/Payment
    le_cat = LabelEncoder()
    le_pay = LabelEncoder()
    
    df_iso = df.copy()
    df_iso["Cat_Encoded"] = le_cat.fit_transform(df_iso["Category"])
    df_iso["Pay_Encoded"] = le_pay.fit_transform(df_iso["Payment_Mode"])
    
    X_iso = df_iso[["Amount", "Month", "Day", "Cat_Encoded", "Pay_Encoded"]].copy()
    
    # Contamination rate at 1%
    iso_forest = IsolationForest(contamination=0.01, random_state=42)
    preds = iso_forest.fit_predict(X_iso)
    df["Anomaly_Flag"] = np.where(preds == -1, "Yes", "No")
    
    # Save anomaly model and encoders
    joblib.dump(iso_forest, os.path.join(settings.MODELS_DIR, "iso_forest_model.joblib"))
    joblib.dump(le_cat, os.path.join(settings.MODELS_DIR, "le_category.joblib"))
    joblib.dump(le_pay, os.path.join(settings.MODELS_DIR, "le_payment.joblib"))
    
    # Save df back with anomaly tag
    df.to_csv(settings.PROCESSED_DATA_PATH, index=False)
    logger.info("Isolation Forest completed and saved.")
    
    # -------------------------------------------------------------------------
    # 3. REGRESSION: Monthly Expenditures Forecast (LR, RF, XGBoost)
    # -------------------------------------------------------------------------
    logger.info("--- 3. Running Monthly Expenditure Regression ---")
    
    # Aggregate monthly spending per customer
    monthly_exp = df[df["Transaction_Type"] == "Expense"].groupby(["Customer_ID", "Year", "Month"])["Amount"].sum().reset_index()
    monthly_exp = monthly_exp.sort_values(by=["Customer_ID", "Year", "Month"]).reset_index(drop=True)
    
    # Add Lags
    monthly_exp["Lag_1"] = monthly_exp.groupby("Customer_ID")["Amount"].shift(1)
    monthly_exp["Lag_2"] = monthly_exp.groupby("Customer_ID")["Amount"].shift(2)
    monthly_exp["Lag_3"] = monthly_exp.groupby("Customer_ID")["Amount"].shift(3)
    
    monthly_exp["Rolling_Mean_3M"] = monthly_exp.groupby("Customer_ID")["Amount"].transform(
        lambda x: x.shift(1).rolling(window=3, min_periods=1).mean()
    )
    monthly_exp["Month_Num"] = monthly_exp["Month"]
    
    # Drop rows with NaN due to shift
    reg_data = monthly_exp.dropna().reset_index(drop=True)
    
    features = ["Lag_1", "Lag_2", "Lag_3", "Rolling_Mean_3M", "Month_Num"]
    X_reg = reg_data[features]
    y_reg = reg_data["Amount"]
    
    X_train, X_test, y_train, y_test = train_test_split(X_reg, y_reg, test_size=0.2, random_state=42)
    
    # Train Models
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    
    xgbr = xgb.XGBRegressor(n_estimators=100, random_state=42)
    xgbr.fit(X_train, y_train)
    
    # Evaluate
    models = {"Linear Regression": lr, "Random Forest": rf, "XGBoost": xgbr}
    metrics = {}
    
    for name, model in models.items():
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        metrics[name] = {"MAE": mae, "RMSE": rmse, "R2": r2}
        logger.info(f"{name} -> MAE: ${mae:.2f}, RMSE: ${rmse:.2f}, R2: {r2:.4f}")
        
    # K-Fold Cross Validation on XGBoost
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(xgbr, X_reg, y_reg, cv=kf, scoring="neg_mean_absolute_error")
    avg_cv_mae = -cv_scores.mean()
    logger.info(f"XGBoost 5-Fold CV MAE: ${avg_cv_mae:.2f}")
    
    # Feature Importances from Random Forest
    importances = rf.feature_importances_
    feat_imp = dict(zip(features, importances))
    
    # SHAP Explainability
    logger.info("Computing SHAP explanations...")
    explainer = shap.TreeExplainer(xgbr)
    shap_values = explainer(X_test)
    
    # Save SHAP Summary Plot
    plt.figure(figsize=(8, 5))
    shap.summary_plot(shap_values, X_test, show=False)
    plt.tight_layout()
    shap_img_path = os.path.join(settings.BASE_DIR, "images", "shap_summary.png")
    plt.savefig(shap_img_path)
    plt.close()
    logger.info(f"SHAP summary plot saved to {shap_img_path}")
    
    # Save Models
    joblib.dump(lr, os.path.join(settings.MODELS_DIR, "linear_regression_model.joblib"))
    joblib.dump(rf, os.path.join(settings.MODELS_DIR, "random_forest_model.joblib"))
    joblib.dump(xgbr, os.path.join(settings.MODELS_DIR, "xgboost_model.joblib"))
    
    # -------------------------------------------------------------------------
    # 4. FORECASTING: Time Series (Prophet with SARIMAX Fallback)
    # -------------------------------------------------------------------------
    logger.info("--- 4. Running Timeline Time Series Forecasting ---")
    daily_spend = df[df["Transaction_Type"] == "Expense"].groupby("Date")["Amount"].sum().reset_index()
    daily_spend = daily_spend.sort_values(by="Date").reset_index(drop=True)
    daily_spend.columns = ["ds", "y"]
    
    prophet_fit_success = False
    
    try:
        from prophet import Prophet
        logger.info("Attempting Prophet model fit...")
        model_prophet = Prophet(daily_seasonality=False, weekly_seasonality=True, yearly_seasonality=True)
        model_prophet.fit(daily_spend)
        
        future = model_prophet.make_future_dataframe(periods=30)
        forecast = model_prophet.predict(future)
        
        # Save Prophet
        joblib.dump(model_prophet, os.path.join(settings.MODELS_DIR, "prophet_model.joblib"))
        prophet_fit_success = True
        logger.info("Prophet forecasting model fitted and saved successfully.")
    except Exception as e:
        logger.warning(f"Prophet fitting failed: {e}. Falling back to Statsmodels SARIMAX model...")
        
    # Always fit SARIMAX as standard model / fallback
    daily_spend_idx = daily_spend.set_index("ds")
    daily_spend_idx.index = pd.DatetimeIndex(daily_spend_idx.index).to_period('D')
    
    sarimax_model = SARIMAX(daily_spend_idx["y"], order=(1, 1, 1), seasonal_order=(1, 1, 1, 7))
    sarimax_fit = sarimax_model.fit(disp=False)
    joblib.dump(sarimax_fit, os.path.join(settings.MODELS_DIR, "sarimax_model.joblib"))
    logger.info("SARIMAX forecasting model fitted and saved.")
    
    # 5. Generate Markdown Report
    ml_report_md = f"""# Machine Learning Engineering Report
**Generated**: {pd.Timestamp.now().strftime('%Y-%m-%d')}  

## 1. Regression Spending Forecasting Model
We trained models to predict next month's total customer spending based on 3 months of lags and monthly seasonality.

### Model Evaluation Results
| Model Name | Mean Absolute Error (MAE) | Root Mean Squared Error (RMSE) | R-squared ($R^2$) |
| :--- | :--- | :--- | :--- |
| **Linear Regression** | ${metrics['Linear Regression']['MAE']:.2f} | ${metrics['Linear Regression']['RMSE']:.2f} | {metrics['Linear Regression']['R2']:.4f} |
| **Random Forest** | ${metrics['Random Forest']['MAE']:.2f} | ${metrics['Random Forest']['RMSE']:.2f} | {metrics['Random Forest']['R2']:.4f} |
| **XGBoost** | ${metrics['XGBoost']['MAE']:.2f} | ${metrics['XGBoost']['RMSE']:.2f} | {metrics['XGBoost']['R2']:.4f} |

*   **XGBoost 5-Fold CV MAE**: `${avg_cv_mae:.2f}`

### Feature Importances (Random Forest)
{chr(10).join([f"*   **{k}**: {v*100:.2f}%" for k, v in sorted(feat_imp.items(), key=lambda item: item[1], reverse=True)])}

## 2. Customer Segmentation (K-Means)
Months were segmented into 3 spending profiles based on categories distribution.
*   **Cluster Sizes**: {list(monthly_cat['Cluster'].value_counts())}
*   **Models Saved**: `kmeans_model.joblib`, `kmeans_scaler.joblib`

## 3. Anomaly Detection (Isolation Forest)
*   **Contamination Rate**: `1.0%`
*   **Anomalous Transactions Detected**: `{len(df[df['Anomaly_Flag'] == 'Yes'])}`
*   **Model Saved**: `iso_forest_model.joblib`

## 4. Time Series Forecasting
*   **Prophet Integrated**: { 'Yes' if prophet_fit_success else 'No (Fitted Statsmodels SARIMAX fallback)' }
*   **SARIMAX Model Order**: `SARIMAX(1,1,1)x(1,1,1,7)`
"""
    with open(os.path.join(settings.REPORTS_DIR, "ml_report.md"), "w", encoding="utf-8") as f:
        f.write(ml_report_md)
    logger.info("Saved ML report to reports/ml_report.md")

if __name__ == "__main__":
    train_all_models()

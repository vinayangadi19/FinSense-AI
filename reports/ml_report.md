# Machine Learning Engineering Report
**Generated**: 2026-07-29  

## 1. Regression Spending Forecasting Model
We trained models to predict next month's total customer spending based on 3 months of lags and monthly seasonality.

### Model Evaluation Results
| Model Name | Mean Absolute Error (MAE) | Root Mean Squared Error (RMSE) | R-squared ($R^2$) |
| :--- | :--- | :--- | :--- |
| **Linear Regression** | $1257.08 | $1465.24 | -0.1447 |
| **Random Forest** | $1090.83 | $1330.52 | 0.0561 |
| **XGBoost** | $1285.33 | $1649.65 | -0.4509 |

*   **XGBoost 5-Fold CV MAE**: `$1410.18`

### Feature Importances (Random Forest)
*   **Rolling_Mean_3M**: 21.89%
*   **Lag_1**: 21.03%
*   **Lag_3**: 20.45%
*   **Lag_2**: 19.25%
*   **Month_Num**: 17.37%

## 2. Customer Segmentation (K-Means)
Months were segmented into 3 spending profiles based on categories distribution.
*   **Cluster Sizes**: [45, 34, 29]
*   **Models Saved**: `kmeans_model.joblib`, `kmeans_scaler.joblib`

## 3. Anomaly Detection (Isolation Forest)
*   **Contamination Rate**: `1.0%`
*   **Anomalous Transactions Detected**: `121`
*   **Model Saved**: `iso_forest_model.joblib`

## 4. Time Series Forecasting
*   **Prophet Integrated**: Yes
*   **SARIMAX Model Order**: `SARIMAX(1,1,1)x(1,1,1,7)`

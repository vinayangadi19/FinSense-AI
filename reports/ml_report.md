# Machine Learning Engineering Report
**Generated**: 2026-07-30  

## 1. Regression Spending Forecasting Model
We trained models to predict next month's total customer spending based on 3 months of lags and monthly seasonality.

### Model Evaluation Results
| Model Name | Mean Absolute Error (MAE) | Root Mean Squared Error (RMSE) | R-squared ($R^2$) |
| :--- | :--- | :--- | :--- |
| **Linear Regression** | ₹43320.77 | ₹72927.39 | 0.9394 |
| **Random Forest** | ₹36576.88 | ₹60625.53 | 0.9581 |
| **XGBoost** | ₹38090.14 | ₹63098.92 | 0.9546 |

*   **XGBoost 5-Fold CV MAE**: `₹58004.10`

### Feature Importances (Random Forest)
*   **Rolling_Mean_3M**: 33.22%
*   **Lag_1**: 31.17%
*   **Lag_3**: 20.10%
*   **Lag_2**: 14.72%
*   **Month_Num**: 0.78%

## 2. Customer Segmentation (K-Means)
Months were segmented into 3 spending profiles based on categories distribution.
*   **Cluster Sizes**: [108, 38, 34]
*   **Models Saved**: `kmeans_model.joblib`, `kmeans_scaler.joblib`

## 3. Anomaly Detection (Isolation Forest)
*   **Contamination Rate**: `1.0%`
*   **Anomalous Transactions Detected**: `123`
*   **Model Saved**: `iso_forest_model.joblib`

## 4. Time Series Forecasting
*   **Prophet Integrated**: Yes
*   **SARIMAX Model Order**: `SARIMAX(1,1,1)x(1,1,1,7)`

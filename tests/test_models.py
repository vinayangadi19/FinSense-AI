import pytest
import os
import joblib
import numpy as np
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings

def test_models_exist():
    """
    Checks if all serialized joblib files exist.
    """
    model_files = [
        "kmeans_model.joblib",
        "kmeans_scaler.joblib",
        "iso_forest_model.joblib",
        "xgboost_model.joblib",
        "sarimax_model.joblib"
    ]
    for m in model_files:
        path = os.path.join(settings.MODELS_DIR, m)
        assert os.path.exists(path), f"Model file {m} missing from {settings.MODELS_DIR}"

def test_kmeans_prediction():
    """
    Validates KMeans model can load and predict.
    """
    kmeans_path = os.path.join(settings.MODELS_DIR, "kmeans_model.joblib")
    scaler_path = os.path.join(settings.MODELS_DIR, "kmeans_scaler.joblib")
    
    kmeans = joblib.load(kmeans_path)
    scaler = joblib.load(scaler_path)
    
    # Use n_features_in_ dynamically
    num_features = scaler.n_features_in_
    dummy_input = np.random.uniform(0, 1000, size=(1, num_features))
    scaled_input = scaler.transform(dummy_input)
    cluster = kmeans.predict(scaled_input)
    
    assert len(cluster) == 1
    assert cluster[0] in [0, 1, 2]


def test_iso_forest_prediction():
    """
    Validates Isolation Forest model can predict.
    """
    iso_path = os.path.join(settings.MODELS_DIR, "iso_forest_model.joblib")
    iso = joblib.load(iso_path)
    
    # Features: Amount, Month, Day, Cat_Encoded, Pay_Encoded
    dummy_input = np.array([[200.0, 5, 12, 3, 2]])
    pred = iso.predict(dummy_input)
    
    assert len(pred) == 1
    assert pred[0] in [1, -1]

def test_xgboost_prediction():
    """
    Validates XGBoost forecasting regression can predict.
    """
    xgb_path = os.path.join(settings.MODELS_DIR, "xgboost_model.joblib")
    xgbr = joblib.load(xgb_path)
    
    # Features: Lag_1, Lag_2, Lag_3, Rolling_Mean_3M, Month_Num
    dummy_input = np.array([[4500.0, 4200.0, 4800.0, 4500.0, 6]])
    pred = xgbr.predict(dummy_input)
    
    assert len(pred) == 1
    assert pred[0] > 0

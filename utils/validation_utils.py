import os
import pandas as pd
import numpy as np
from datetime import datetime
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings
from utils.logging_utils import get_logger

logger = get_logger("data_validator")

class DataValidator:
    """
    Validates transactional datasets, flags anomalous entries, and generates validation reports.
    """
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.report_stats = {}
        
    def validate_all(self) -> dict:
        """
        Runs all validation steps and updates report stats.
        """
        logger.info("Executing comprehensive data validation checks...")
        
        # 1. Total records
        total_records = len(self.df)
        self.report_stats["total_records"] = total_records
        
        # 2. Duplicate records count
        duplicates = self.df.duplicated(subset=["Transaction_ID"]).sum()
        self.report_stats["duplicate_transaction_ids"] = int(duplicates)
        
        # 3. Missing values count
        missing_vals = self.df.isnull().sum().to_dict()
        self.report_stats["missing_values"] = {k: int(v) for k, v in missing_vals.items() if v > 0}
        
        # 4. Future dates validation
        self.df["Parsed_Date"] = pd.to_datetime(self.df["Date"], errors='coerce')
        future_dates = (self.df["Parsed_Date"] > datetime.now()).sum()
        self.report_stats["future_dates_count"] = int(future_dates)
        
        # 5. Invalid payment methods
        valid_payments = set(settings.PAYMENT_MODES)
        invalid_payment_count = (~self.df["Payment_Mode"].isin(valid_payments)).sum()
        self.report_stats["invalid_payment_modes"] = int(invalid_payment_count)
        
        # 6. Invalid transaction types
        invalid_type_count = (~self.df["Transaction_Type"].isin(["Income", "Expense"])).sum()
        self.report_stats["invalid_transaction_types"] = int(invalid_type_count)
        
        # 7. Invalid amounts (negative or zero)
        invalid_amount_count = (self.df["Amount"] <= 0).sum()
        self.report_stats["invalid_amounts"] = int(invalid_amount_count)
        
        # 8. Currency validation
        invalid_currency_count = (self.df["Currency"] != settings.CURRENCY).sum()
        self.report_stats["invalid_currency"] = int(invalid_currency_count)
        
        # 9. Invalid categories
        # Let's verify against standard categories in config mapping
        all_cats = set(settings.ALL_CATEGORIES.keys())
        invalid_cat_count = (~self.df["Category"].isin(all_cats)).sum()
        self.report_stats["invalid_categories"] = int(invalid_cat_count)
        
        # 10. Outlier detection using IQR
        expenses = self.df[self.df["Transaction_Type"] == "Expense"]
        if not expenses.empty:
            q1 = expenses["Amount"].quantile(0.25)
            q3 = expenses["Amount"].quantile(0.75)
            iqr = q3 - q1
            outlier_threshold = q3 + (3 * iqr)
            outliers = (expenses["Amount"] > outlier_threshold).sum()
            self.report_stats["outliers_count"] = int(outliers)
            self.report_stats["outlier_threshold"] = float(round(outlier_threshold, 2))
        else:
            self.report_stats["outliers_count"] = 0
            self.report_stats["outlier_threshold"] = 0.0
            
        # 11. Calculate Data Quality Score (0 - 100)
        # Score factors: deduplication, amount correctness, valid categories, types and dates
        failures = (
            duplicates +
            invalid_amount_count +
            invalid_cat_count +
            invalid_type_count +
            future_dates +
            invalid_payment_count
        )
        quality_score = max(0, 100 * (1 - (failures / (total_records * 6 if total_records > 0 else 1))))
        self.report_stats["data_quality_score"] = float(round(quality_score, 2))
        
        logger.info(f"Validation completed. Data Quality Score: {self.report_stats['data_quality_score']}%")
        return self.report_stats

    def generate_report(self) -> str:
        """
        Creates a markdown report string.
        """
        stats = self.report_stats
        if not stats:
            self.validate_all()
            stats = self.report_stats
            
        report_md = f"""# Automated Data Validation Report
**Run Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  

## Summary
*   **Overall Data Quality Score**: `{stats['data_quality_score']}%`
*   **Total Records Analyzed**: `{stats['total_records']:,}`

## Validation Check List
| Check Type | Target Standard | Status | Discrepancies Flagged |
| :--- | :--- | :--- | :--- |
| **Transaction ID Duplication** | Unique values only | {"✅ PASS" if stats['duplicate_transaction_ids'] == 0 else "⚠️ WARN"} | {stats['duplicate_transaction_ids']} |
| **Missing Critical Values** | Zero nulls in key cols | {"✅ PASS" if not stats['missing_values'] else "⚠️ WARN"} | {sum(stats['missing_values'].values())} fields null |
| **Future Transactions** | Dates <= today | {"✅ PASS" if stats['future_dates_count'] == 0 else "⚠️ WARN"} | {stats['future_dates_count']} |
| **Valid Categories** | Aligns with settings mappings | {"✅ PASS" if stats['invalid_categories'] == 0 else "⚠️ WARN"} | {stats['invalid_categories']} |
| **Amount Integrity** | Positive non-zero numbers | {"✅ PASS" if stats['invalid_amounts'] == 0 else "❌ FAIL"} | {stats['invalid_amounts']} |
| **Transaction Type** | 'Income' or 'Expense' only | {"✅ PASS" if stats['invalid_transaction_types'] == 0 else "❌ FAIL"} | {stats['invalid_transaction_types']} |
| **Payment Mode Validation** | Aligns with settings list | {"✅ PASS" if stats['invalid_payment_modes'] == 0 else "⚠️ WARN"} | {stats['invalid_payment_modes']} |
| **Currency Consistency** | USD only | {"✅ PASS" if stats['invalid_currency'] == 0 else "⚠️ WARN"} | {stats['invalid_currency']} |

## Statistical Outliers
*   **Identified Expense Outliers**: `{stats['outliers_count']}` (Transactions exceeding IQR threshold of **${stats['outlier_threshold']:.2f}**)

---
*Report generated programmatically by the Personal Finance Analytics pipeline.*
"""
        return report_md

    def save_report(self):
        """
        Saves the validation report as reports/validation_report.md
        """
        report_content = self.generate_report()
        report_path = os.path.join(settings.REPORTS_DIR, "validation_report.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        logger.info(f"Saved validation report to {report_path}")

# Automated Data Validation Report
**Run Date**: 2026-07-30 00:01:36  

## Summary
*   **Overall Data Quality Score**: `99.93%`
*   **Total Records Analyzed**: `12,500`

## Validation Check List
| Check Type | Target Standard | Status | Discrepancies Flagged |
| :--- | :--- | :--- | :--- |
| **Transaction ID Duplication** | Unique values only | ✅ PASS | 0 |
| **Missing Critical Values** | Zero nulls in key cols | ⚠️ WARN | 12620 fields null |
| **Future Transactions** | Dates <= today | ✅ PASS | 0 |
| **Valid Categories** | Aligns with settings mappings | ⚠️ WARN | 46 |
| **Amount Integrity** | Positive non-zero numbers | ❌ FAIL | 5 |
| **Transaction Type** | 'Income' or 'Expense' only | ✅ PASS | 0 |
| **Payment Mode Validation** | Aligns with settings list | ✅ PASS | 0 |
| **Currency Consistency** | INR only | ✅ PASS | 0 |

## Statistical Outliers
*   **Identified Expense Outliers**: `965` (Transactions exceeding IQR threshold of **₹16560.70**)

---
*Report generated programmatically by the Personal Finance Analytics pipeline.*

import pytest
import sqlite3
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings

def test_database_connection():
    """
    Checks if database file exists and is readable.
    """
    assert os.path.exists(settings.DATABASE_PATH), f"Database not found at {settings.DATABASE_PATH}"
    
    conn = sqlite3.connect(settings.DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    conn.close()
    
    expected_tables = ["dim_customer", "dim_date", "dim_merchant", "dim_payment", "dim_category", "dim_geography", "fact_transactions"]
    for tab in expected_tables:
        assert tab in tables, f"Expected table {tab} missing from SQLite database"

def test_dimensions_seeding():
    """
    Ensures dimensions table are not empty.
    """
    conn = sqlite3.connect(settings.DATABASE_PATH)
    cursor = conn.cursor()
    
    tables = ["dim_customer", "dim_date", "dim_merchant", "dim_payment", "dim_category", "dim_geography", "fact_transactions"]
    for tab in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {tab}")
        cnt = cursor.fetchone()[0]
        assert cnt > 0, f"Table {tab} is empty!"
        
    conn.close()

def test_views_queryable():
    """
    Checks if analytics views are queryable.
    """
    conn = sqlite3.connect(settings.DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM view_monthly_wallet_summary LIMIT 5")
    rows = cursor.fetchall()
    assert len(rows) > 0, "view_monthly_wallet_summary returned 0 rows"
    
    conn.close()

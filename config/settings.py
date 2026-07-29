import os

# Project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# File paths config
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_PATH = os.path.join(DATA_DIR, "raw", "transactions_raw.csv")
PROCESSED_DATA_PATH = os.path.join(DATA_DIR, "processed", "transactions_processed.csv")
DATABASE_PATH = os.path.join(BASE_DIR, "database", "personal_finance.db")
MODELS_DIR = os.path.join(BASE_DIR, "models")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

# Logging setup config
LOG_FILE_PATH = os.path.join(LOGS_DIR, "pipeline.log")

# Category and Sub-category maps (Indianized)
INCOME_CATEGORIES = {
    "Salary": ["Tech Corp Salary", "Monthly Paycheck", "Part-Time Paycheck"],
    "Freelancing": ["Web Development", "Data Analysis Consulting", "UI Design Project", "Content Writing"],
    "Investment": ["Mutual Fund Payout", "Stock Dividend", "Crypto Staking Reward"],
    "Interest": ["Savings Account Interest", "Fixed Deposit Interest"],
    "Bonus": ["Annual Performance Bonus", "Festival Bonus", "Sign-on Bonus"],
    "Rental Income": ["Apartment Rental", "Commercial Space Rental"],
    "Refund": ["Store Refund", "Tax Refund", "Subscription Reimbursement"],
    "Gift": ["Festival Gift Cash", "Birthday Gift Cash", "Family Support"]
}

EXPENSE_CATEGORIES = {
    "Rent": ["Apartment Rent", "PG Rent", "Office Rent"],
    "Food": ["Zomato Order", "Swiggy Order", "Restaurant Dining", "Coffee Shops"],
    "Groceries": ["DMart Groceries", "Reliance Fresh Groceries", "BigBasket Delivery", "Blinkit", "Zepto"],
    "Vegetables": ["Local Market Vegetables", "Online Vegetable Order"],
    "Milk": ["Daily Milk Delivery", "Milk Packets"],
    "Fuel": ["Petrol (Indian Oil)", "HP Petrol Pump", "Bharat Petroleum"],
    "Electricity": ["Monthly Electricity Bill"],
    "Water Bill": ["Water Tanker Bill", "Municipal Water Supply Bill"],
    "Broadband": ["Airtel Fiber Broadband", "JioFiber Broadband"],
    "Mobile Recharge": ["Airtel Prepaid Recharge", "Jio Prepaid Recharge", "Vi Prepaid Recharge"],
    "UPI Payments": ["PhonePe UPI Transfer", "Google Pay UPI Transfer", "Paytm UPI Transfer"],
    "EMI": ["Home Loan EMI", "Car Loan EMI", "Personal Loan EMI"],
    "Credit Card": ["HDFC Credit Card Bill", "ICICI Credit Card Bill", "SBI Credit Card Bill"],
    "Insurance": ["LIC Premium", "Health Insurance Premium"],
    "Medical": ["Apollo Pharmacy Purchase", "MedPlus Medicine", "Doctor Consultation"],
    "Education": ["School Fee", "College Tuition", "Online Course Fee"],
    "Travel": ["IRCTC Train Booking", "Ola Ride", "Uber Ride India", "Indigo Flight Booking"],
    "Dining": ["Swiggy Delivery", "Zomato Order", "Restaurant Dinner Bill"],
    "Shopping": ["Flipkart Shopping", "Amazon India Shopping", "Myntra Clothing", "Ajio Fashion"],
    "Entertainment": ["BookMyShow Tickets", "Netflix India Subscription", "Amazon Prime India Subscription"],
    "Investments": ["Groww Investment Mutual Fund", "Zerodha Stock Investment", "Gold Bond Investment"],
    "Mutual Fund SIP": ["HDFC Mutual Fund SIP", "ICICI Prudential Mutual Fund SIP"],
    "Gold": ["Gold Jewelry Purchase", "Digital Gold"],
    "Emergency Fund": ["Emergency Reserve Deposit"],
    "Taxes": ["Income Tax e-Filing", "GST Payment"],
    "Miscellaneous": ["Cash Withdrawal", "Bank Maintenance Fees", "Charitable Donations", "Unexpected Legal Fees"]
}

ALL_CATEGORIES = {**INCOME_CATEGORIES, **EXPENSE_CATEGORIES}

# Merchants mapping by Category (Indianized)
MERCHANTS = {
    # Income
    "Salary": ["TCS", "Infosys", "Wipro", "HDFC Bank", "ICICI Bank", "Reliance Industries"],
    "Freelancing": ["Upwork Client", "Fiverr Client", "Direct Consulting Project"],
    "Investment": ["Zerodha Dividends", "Groww Mutual Fund Payout", "Angel One Payout"],
    "Interest": ["SBI Fixed Deposit Interest", "HDFC Savings Interest", "ICICI Interest Credit"],
    "Bonus": ["Annual Corporate Bonus", "Festival Performance Bonus", "Spot Recognition Pay"],
    "Rental Income": ["Residential Rent Credit", "Commercial Lease Payment"],
    "Refund": ["Amazon India Refund", "Flipkart Return Credit", "Paytm Cash Wallet Refund"],
    "Gift": ["Diwali Cash Gift", "Family Support Transfer"],
    
    # Expense
    "Rent": ["Local Landlord Deposit", "PG Accomodation Rent", "NestAway Rental"],
    "Food": ["Zomato Order", "Swiggy Order", "McDonalds India", "Dominos Pizza", "Local Restaurant Dining"],
    "Groceries": ["DMart Supermarket", "Reliance Fresh", "BigBasket Online", "Blinkit Delivery", "Zepto Grocery"],
    "Vegetables": ["Local Mandi Vendor", "Reliance Smart Market", "Blinkit Vegetables"],
    "Milk": ["Country Delight Delivery", "Amul Milk Parlour", "Mother Dairy Cabin"],
    "Fuel": ["Indian Oil Petrol Pump", "HP Petrol Station", "Bharat Petroleum Outlet"],
    "Electricity": ["TATA Power Bill", "BESCOM Bill", "MSEDCL Bill", "Adani Electricity Payment"],
    "Water Bill": ["Local Water Tanker Service", "Municipal Corporation Water Bill"],
    "Broadband": ["Airtel Xtream Fiber", "JioFiber Broadband", "ACT Fibernet Subscription"],
    "Mobile Recharge": ["Jio Prepaid Recharge", "Airtel Mobile Recharge", "Vi Prepaid Bill"],
    "UPI Payments": ["PhonePe Money Transfer", "Google Pay P2P Transfer", "Paytm UPI Pay"],
    "EMI": ["HDFC Housing Loan EMI", "ICICI Car Loan EMI", "SBI Personal Loan EMI"],
    "Credit Card": ["HDFC Credit Card Settlement", "SBI Card Bill Payment", "Axis Credit Card Pay"],
    "Insurance": ["LIC Annual Premium Payment", "HDFC ERGO Health Insurance", "ICICI Lombard Auto Policy"],
    "Medical": ["Apollo Pharmacy Medicines", "MedPlus Pharmacy", "Local Clinic Consultation", "Fortis Hospital Bill"],
    "Education": ["KV School Term Fee", "Manipal University Tuition", "Udemy Technical Course", "Coursera Certificate"],
    "Travel": ["IRCTC Ticket Booking", "Ola Cabs Ride", "Uber India Cab", "IndiGo Flight Booking", "RedBus Ticket"],
    "Dining": ["Swiggy Delivery", "Zomato Order", "Restaurant Dinner Bill"],
    "Shopping": ["Amazon India Shopping", "Flipkart Online Sale", "Myntra Apparel Purchase", "Ajio Fashion Cart", "Reliance Digital Electronics"],
    "Entertainment": ["BookMyShow Cinema Tickets", "Netflix India Plan", "Amazon Prime Video Subscription", "Disney+ Hotstar Subscription"],
    "Investments": ["Groww Direct Mutual Fund", "Zerodha Equity Purchase", "SBI Gold Bond Scheme"],
    "Mutual Fund SIP": ["HDFC Index Fund SIP", "ICICI Prudential Bluechip SIP", "Nippon India Small Cap SIP"],
    "Gold": ["Tanishq Jewelers Purchase", "Digital Gold Accumulation", "MMTC-PAMP Gold Coin"],
    "Emergency Fund": ["HDFC Liquid Fund Deposit", "SBI Emergency Fund Savings Account"],
    "Taxes": ["Income Tax e-Filing Portal", "GSTIN Quarterly Returns Payment"],
    "Miscellaneous": ["HDFC ATM Cash Withdrawal", "Bank Maintenance Charge", "PM Cares Fund Donation"]
}

# Account configurations
ACCOUNT_TYPES = ["Savings Account", "Current Account", "Credit Card"]
PAYMENT_MODES = ["Credit Card", "Debit Card", "Net Banking", "UPI", "Cash"]
CURRENCY = "INR"

# Geographical data coordinates mapped by City, State, Country
GEOGRAPHY = {
    "Mumbai": {"state": "MH", "country": "India", "lat": (19.0760, 0.05), "lon": (72.8777, 0.05)},
    "Delhi": {"state": "DL", "country": "India", "lat": (28.7041, 0.04), "lon": (77.1025, 0.04)},
    "Bangalore": {"state": "KA", "country": "India", "lat": (12.9716, 0.04), "lon": (77.5946, 0.04)},
    "Hyderabad": {"state": "TG", "country": "India", "lat": (17.3850, 0.03), "lon": (78.4867, 0.03)},
    "Chennai": {"state": "TN", "country": "India", "lat": (13.0827, 0.04), "lon": (80.2707, 0.04)},
    "Kolkata": {"state": "WB", "country": "India", "lat": (22.5726, 0.03), "lon": (88.3639, 0.03)},
    "Pune": {"state": "MH", "country": "India", "lat": (18.5204, 0.03), "lon": (73.8567, 0.03)},
    "Ahmedabad": {"state": "GJ", "country": "India", "lat": (23.0225, 0.03), "lon": (72.5714, 0.03)}
}

# Standard Budget Limits in INR
BUDGET_LIMITS = {
    "Housing": 30000.0,
    "Food & Dining": 15000.0,
    "Groceries": 12000.0,
    "Transportation": 8000.0,
    "Shopping": 10000.0,
    "Healthcare": 5000.0,
    "Insurance & Taxes": 15000.0,
    "Utilities": 8000.0,
    "Entertainment": 8000.0,
    "Travel": 15000.0,
    "Education & Self-Care": 10000.0,
    "Debt Service": 25000.0,
    "Investments & Savings": 40000.0,
    "Miscellaneous": 5000.0
}

# Budget Categories Mapping
BUDGET_MAPPING = {
    "Rent": "Housing", "Food": "Food & Dining", "Groceries": "Groceries",
    "Vegetables": "Groceries", "Milk": "Groceries", "Fuel": "Transportation",
    "Transport": "Transportation", "Shopping": "Shopping", "Healthcare": "Healthcare",
    "Insurance": "Insurance & Taxes", "Electricity": "Utilities", "Water Bill": "Utilities",
    "Internet": "Utilities", "Broadband": "Utilities", "Mobile Recharge": "Utilities",
    "Entertainment": "Entertainment", "Subscriptions": "Entertainment", "Travel": "Travel",
    "Education": "Education & Self-Care", "EMI": "Debt Service", "Credit Card": "Debt Service",
    "Investment": "Investments & Savings", "Investments": "Investments & Savings",
    "Mutual Fund SIP": "Investments & Savings", "Gold": "Investments & Savings",
    "Emergency Fund": "Investments & Savings", "Taxes": "Insurance & Taxes",
    "UPI Payments": "Miscellaneous", "Miscellaneous": "Miscellaneous",
    "Salary": "Income", "Freelancing": "Income", "Investment (Income)": "Income",
    "Interest": "Income", "Bonus": "Income", "Rental Income": "Income",
    "Refund": "Income", "Gift": "Income"
}

# Ensure directories exist
for folder in [DATA_DIR, os.path.join(DATA_DIR, "raw"), os.path.join(DATA_DIR, "processed"),
               os.path.join(DATA_DIR, "external"), os.path.join(DATA_DIR, "archive"),
               MODELS_DIR, LOGS_DIR, REPORTS_DIR, os.path.dirname(DATABASE_PATH)]:
    os.makedirs(folder, exist_ok=True)

# Detailed Customer Profiles for FinSense AI
CUSTOMER_PROFILES = {
    "CUST-1001": {
        "name": "Rohan Mehta",
        "age": 21,
        "occupation": "Student",
        "city": "Pune",
        "monthly_income": 30000.0,
        "risk_profile": "High",
        "savings_goal": "Higher Education Fees",
        "investment_style": "Aggressive (Equity, Cryptos)",
        "credit_score": 680,
        "emergency_fund_goal": 50000.0,
        "salary_merchant": "Direct Consulting Project",
        "salary_category": "Freelancing",
        "salary_sub_category": "Web Development",
        "rent_amount": 8000.0,
        "sip_amount": 5000.0
    },
    "CUST-1002": {
        "name": "Ananya Iyer",
        "age": 28,
        "occupation": "Software Engineer",
        "city": "Bangalore",
        "monthly_income": 150000.0,
        "risk_profile": "Medium",
        "savings_goal": "Dream Home Downpayment",
        "investment_style": "Moderate (SIPs, Stocks, PPF)",
        "credit_score": 780,
        "emergency_fund_goal": 300000.0,
        "salary_merchant": "Infosys",
        "salary_category": "Salary",
        "salary_sub_category": "Tech Corp Salary",
        "rent_amount": 25000.0,
        "sip_amount": 25000.0
    },
    "CUST-1003": {
        "name": "Dr. Vikram Adiga",
        "age": 42,
        "occupation": "Doctor",
        "city": "Mumbai",
        "monthly_income": 450000.0,
        "risk_profile": "Low",
        "savings_goal": "Private Clinic Expansion",
        "investment_style": "Conservative (Fixed Deposits, Debt Funds, Gold)",
        "credit_score": 810,
        "emergency_fund_goal": 1000000.0,
        "salary_merchant": "Fortis Hospital Bill",
        "salary_category": "Salary",
        "salary_sub_category": "Tech Corp Salary",
        "rent_amount": 75000.0,
        "sip_amount": 75000.0
    },
    "CUST-1004": {
        "name": "Rajesh Bansal",
        "age": 50,
        "occupation": "Business Owner",
        "city": "Delhi",
        "monthly_income": 800000.0,
        "risk_profile": "High",
        "savings_goal": "New Warehouse Purchase",
        "investment_style": "Aggressive (Equity Stocks, VC, Gold)",
        "credit_score": 750,
        "emergency_fund_goal": 2000000.0,
        "salary_merchant": "Reliance Industries",
        "salary_category": "Salary",
        "salary_sub_category": "Tech Corp Salary",
        "rent_amount": 120000.0,
        "sip_amount": 150000.0
    },
    "CUST-1005": {
        "name": "Devendra Shastri",
        "age": 67,
        "occupation": "Retired Person",
        "city": "Ahmedabad",
        "monthly_income": 65000.0,
        "risk_profile": "Low",
        "savings_goal": "Healthcare Contingency",
        "investment_style": "Very Conservative (SCSS, Post Office, FD)",
        "credit_score": 790,
        "emergency_fund_goal": 500000.0,
        "salary_merchant": "SBI Fixed Deposit Interest",
        "salary_category": "Interest",
        "salary_sub_category": "Fixed Deposit Interest",
        "rent_amount": 15000.0,
        "sip_amount": 8000.0
    }
}

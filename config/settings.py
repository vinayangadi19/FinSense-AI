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

# Category and Sub-category maps
INCOME_CATEGORIES = {
    "Salary": ["Tech Corp Salary", "Monthly Paycheck", "Part-Time Paycheck"],
    "Freelancing": ["Web Development", "Data Analysis Consulting", "UI Design Project", "Content Writing"],
    "Investment": ["Stock Dividend", "Crypto Staking Reward", "Mutual Fund Payout"],
    "Interest": ["Savings Account Interest", "Fixed Deposit Interest"],
    "Bonus": ["Annual Performance Bonus", "Sign-on Bonus", "Holiday Bonus"],
    "Rental Income": ["Apartment Rental", "Commercial Space Rental"],
    "Refund": ["Store Refund", "Tax Refund", "Subscription Reimbursement"],
    "Gift": ["Birthday Gift Cash", "Holiday Gift", "Family Support"]
}

EXPENSE_CATEGORIES = {
    "Rent": ["Apartment Rent", "Office Space Rent", "Parking Lot Rent"],
    "Food": ["Dining Out", "Coffee Shops", "Fast Food", "Food Delivery"],
    "Groceries": ["Supermarket Groceries", "Organic Food Store", "Beverages & Snacks"],
    "Fuel": ["Petrol Station", "EV Charging", "Gasoline Purchase"],
    "Transport": ["Ride-Sharing (Uber/Lyft)", "Public Transit Pass", "Train Tickets", "Tolls & Parking"],
    "Shopping": ["Clothing & Accessories", "Electronics & Gadgets", "Home Decor & Furniture", "Books & Stationery"],
    "Healthcare": ["Doctor Visit", "Pharmacy & Medicine", "Dental Care", "Eye Care Clinic"],
    "Insurance": ["Auto Insurance Premium", "Life Insurance Premium", "Home Insurance Premium", "Health Insurance Co-pay"],
    "Electricity": ["State Power Grid Bill", "Solar Energy Surcharge"],
    "Water Bill": ["Municipal Water Supply Bill"],
    "Internet": ["Broadband Internet Subscription", "Mobile Data Plan"],
    "Entertainment": ["Movie Theater Tickets", "Concerts & Shows", "Video Gaming Purchases", "Streaming Rentals"],
    "Travel": ["Flight Tickets", "Hotel Booking", "Car Rental Service", "Tours & Sightseeing"],
    "Education": ["University Tuition", "Online Courses (Coursera/Udemy)", "Textbooks & Materials", "Technical Certifications"],
    "Subscriptions": ["Netflix/Spotify Subscription", "Gym Membership Fee", "Software SaaS Tools", "Newsletter Subscription"],
    "EMI": ["Home Mortgage Payment", "Car Loan Installment", "Education Loan EMI"],
    "Investment": ["Mutual Fund SIP", "Stock Purchase", "Retirement Fund Contribution", "Gold Bond Investment"],
    "Taxes": ["Quarterly Income Tax", "Annual Property Tax", "Capital Gains Tax"],
    "Miscellaneous": ["Cash Withdrawal", "Bank Maintenance Fees", "Charitable Donations", "Unexpected Legal Fees"]
}

ALL_CATEGORIES = {**INCOME_CATEGORIES, **EXPENSE_CATEGORIES}

# Merchants mapping by Category
MERCHANTS = {
    # Income
    "Salary": ["Google Inc.", "Meta Platforms", "Apple Inc.", "Amazon Corp", "Microsoft Corp"],
    "Freelancing": ["Upwork Client", "Fiverr Client", "Toptal Consulting", "Direct Client Project"],
    "Investment": ["Vanguard Dividends", "Fidelity Brokerage", "Robinhood Dividends", "Charles Schwab Payout"],
    "Interest": ["Ally High Yield Interest", "Chase Savings Interest", "Discover Interest Payout"],
    "Bonus": ["Annual Corporate Bonus", "Spot Bonus Credit", "Signing Bonus Pay"],
    "Rental Income": ["Apartment Rental Credit", "Office Leasing Payout"],
    "Refund": ["Amazon Store Refund", "Target Store Refund", "Apple Store Return Credit"],
    "Gift": ["Birthday Cash Gift", "Holiday Family Gift", "Graduation Support"],
    
    # Expense
    "Rent": ["Metropolitan Leasing", "Avalon Communities", "Equity Residential", "City Property Mgmt"],
    "Food": ["Starbucks Coffee", "Chipotle Grill", "UberEats Delivery", "McDonalds", "Sweetgreen Salads", "Dominos Pizza"],
    "Groceries": ["Whole Foods Market", "Trader Joes", "Kroger Supermarket", "Safeway Groceries", "Costco Wholesale"],
    "Fuel": ["Chevron Station", "Shell Gasoline", "ExxonMobil Fuel", "Tesla EV Supercharger", "BP Service Station"],
    "Transport": ["Uber Ride Sharing", "Lyft Ride", "Transit Authority Ticket", "Amtrak Train Pass", "City Parking Garage"],
    "Shopping": ["Amazon Online", "Target Store", "Nordstrom Boutique", "Apple Store Online", "Best Buy Electronics", "Nike Store"],
    "Healthcare": ["CVS Pharmacy", "Walgreens Medicine", "City Dental Care", "Community Urgent Care", "General Hospital Health"],
    "Insurance": ["Geico Auto Insurance", "Progressive Premium", "State Farm Coverage", "Blue Cross Co-pay"],
    "Electricity": ["Pacific Gas & Electric", "State Grid Power", "ConEd Electric Bill"],
    "Water Bill": ["Municipal Water Supply", "Water Utility Co"],
    "Internet": ["Comcast Xfinity", "AT&T Broadband", "Verizon FiOS internet"],
    "Entertainment": ["AMC Theaters", "Ticketmaster Ticket", "Steam Games", "Playstation Network Store", "Youtube Premium Store"],
    "Travel": ["Delta Air Lines", "United Airlines Flight", "Marriott Hotels", "Airbnb Lodging", "Hertz Car Rental"],
    "Education": ["Coursera Courses", "Udemy Tech Course", "University Bookshop", "Linux Foundation Certificate"],
    "Subscriptions": ["Netflix Service", "Spotify Premium", "Gym Fitness Club", "Adobe Creative Cloud"],
    "EMI": ["Chase Mortgage Autopay", "Toyota Auto Loan EMI", "Sallie Mae Student Loan"],
    "Investment": ["Vanguard Mutual Fund SIP", "Fidelity Brokerage Buy", "Schwab Investment Mutual"],
    "Taxes": ["IRS Quarterly Tax", "State Tax Revenue", "County Property Tax Office"],
    "Miscellaneous": ["Chase ATM Withdrawal", "Bank Maintenance Fee", "Red Cross Donation", "Local Court Fee"]
}

# Account configurations
ACCOUNT_TYPES = ["Savings Account", "Current Account", "Credit Card"]
PAYMENT_MODES = ["Credit Card", "Debit Card", "Net Banking", "UPI", "Cash"]
CURRENCY = "USD"

# Geographical data coordinates mapped by City, State, Country
GEOGRAPHY = {
    "New York": {"state": "NY", "country": "USA", "lat": (40.7128, 0.05), "lon": (-74.0060, 0.05)},
    "San Francisco": {"state": "CA", "country": "USA", "lat": (37.7749, 0.04), "lon": (-122.4194, 0.04)},
    "Chicago": {"state": "IL", "country": "USA", "lat": (41.8781, 0.04), "lon": (-87.6298, 0.04)},
    "Austin": {"state": "TX", "country": "USA", "lat": (30.2672, 0.03), "lon": (-97.7431, 0.03)},
    "Seattle": {"state": "WA", "country": "USA", "lat": (47.6062, 0.04), "lon": (-122.3321, 0.04)},
    "Miami": {"state": "FL", "country": "USA", "lat": (25.7617, 0.03), "lon": (-80.1918, 0.03)},
    "Denver": {"state": "CO", "country": "USA", "lat": (39.7392, 0.03), "lon": (-104.9903, 0.03)},
    "Boston": {"state": "MA", "country": "USA", "lat": (42.3601, 0.03), "lon": (-71.0589, 0.03)}
}

# Ensure directories exist
for folder in [DATA_DIR, os.path.join(DATA_DIR, "raw"), os.path.join(DATA_DIR, "processed"),
               os.path.join(DATA_DIR, "external"), os.path.join(DATA_DIR, "archive"),
               MODELS_DIR, LOGS_DIR, REPORTS_DIR, os.path.dirname(DATABASE_PATH)]:
    os.makedirs(folder, exist_ok=True)

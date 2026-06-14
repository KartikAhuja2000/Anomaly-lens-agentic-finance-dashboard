import mysql.connector
import random
from datetime import datetime, timedelta

conn = mysql.connector.connect(
    host="localhost",
    user="your username",
    password="your password here",
    database="expense_tracker"
)
cur = conn.cursor()

departments = ["Sales", "Marketing", "IT", "HR", "Operations", "Finance"]
categories = ["Travel", "Software", "Office Supplies", "Marketing Spend", "Training", "Meals"]
vendors = ["Acme Supplies", "Globex Travel", "TechCorp Hardware", "Initech Services",
           "Staples Office", "CloudNine Hosting", "QuickCab", "FoodieCaterers"]

start_date = datetime(2025, 9, 1)
end_date = datetime(2026, 2, 28)

def random_date():
    delta = (end_date - start_date).days
    return start_date + timedelta(days=random.randint(0, delta))

# --- 200 normal transactions ---
for _ in range(200):
    dept_id = random.randint(1, len(departments))
    vendor_id = random.randint(1, len(vendors))
    category = random.choice(categories)
    amount = round(random.uniform(500, 15000), 2)
    date = random_date().strftime("%Y-%m-%d")
    desc = f"{category} expense via {vendors[vendor_id-1]}"
    cur.execute(
        "INSERT INTO transactions (department_id, vendor_id, category, amount, transaction_date, description) VALUES (%s, %s, %s, %s, %s, %s)",
        (dept_id, vendor_id, category, amount, date, desc)
    )

conn.commit()

# --- New anomalies ---

# Duplicate payment - travel
for _ in range(2):
    cur.execute(
        "INSERT INTO transactions (department_id, vendor_id, category, amount, transaction_date, description) VALUES (%s, %s, %s, %s, %s, %s)",
        (1, 2, "Travel", 35000.00, "2026-01-15", "Business travel reimbursement")
    )

# Unusual amount - office supplies
cur.execute(
    "INSERT INTO transactions (department_id, vendor_id, category, amount, transaction_date, description) VALUES (%s, %s, %s, %s, %s, %s)",
    (4, 5, "Office Supplies", 88000.00, "2026-01-20", "Bulk office supplies order")
)

# Policy violation - weekend meal
cur.execute(
    "INSERT INTO transactions (department_id, vendor_id, category, amount, transaction_date, description) VALUES (%s, %s, %s, %s, %s, %s)",
    (5, 8, "Meals", 18000.00, "2026-01-11", "Team offsite dinner - weekend")
)

# Unusual amount - training spike
cur.execute(
    "INSERT INTO transactions (department_id, vendor_id, category, amount, transaction_date, description) VALUES (%s, %s, %s, %s, %s, %s)",
    (6, 3, "Training", 72000.00, "2025-12-05", "External training program")
)

# Duplicate - software vendor
for _ in range(2):
    cur.execute(
        "INSERT INTO transactions (department_id, vendor_id, category, amount, transaction_date, description) VALUES (%s, %s, %s, %s, %s, %s)",
        (2, 6, "Software", 29000.00, "2026-02-20", "Software license renewal")
    )

conn.commit()
cur.close()
conn.close()
print("Additional transactions inserted successfully.")
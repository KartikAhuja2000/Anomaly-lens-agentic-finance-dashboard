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

# --- Departments ---
departments = ["Sales", "Marketing", "IT", "HR", "Operations", "Finance"]
for d in departments:
    cur.execute("INSERT INTO departments (department_name) VALUES (%s)", (d,))

# --- Vendors ---
vendors = ["Acme Supplies", "Globex Travel", "TechCorp Hardware", "Initech Services",
           "Staples Office", "CloudNine Hosting", "QuickCab", "FoodieCaterers"]
for v in vendors:
    cur.execute("INSERT INTO vendors (vendor_name) VALUES (%s)", (v,))

conn.commit()

# --- Budgets ---
categories = ["Travel", "Software", "Office Supplies", "Marketing Spend", "Training", "Meals"]
months = ["2025-09", "2025-10", "2025-11", "2025-12", "2026-01", "2026-02"]

for dept_id in range(1, len(departments) + 1):
    for cat in categories:
        for month in months:
            budget = random.randint(20000, 100000)
            cur.execute(
                "INSERT INTO budgets (department_id, category, month, budget_amount) VALUES (%s, %s, %s, %s)",
                (dept_id, cat, month, budget)
            )

conn.commit()

# --- Normal transactions ---
start_date = datetime(2025, 9, 1)
end_date = datetime(2026, 2, 28)

def random_date():
    delta = (end_date - start_date).days
    return start_date + timedelta(days=random.randint(0, delta))

for _ in range(500):
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

# --- Deliberate anomalies ---

# 1. Duplicate payment
for _ in range(2):
    cur.execute(
        "INSERT INTO transactions (department_id, vendor_id, category, amount, transaction_date, description) VALUES (%s, %s, %s, %s, %s, %s)",
        (3, 6, "Software", 48000.00, "2026-02-10", "Cloud hosting renewal")
    )

# 2. Unusually large amount
cur.execute(
    "INSERT INTO transactions (department_id, vendor_id, category, amount, transaction_date, description) VALUES (%s, %s, %s, %s, %s, %s)",
    (2, 4, "Meals", 95000.00, "2026-02-12", "Team dinner")
)

# 3. Policy violation - weekend meal expense over limit
cur.execute(
    "INSERT INTO transactions (department_id, vendor_id, category, amount, transaction_date, description) VALUES (%s, %s, %s, %s, %s, %s)",
    (1, 8, "Meals", 22000.00, "2026-02-08", "Client entertainment - weekend")
)

conn.commit()
cur.close()
conn.close()
print("Database populated successfully.")
import mysql.connector
import requests
import os
from datetime import datetime

GROQ_API_KEY = "your API key here"
GROQ_URL = "your url here"

DB_CONFIG = {
    "host": "localhost",
    "user": "your username",
    "password": "your passoword here",
    "database": "expense_tracker"
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def find_duplicate_payments(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT t1.transaction_id, t1.vendor_id, t1.amount, t1.transaction_date,
               t1.category, t1.department_id, t1.description
        FROM transactions t1
        JOIN transactions t2
          ON t1.vendor_id = t2.vendor_id
         AND t1.amount = t2.amount
         AND t1.transaction_date = t2.transaction_date
         AND t1.transaction_id != t2.transaction_id
    """)
    return cur.fetchall()

def find_unusual_amounts(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT t1.transaction_id, t1.vendor_id, t1.amount, t1.transaction_date,
               t1.category, t1.department_id, t1.description,
               (SELECT AVG(amount) FROM transactions t2 WHERE t2.category = t1.category) as cat_avg
        FROM transactions t1
    """)
    rows = cur.fetchall()
    flagged = [r[:7] for r in rows if r[2] > r[7] * 3]  # amount > 3x category average
    return flagged

def find_policy_violations(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT transaction_id, vendor_id, amount, transaction_date, category, department_id, description
        FROM transactions
        WHERE category = 'Meals' AND amount > 10000
    """)
    rows = cur.fetchall()
    violations = []
    for r in rows:
        date_obj = r[3]  # already a date object from MySQL
        if date_obj.weekday() >= 5:
            violations.append(r)
    return violations

def already_flagged(conn, transaction_id):
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM flagged_transactions WHERE transaction_id = %s", (transaction_id,))
    return cur.fetchone() is not None

def ask_llm_for_explanation(transaction, reason):
    transaction_id, vendor_id, amount, date, category, department_id, description = transaction

    prompt = f"""You are a finance compliance assistant. A transaction has been automatically flagged for the reason: "{reason}".

Transaction details:
- Amount: {amount}
- Category: {category}
- Date: {date}
- Description: {description}
- Department ID: {department_id}
- Vendor ID: {vendor_id}

Write a short (2-3 sentence) plain-English explanation of why this transaction looks suspicious, and one suggested next step for the finance team. Keep it concise and professional."""

    response = requests.post(
        GROQ_URL,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "max_tokens": 200,
            "messages": [{"role": "user", "content": prompt}]
        }
    )
    data = response.json()
    print("GROQ RESPONSE:", data)  # temporary debug line
    return data["choices"][0]["message"]["content"]

def write_flag(conn, transaction_id, reason, explanation):
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO flagged_transactions (transaction_id, flag_reason, ai_explanation, flagged_on, status) VALUES (%s, %s, %s, %s, %s)",
        (transaction_id, reason, explanation, datetime.now(), "open")
    )
    conn.commit()

def run_agent():
    conn = get_connection()

    checks = [
        ("duplicate", find_duplicate_payments(conn)),
        ("unusual_amount", find_unusual_amounts(conn)),
        ("policy_violation", find_policy_violations(conn)),
    ]

    total_flagged = 0
    for reason, transactions in checks:
        for txn in transactions:
            transaction_id = txn[0]
            if already_flagged(conn, transaction_id):
                continue
            explanation = ask_llm_for_explanation(txn, reason)
            write_flag(conn, transaction_id, reason, explanation)
            total_flagged += 1
            print(f"Flagged transaction {transaction_id} ({reason})")

    conn.close()
    print(f"Done. {total_flagged} new transactions flagged.")

if __name__ == "__main__":
    run_agent()
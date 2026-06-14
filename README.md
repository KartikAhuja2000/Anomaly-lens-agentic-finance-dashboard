# Anomaly-lens-agentic-finance-dashboard
An AI-powered expense monitoring system that automatically detects anomalies  in financial transactions and explains them in plain English using an LLM.

## Architecture

MySQL Database → Python Agent (Groq + LLaMA 3.3 70B) → Flagged Transactions Table → Power BI Dashboard

## Features

- **Spend Overview** — monthly trends, category breakdown, department-wise spend
- **Budget vs Actual** — matrix with conditional formatting on variance %
- **Flagged Transactions** — AI-generated explanations per anomaly, with open/reviewed/dismissed workflow

## Anomaly Detection Logic

The agent detects three types of issues:
1. **Duplicate payments** — same vendor, same amount, same date
2. **Unusual amounts** — transaction exceeds 3x the category average
3. **Policy violations** — meal expenses over ₹10,000 on weekends

## Tech Stack

| Layer | Tool |
|-------|------|
| Database | MySQL |
| Agent | Python |
| LLM | Groq API (LLaMA 3.3 70B) |
| Visualization | Power BI |
| DAX Measures | Total Actual Spend, Total Budget, Variance %, Open Flags Count |

## Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/anomalylens-agentic-finance-dashboard
cd anomalylens-agentic-finance-dashboard
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up MySQL
- Create a database called `expense_tracker`
- Run `schema.sql` in MySQL Workbench

### 4. Add your credentials
In `generate_data.py` and `agent_flagged_transactions.py`, update:
```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "YOUR_MYSQL_PASSWORD",
    "database": "expense_tracker"
}
GROQ_API_KEY = "YOUR_GROQ_API_KEY"
```

### 5. Generate sample data
```bash
python generate_data.py
```

### 6. Run the agent
```bash
python agent_flagged_transactions.py
```

### 7. Connect Power BI
- Open Power BI Desktop → Get Data → MySQL Database
- Server: `localhost`, Database: `expense_tracker`
- Load all 5 tables and build the data model

## Screenshots

### Spend Overview
<img width="706" height="392" alt="image" src="https://github.com/user-attachments/assets/19394818-c547-41a8-b1d0-3ff07471ffb0" />


### Budget vs Actual
<img width="707" height="391" alt="image" src="https://github.com/user-attachments/assets/be8419bf-7b16-4465-8ee9-2e750f01f5b2" />


### Flagged Transactions
<img width="705" height="390" alt="image" src="https://github.com/user-attachments/assets/f029ce6c-65e3-4bf1-a562-aaa1240e2c5f" />


## Author
Kartik Ahuja — [LinkedIn](https://www.linkedin.com/in/kartik-ahuja-4b3544136/)

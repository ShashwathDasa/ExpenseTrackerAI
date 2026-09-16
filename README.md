# ExpenseTrackerAI

An AI-powered personal finance assistant that allows users to query and analyze their financial data using natural language through Telegram.

The application uses an LLM to understand user intent and select the appropriate finance tool, while financial data retrieval and calculations are handled deterministically by Python services connected to Google Sheets.

---

## Overview

ExpenseTrackerAI provides a conversational interface for interacting with personal financial data.

Instead of navigating through spreadsheets and manually calculating expenses, users can ask questions such as:

- How much did I spend this month?
- How much did I spend on food?
- Compare my expenses for August and September.
- Compare my category-wise spending between two months.
- How much did I spend in the first 10 days of August?

The LLM interprets the request, selects the appropriate tool, and the application retrieves and calculates the required information from Google Sheets.

---

## Architecture

```text
                         ┌─────────────────┐
                         │     Telegram    │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ Authentication  │
                         │  & User Lookup  │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │  Finance Agent  │
                         │      (LLM)      │
                         └────────┬────────┘
                                  │
                            Tool Selection
                                  │
                                  ▼
                         ┌─────────────────┐
                         │  Finance Tools  │
                         └────────┬────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │ Transaction Service │
                       └──────────┬──────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │  Google Sheets  │
                         │  Source of Truth│
                         └─────────────────┘
```

### Request Flow

1. User sends a message through Telegram.
2. The Telegram chat ID is authenticated against the `Users` sheet.
3. The authenticated user is passed into the application session.
4. The LLM interprets the user's request.
5. The LLM selects the appropriate finance tool.
6. The tool retrieves the required transactions from Google Sheets.
7. Python performs deterministic financial calculations.
8. The structured result is returned to the LLM.
9. The LLM generates a concise natural-language response.
10. The response is sent back through Telegram.

---

## Key Design Decisions

### LLM for reasoning, Python for calculations

The LLM is responsible for:

- Understanding natural-language requests
- Identifying user intent
- Selecting the appropriate tool
- Determining parameters such as date ranges
- Explaining the results

Python is responsible for:

- Retrieving financial records
- Filtering transactions
- Aggregating amounts
- Comparing periods
- Calculating differences
- Calculating percentage changes

This separation prevents the LLM from being responsible for financial arithmetic.

### Google Sheets as the source of truth

The project currently uses Google Sheets as the financial data store.

No separate database is required for the current use case.

Each user's transactions are stored in a dedicated worksheet, while the `Users` worksheet maps application users to their corresponding transaction sheet.

```text
Users
 ├── username
 ├── telegram_chat_id
 ├── allowed
 └── sheet_name
```

The application does not assume that a username and worksheet name are the same.

### Authentication before the LLM

Telegram users are authenticated using their Telegram chat ID before a request reaches the finance agent.

The authenticated user is stored in the application session and is not controlled by the LLM.

This means the LLM cannot decide which authenticated user is making the request.

---

## Current Finance Tools

### Total Expenses

Retrieves total expenses for a specified date range.

Example:

```text
How much did I spend in August?
```

### Category Summary

Provides an expense breakdown by category.

Examples:

```text
How much did I spend on Food in August?
```

```text
Where did I spend my money this month?
```

### Expense Comparison

Compares total expenses between two periods.

Example:

```text
Compare my expenses for the first 10 days of August and September.
```

The tool calculates:

- Total for period 1
- Total for period 2
- Difference
- Percentage change

### Category Expense Comparison

Compares category-wise spending between two periods.

Example:

```text
Compare my category-wise expenses between August and September.
```

The tool calculates the change for each category independently.

---

## Transaction Types

The financial tracker distinguishes between different transaction types:

```text
Income
Expense
Transfer
Investment
```

The application applies the following rules:

- `Expense` → counted as spending
- `Transfer` → not counted as spending
- `Investment` → not automatically counted as spending
- `Income` → not counted as spending

This prevents transfers and investments from being incorrectly included in expense calculations.

---

## Project Structure

```text
ExpenseTrackerAI/
│
├── agent/
│   ├── __init__.py
│   ├── finance_agent.py
│   ├── tool_registry.py
│   └── tools.py
│
├── sheets/
│   ├── __init__.py
│   ├── client.py
│   ├── users.py
│   └── transactions.py
│
├── telegram_bot/
│   ├── __init__.py
│   └── bot.py
│
├── utils/
│   ├── __init__.py
│   ├── amounts.py
│   └── dates.py
│
├── app.py
├── config.py
└── requirements.txt
```

> `.env` and `google_credentials.json` contain sensitive credentials and should never be committed to the repository.

---

## Tech Stack

### Backend

- Python
- Google Sheets API
- gspread

### AI

- Groq API
- `openai/gpt-oss-120b`
- LLM tool calling

### Interface

- Telegram
- python-telegram-bot

### Data

- Google Sheets

---

## Tool Calling Architecture

The project uses a custom tool registry that converts Python functions into LLM-compatible tool definitions.

A finance operation can be defined as a normal Python function:

```python
@llm_tool()
def get_total_expenses(
    session,
    start_date: str | None = None,
    end_date: str | None = None,
    username: str | None = None
):
    ...
```

The tool registry uses:

- Python type annotations
- Function signatures
- Docstrings

to generate the schema provided to the LLM.

This allows new finance capabilities to be added as tools without hardcoding every possible user question into the agent.

---

## Example Interaction

```text
User:
Compare my expenses for the first 10 days of August and September.

Agent:
→ Understands comparison intent
→ Resolves August 1–10
→ Resolves September 1–10
→ Calls compare_expenses()
→ Python retrieves and calculates the values
→ LLM explains the result
→ Response sent to Telegram
```

Another example:

```text
User:
How much did I spend on Food in August?

Agent:
→ Identifies category + date range
→ Calls get_category_summary()
→ Retrieves Expense transactions
→ Filters category = Food
→ Calculates total
→ Returns result through the LLM
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/ShashwathDasa/ExpenseTrackerAI.git
cd ExpenseTrackerAI
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

macOS/Linux:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GROQ_API_KEY=your_groq_api_key
```

### 5. Configure Google Sheets

Create a Google service account and provide its credentials as:

```text
google_credentials.json
```

Share the Google Sheet with the service account email.

The spreadsheet ID is configured in `config.py`.

### 6. Run the application

```bash
python app.py
```

The Telegram bot will start polling for messages.

---

## Security

The project uses Telegram chat IDs for application-level authentication.

Sensitive credentials should be stored outside version control.

The following files should never be committed:

```text
.env
google_credentials.json
```

Make sure they are included in `.gitignore`.

---

## Current Limitations

The current version focuses primarily on structured financial queries and analysis.

It does not yet include:

- Adding transactions through Telegram
- Editing or deleting transactions
- Budget management
- Anomaly detection
- Spending forecasts
- Recurring expense detection
- Advanced financial recommendations
- Persistent conversational memory
- Automated evaluation of tool selection and response accuracy

---

## Future Direction

The core agent architecture can be extended with additional finance tools without changing the overall design.

Potential additions include:

- Spending trend analysis
- Anomaly detection
- Expense forecasting
- Budget management
- Adding and editing transactions through Telegram
- Recurring expense detection
- Automated agent evaluation

The goal is to keep the LLM responsible for interpreting requests and coordinating capabilities while keeping financial operations deterministic and testable.

---

## Author

**Shashwath Dasa**

GitHub: https://github.com/ShashwathDasa/ExpenseTrackerAI

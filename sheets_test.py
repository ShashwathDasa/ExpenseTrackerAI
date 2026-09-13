import agent.tools

from agent.tool_registry import call_tool
from sheets.client import GoogleSheetsClient
from sheets.users import UserService
from sheets.transactions import TransactionService


sheets_client = GoogleSheetsClient()

user_service = UserService(sheets_client)
transaction_service = TransactionService(sheets_client)

user = user_service.get_user_by_chat_id("6571180313")

session = {
    "user": user,
    "transaction_service": transaction_service,
}

result = call_tool(
    "get_total_expenses",
    session,
    {
        "start_date": "2026-09-01",
        "end_date": "2026-09-13",
    }
)

print(result)

print(result)
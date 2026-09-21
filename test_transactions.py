from agent.finance_agent import FinanceAgent
from sheets.client import GoogleSheetsClient
from sheets.users import UserService
from sheets.transactions import TransactionService


def create_session():
    sheets_client = GoogleSheetsClient()

    user_service = UserService(sheets_client)
    transaction_service = TransactionService(sheets_client)

    # Use one of your actual authorized Telegram chat IDs
    chat_id = "6571180313"

    user = user_service.get_user_by_chat_id(chat_id)

    if user is None:
        raise ValueError("User not found")

    return {
        "user": user,
        "user_service": user_service,
        "transaction_service": transaction_service,
    }


session = create_session()
agent = FinanceAgent(session)

test_cases = [
    "I spent ₹500 on dinner",
    "I spent ₹750 on Food",
    "I spent ₹1200 on groceries from Canara",
    "I spent ₹2000 on Food from Canara for dinner",
    "I transferred ₹5000 from Canara to Kotak",
]

for message in test_cases:
    print("\n" + "=" * 60)
    print(f"USER: {message}")
    print("=" * 60)

    response, history = agent.respond(message)

    print("\nAGENT RESPONSE:")
    print(response)
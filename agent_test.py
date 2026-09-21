# import agent.tools
#
# from agent.finance_agent import FinanceAgent
# from sheets.client import GoogleSheetsClient
# from sheets.users import UserService
# from sheets.transactions import TransactionService
#
#
# sheets_client = GoogleSheetsClient()
#
# user_service = UserService(sheets_client)
# transaction_service = TransactionService(sheets_client)
#
# user = user_service.get_user_by_chat_id("6571180313")
#
# session = {
#     "user": user,
#     "transaction_service": transaction_service,
# }
#
# agent = FinanceAgent(session)
#
# response = agent.respond(
#     "Where did I spend my money last month?"
# )
#
# print(response)

# from sheets.client import GoogleSheetsClient
# from sheets.users import UserService
#
# sheets_client = GoogleSheetsClient()
# user_service = UserService(sheets_client)
#
# print(user_service.get_user_by_username("Uha"))
# print(user_service.get_user_by_username("ShashwathDasa"))

# from agent.formatter import format_currency
#
# print(format_currency(28834.30))

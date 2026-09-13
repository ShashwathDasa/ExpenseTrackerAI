from agent.tool_registry import llm_tool


@llm_tool()
def get_total_expenses(session, start_date: str | None = None, end_date: str | None = None):
    """
    Calculate the total amount of expenses for the authenticated user.

    If a date range is provided, only expenses within that range are included.
    If no date range is provided, all available expenses are included.

    :param start_date: Optional start date, inclusive, in YYYY-MM-DD format.
    :param end_date: Optional end date, inclusive, in YYYY-MM-DD format.
    """

    transaction_service = session["transaction_service"]
    user = session["user"]
    transactions = transaction_service.get_transactions(user)
    expenses = transaction_service.filter_transactions(transactions, transaction_type="Expense", start_date=start_date,
        end_date=end_date)
    total = transaction_service.get_total(expenses)
    return {"status": "success","total": total}
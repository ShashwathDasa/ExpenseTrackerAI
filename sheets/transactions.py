from datetime import date, timedelta

from sheets.lists import ListsService
from utils.dates import parse_date
from utils.amounts import parse_amount


class TransactionService:
    def __init__(self, sheets_client):
        self.sheets_client = sheets_client
        self.lists_service = ListsService(sheets_client)

    def get_transactions(self, user):
        worksheet = self.sheets_client.get_worksheet(user["sheet_name"])
        return worksheet.get_all_records()

    def filter_transactions(self, transactions, transaction_type=None, start_date=None, end_date=None):
        if start_date:
            start_date = parse_date(start_date)
        if end_date:
            end_date = parse_date(end_date)

        filtered = []
        for transaction in transactions:
            # Filter by transaction type
            if transaction_type and transaction.get("Type") != transaction_type:
                continue
            # Parse transaction date
            transaction_date = parse_date(transaction["Date"])
            # Filter by start date
            if start_date and transaction_date < start_date:
                continue
            # Filter by end date
            if end_date and transaction_date > end_date:
                continue
            filtered.append(transaction)
        return filtered

    def get_total(self, transactions):
        total = 0

        for transaction in transactions:
            total += parse_amount(transaction["Amount"])

        return total

    def get_category_summary(self, transactions):
        summary = {}
        for transaction in transactions:
            category = transaction["Category"]
            amount = parse_amount(transaction["Amount"])
            if category not in summary:
                summary[category] = 0
            summary[category] += amount
        return summary

    def get_monthly_summary(self, transactions, transaction_type=None):
        summary = {}
        for transaction in transactions:
            if transaction_type and transaction.get("Type") != transaction_type:
                continue
            transaction_date = parse_date(transaction["Date"])
            month = transaction_date.strftime("%b")
            amount = parse_amount(transaction["Amount"])
            if month not in summary:
                summary[month] = 0
            summary[month] += amount
        return summary

    def get_most_used_categories(self, transactions, limit=6):
        category_counts = {}
        for transaction in transactions:
            if transaction.get("Type") != "Expense":
                continue
            category = transaction.get("Category")
            if not category:
                continue

            category_counts[category] = category_counts.get(category, 0) + 1
        sorted_categories = sorted(category_counts.items(), key=lambda item: item[1], reverse=True)
        return [category for category, count in sorted_categories[:limit]]

    def get_most_used_categories_for_user(self, user, limit=6):
        today = date.today()
        first_day_current_month = today.replace(day=1)
        last_day_previous_month = first_day_current_month - timedelta(days=1)
        first_day_previous_month = last_day_previous_month.replace(day=1)

        transactions = self.get_transactions(user)
        filtered_transactions = self.filter_transactions(transactions, transaction_type="Expense",
                                                         start_date=first_day_previous_month.isoformat(),
                                                         end_date=last_day_previous_month.isoformat(), )

        category_counts = {}
        for transaction in filtered_transactions:
            category = transaction.get("Category")
            if not category:
                continue
            category_counts[category] = category_counts.get(category, 0) + 1

        sorted_categories = sorted(category_counts.items(), key=lambda item: item[1], reverse=True)
        return [category for category, count in sorted_categories[:limit]]

    def get_most_used_accounts_for_user(self, user, limit=6):
        today = date.today()

        first_day_current_month = today.replace(day=1)
        last_day_previous_month = first_day_current_month - timedelta(days=1)
        first_day_previous_month = last_day_previous_month.replace(day=1)

        transactions = self.get_transactions(user)
        filtered_transactions = self.filter_transactions(transactions, transaction_type="Expense",
                                                         start_date=first_day_previous_month.isoformat(),
                                                         end_date=last_day_previous_month.isoformat(), )

        account_counts = {}
        for transaction in filtered_transactions:
            account = transaction.get("From Account")
            if not account:
                continue
            account_counts[account] = account_counts.get(account, 0) + 1

        sorted_accounts = sorted(account_counts.items(), key=lambda item: item[1], reverse=True, )

        return [account for account, count in sorted_accounts[:limit]]

    def add_transaction(self, user, transaction):
        transaction_type = transaction.get("type")
        amount = transaction.get("amount")
        reason = transaction.get("reason")
        category = transaction.get("category")
        from_account = transaction.get("from_account")
        to_account = transaction.get("to_account")
        transaction_date = transaction.get("transaction_date")

        # --------------------------------
        # Validate transaction type
        # --------------------------------

        valid_types = self.lists_service.get_transaction_types()
        if transaction_type not in valid_types:
            raise ValueError(f"Invalid transaction type: {transaction_type}")

        # --------------------------------
        # Validate amount
        # --------------------------------

        if amount is None:
            raise ValueError("Transaction amount is required")
        amount = parse_amount(str(amount))
        if amount <= 0:
            raise ValueError("Transaction amount must be greater than zero")

        # --------------------------------
        # Validate reason
        # --------------------------------

        if not reason:
            raise ValueError("Reason is required for a transaction")

        # --------------------------------
        # Validate category
        # --------------------------------

        if category:
            valid_categories = self.lists_service.get_categories()
            if category not in valid_categories:
                raise ValueError(f"Invalid category: {category}")

        # --------------------------------
        # Validate accounts
        # --------------------------------

        valid_accounts = self.lists_service.get_accounts(user)
        if from_account and from_account not in valid_accounts:
            raise ValueError(f"Invalid from account: {from_account}")
        if to_account and to_account not in valid_accounts:
            raise ValueError(f"Invalid to account: {to_account}")

        # --------------------------------
        # Validate transaction-specific fields
        # --------------------------------

        if transaction_type == "Expense":
            if not category:
                raise ValueError("Category is required for an expense")
            if not from_account:
                raise ValueError("From account is required for an expense")
        elif transaction_type == "Transfer":
            if not from_account:
                raise ValueError("From account is required for a transfer")
            if not to_account:
                raise ValueError("To account is required for a transfer")
            if from_account == to_account:
                raise ValueError("From account and to account cannot be the same")
        elif transaction_type == "Income":
            if not to_account:
                raise ValueError("To account is required for income")
        elif transaction_type == "Investment":
            if not from_account:
                raise ValueError("From account is required for an investment")

        # --------------------------------
        # Prepare transaction date
        # --------------------------------

        if transaction_date:
            transaction_day = parse_date(transaction_date)
        else:
            transaction_day = date.today()
        date_value = f"{transaction_day.day}-{transaction_day.strftime('%b-%Y')}"
        month_value = transaction_day.strftime("%b")

        # --------------------------------
        # Prepare row
        # --------------------------------

        row = [date_value, month_value, from_account or "", to_account or "", transaction_type, category or "",
               reason, amount]

        # --------------------------------
        # Write to Google Sheets
        # --------------------------------

        worksheet = self.sheets_client.get_worksheet(user["sheet_name"])
        worksheet.append_row(row, value_input_option="USER_ENTERED")

        # --------------------------------
        # Return result
        # --------------------------------

        return {
            "status": "success",
            "transaction": {
                "date": date_value,
                "month": month_value,
                "type": transaction_type,
                "amount": amount,
                "category": category,
                "reason": reason.title(),
                "from_account": from_account,
                "to_account": to_account,
            },
        }

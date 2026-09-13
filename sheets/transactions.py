from utils.dates import parse_date
from utils.amounts import parse_amount


class TransactionService:
    def __init__(self, sheets_client):
        self.sheets_client = sheets_client

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
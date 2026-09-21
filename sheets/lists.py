class ListsService:

    def __init__(self, sheets_client):
        self.sheets_client = sheets_client

    def get_lists(self):
        worksheet = self.sheets_client.get_worksheet("Lists")
        return worksheet.get_all_values()

    def get_transaction_types(self):
        values = self.get_lists()
        # Transaction Type is column E (index 4)
        return [row[4] for row in values[1:] if len(row) > 4 and row[4]]

    def get_categories(self):
        values = self.get_lists()
        # Categories is column G (index 6)
        return [row[6] for row in values[1:] if len(row) > 6 and row[6]]

    def get_accounts(self, user):
        values = self.get_lists()
        username = user["sheet_name"]

        # Find the user's account column from the header row.
        # Example:
        # Uha -> "Uha Accounts"
        # Shash -> "Shash Accounts"
        expected_header = f"{username} Accounts"
        header = values[0]
        account_column = None
        for index, column_name in enumerate(header):
            if column_name.strip().lower() == expected_header.lower():
                account_column = index
                break
        if account_column is None:
            raise ValueError(f"Account list not found for user: {username}")

        return [row[account_column] for row in values[1:] if len(row) > account_column and row[account_column]]

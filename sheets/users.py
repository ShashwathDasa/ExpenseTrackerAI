class UserService:

    def __init__(self, sheets_client):
        self.sheets_client = sheets_client

    def get_user_by_chat_id(self, chat_id):
        users_sheet = self.sheets_client.get_worksheet("Users")
        users = users_sheet.get_all_records()

        for user in users:
            if str(user["telegram_chat_id"]) == str(chat_id):
                if str(user["allowed"]).upper() == "TRUE":
                    return user

        return None

    def is_authorized(self, chat_id):
        return self.get_user_by_chat_id(chat_id) is not None
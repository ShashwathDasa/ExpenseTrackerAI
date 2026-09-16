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

    def get_user_by_username(self, username):
        users_sheet = self.sheets_client.get_worksheet("Users")
        users = users_sheet.get_all_records()

        for user in users:
            if user["username"].lower() == username.lower():
                if str(user["allowed"]).upper() == "TRUE":
                    return user
        return None

    def resolve_user(self, authenticated_user, username=None):
        if username is None:
            return authenticated_user
        user = self.get_user_by_username(username)
        if user is None:
            raise ValueError(f"User '{username}' not found")
        return user

    def is_authorized(self, chat_id):
        return self.get_user_by_chat_id(chat_id) is not None
from sheets.client import GoogleSheetsClient
from sheets.users import UserService
from telegram.bot import TelegramBot


def main():
    sheets_client = GoogleSheetsClient()
    user_service = UserService(sheets_client)
    bot = TelegramBot(user_service)
    bot.run()


if __name__ == "__main__":
    main()
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters


from config import Config


class TelegramBot:

    def __init__(self, user_service):
        self.user_service = user_service

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id

        user = self.user_service.get_user_by_chat_id(chat_id)

        if user is None:
            await update.message.reply_text("You are not authorized to use this bot.")
            return

        await update.message.reply_text(f"Hi {user['username']}!")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        message = update.message.text

        user = self.user_service.get_user_by_chat_id(chat_id)

        if user is None:
            await update.message.reply_text("You are not authorized to use this bot.")
            return

        print(
            f"User: {user['username']} | "
            f"Chat ID: {chat_id} | "
            f"Message: {message}"
        )

        await update.message.reply_text(f"Received: {message}")

    def run(self):
        application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()


        application.add_handler(CommandHandler("start", self.start))

        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        application.run_polling()
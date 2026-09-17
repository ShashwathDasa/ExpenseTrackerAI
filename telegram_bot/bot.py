from telegram import Update
from telegram.ext import ContextTypes, Application, CommandHandler, MessageHandler, filters

from agent.finance_agent import FinanceAgent
from config import Config
from conversation.store import ConversationStore


class TelegramBot:
    def __init__(self, user_service, transaction_service):
        self.user_service = user_service
        self.transaction_service = transaction_service
        self.conversation_store = ConversationStore()

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
        session = {
            "user": user,
            "user_service": self.user_service,
            "transaction_service": self.transaction_service,
        }
        history = self.conversation_store.get_history(chat_id)
        agent = FinanceAgent(session)
        response, updated_history = agent.respond(message, history)
        self.conversation_store.save_history(chat_id, updated_history)
        await update.message.reply_text(response)

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        print("ERROR:")
        print(context.error)
        print(f"Exception while handling update: {context.error}")
        if isinstance(update, Update) and update.effective_message:
            await update.effective_message.reply_text(
                "Sorry, something went wrong while processing your request. Please try again.")

    def run(self):
        application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        application.add_error_handler(self.error_handler)
        application.run_polling()
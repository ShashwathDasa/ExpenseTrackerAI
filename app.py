import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    print(f"User: {user.username}")
    print(f"Chat ID: {update.effective_chat.id}")

    await update.message.reply_text(
        f"Hello {user.first_name}! Your finance bot is working."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    message = update.message.text

    print(f"Username: {user.username}")
    print(f"Chat ID: {chat_id}")
    print(f"Message: {message}")

    await update.message.reply_text(
        f"You said: {message}"
    )


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    print("Bot is running...")

    application.run_polling()


if __name__ == "__main__":
    main()
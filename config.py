import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    GOOGLE_CREDENTIALS_FILE = "google_credentials.json"
    SPREADSHEET_ID = "11cHDTICI7txJrwprEUb1u5nu2WLWScdbx6nOfhWBECU"
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
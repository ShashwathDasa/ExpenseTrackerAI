import gspread

from google.oauth2.service_account import Credentials

from config import Config


class GoogleSheetsClient:

    def __init__(self):
        self.client = self._authenticate()
        self.spreadsheet = self.client.open_by_key(
            Config.SPREADSHEET_ID
        )

    def _authenticate(self):
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]

        credentials = Credentials.from_service_account_file(
            Config.GOOGLE_CREDENTIALS_FILE,
            scopes=scopes,
        )

        return gspread.authorize(credentials)

    def get_worksheet(self, name):
        return self.spreadsheet.worksheet(name)
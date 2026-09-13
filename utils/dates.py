from datetime import datetime


def parse_date(value):
    formats = [
        "%d-%b-%Y",  # Google Sheets: 6-Sep-2026
        "%Y-%m-%d",  # Tool/API: 2026-09-06
    ]

    for date_format in formats:
        try:
            return datetime.strptime(value, date_format)
        except ValueError:
            continue

    raise ValueError(f"Unsupported date format: {value}")
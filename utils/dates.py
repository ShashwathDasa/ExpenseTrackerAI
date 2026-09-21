from datetime import datetime


def parse_date(value):
    formats = ["%d-%b-%Y", "%Y-%m-%d", "%d/%m/%Y", "%d/%m"]

    for date_format in formats:
        try:
            parsed_date = datetime.strptime(value, date_format)
            if date_format == "%d/%m":
                parsed_date = parsed_date.replace(year=datetime.today().year)
            return parsed_date
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {value}")

def parse_amount(value):
    value = value.replace("₹", "").replace(",", "").strip()
    return float(value)
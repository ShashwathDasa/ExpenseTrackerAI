from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def create_option_keyboard(options, callback_prefix, columns=2):
    keyboard = []

    for i in range(0, len(options), columns):
        row = []
        for option in options[i:i + columns]:
            row.append(InlineKeyboardButton(text=option, callback_data=f"{callback_prefix}:{option}"))
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)


def create_confirmation_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="✅ Confirm",
                callback_data="confirm:yes",
            ),
            InlineKeyboardButton(
                text="❌ Cancel",
                callback_data="confirm:no",
            ),
        ]
    ]

    return InlineKeyboardMarkup(keyboard)
from telegram import  InlineKeyboardButton


def build_currency_listing_countdown_post_settings_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="إضافة ➕",
                callback_data="add_currency_listing_countdown_post",
            ),
            InlineKeyboardButton(
                text="حذف 🗑️",
                callback_data="delete_currency_listing_countdown_post",
            ),
        ]
    ]
    return keyboard

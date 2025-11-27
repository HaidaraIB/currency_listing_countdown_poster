from telegram import InlineKeyboardButton


def build_post_scheduling_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="إضافة ➕",
                callback_data="add_post_scheduling",
            ),
            InlineKeyboardButton(
                text="حذف 🗑️",
                callback_data="delete_post_scheduling",
            ),
            InlineKeyboardButton(
                text="تعديل �",
                callback_data="edit_post_scheduling",
            ),
        ]
    ]
    return keyboard


def build_edit_post_scheduling_keyboard(is_paused: bool):
    keyboard = [
        [
            InlineKeyboardButton(
                text="تشغيل الجدولة" if is_paused else "إيقاف الجدولة",
                callback_data="edit_scheduling",
            )
        ],
        [
            InlineKeyboardButton(
                text="تعديل الرسالة",
                callback_data="edit_message",
            ),
            InlineKeyboardButton(
                text="تعديل المجموعة",
                callback_data="edit_group",
            ),
        ],
        [
            InlineKeyboardButton(
                text="تعديل الفاصل الزمني",
                callback_data="edit_interval",
            ),
        ],
    ]
    return keyboard

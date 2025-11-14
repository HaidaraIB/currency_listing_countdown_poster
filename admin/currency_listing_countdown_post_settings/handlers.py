from telegram import (
    Update,
    Chat,
    ReplyKeyboardMarkup,
    KeyboardButtonRequestChat,
    KeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    CommandHandler,
)
from custom_filters import Admin
from common.keyboards import build_back_button, build_back_to_home_page_button
from common.back_to_home_page import back_to_admin_home_page_handler
from start import admin_command
import models


NAME, LOGO, LISTING_DATE, GROUP_ID = range(4)


async def add_currency_listing_countdown_post(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await update.callback_query.edit_message_text(
            text="أرسل اسم العملة",
            reply_markup=InlineKeyboardMarkup(build_back_to_home_page_button()),
        )
        return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.message:
            context.user_data["currency_listing_countdown_post_name"] = (
                update.message.text
            )
        back_buttons = [
            build_back_button("back_to_get_name"),
            build_back_to_home_page_button()[0],
        ]
        await update.message.reply_text(
            text="أرسل لوغو العملة",
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )
        return LOGO


back_to_get_name = add_currency_listing_countdown_post


async def get_logo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.message.photo:
            context.user_data["currency_listing_countdown_post_logo"] = (
                update.message.photo[-1].file_id
            )
        back_buttons = [
            build_back_button("back_to_get_logo"),
            build_back_to_home_page_button()[0],
        ]
        await update.message.reply_text(
            text="أرسل تاريخ الإطلاق",
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )
        return LISTING_DATE


back_to_get_logo = get_name


async def get_listing_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.message:
            context.user_data["currency_listing_countdown_post_listing_date"] = (
                update.message.text
            )
        await update.message.reply_text(
            text=(
                "اختر المجموعة التي سيتم إرسال المنشور فيها بالضغط على الزر أدناه\n\n"
                "أو قم بإرسال ID المجموعة مباشرة\n\n"
                "للرجوع اضغط /back"
            ),
            reply_markup=ReplyKeyboardMarkup(
                keyboard=ReplyKeyboardMarkup.from_button(
                    KeyboardButton(
                        text="اختيار مجموعة",
                        request_chat=KeyboardButtonRequestChat(
                            request_id=6,
                            chat_is_channel=False,
                        ),
                    ),
                ),
                resize_keyboard=True,
            ),
        )
        return GROUP_ID


back_to_get_listing_date = get_logo


async def get_group_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.message.chat_shared:
            group_id = update.message.chat_shared.chat_id
        else:
            group_id = int(update.message.text)
        try:
            chat = await context.bot.get_chat(group_id)
            bot_member = await chat.get_member(context.bot.id)
            if not (bot_member.status in ["administrator", "creator"]):
                await update.message.reply_text(
                    "يجب أن يكون البوت مشرفًا في المجموعة المحددة. يرجى تعيين البوت كمسؤول ثم إعادة المحاولة."
                )
                return
        except Exception:
            await update.message.reply_text(
                "تعذر التحقق من حالة البوت أو المجموعة. تأكد من أن البوت متواجد في المجموعة وأن الرقم صحيح."
            )
            return
        with models.session_scope() as s:
            currency_listing_countdown_post = models.CurrencyListingCountdownPost(
                name=context.user_data["currency_listing_countdown_post_name"],
                logo=context.user_data["currency_listing_countdown_post_logo"],
                listing_date=context.user_data[
                    "currency_listing_countdown_post_listing_date"
                ],
                group_id=group_id,
            )
            s.add(currency_listing_countdown_post)
            s.commit()
        await update.callback_query.edit_message_text(
            text=("تمت إضافة المنشور بنجاح ✅\n\n" "للمتابعة اضغط /admin")
        )
        return ConversationHandler.END


add_currency_listing_countdown_post_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            add_currency_listing_countdown_post,
            pattern="add_currency_listing_countdown_post",
        )
    ],
    states={
        NAME: [
            MessageHandler(
                filters=filters.TEXT,
                callback=get_name,
            )
        ],
        LOGO: [
            MessageHandler(
                filters=filters.PHOTO,
                callback=get_logo,
            )
        ],
        LISTING_DATE: [
            MessageHandler(
                filters=filters.Regex(r"^\d{2}/\d{2}/\d{4}$"),
                callback=get_listing_date,
            )
        ],
        GROUP_ID: [
            MessageHandler(
                filters=filters.StatusUpdate.CHAT_SHARED | filters.Regex(r"-?[0-9]+"),
                callback=get_group_id,
            )
        ],
    },
    fallbacks=[
        admin_command,
        back_to_admin_home_page_handler,
        CommandHandler(
            "back",
            back_to_get_listing_date,
        ),
        CallbackQueryHandler(
            back_to_get_name,
            r"^back_to_get_name$",
        ),
        CallbackQueryHandler(
            back_to_get_logo,
            r"^back_to_get_logo$",
        ),
    ],
)

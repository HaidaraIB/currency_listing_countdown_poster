from telegram import (
    Update,
    Chat,
    ReplyKeyboardMarkup,
    KeyboardButtonRequestChat,
    KeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    CommandHandler,
    filters,
)
from admin.currency_listing_countdown_post_settings.keyboards import (
    build_currency_listing_countdown_post_settings_keyboard,
)
from custom_filters import Admin
from common.keyboards import (
    build_back_button,
    build_back_to_home_page_button,
    build_keyboard,
    build_admin_keyboard,
)
from common.back_to_home_page import back_to_admin_home_page_handler
from common.constants import *
from start import admin_command
import models
from datetime import datetime
from Config import Config

NAME, LOGO, LISTING_DATE, GROUP_ID = range(4)


async def currency_listing_countdown_post_settings(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        keyboard = build_currency_listing_countdown_post_settings_keyboard()
        keyboard.append(build_back_to_home_page_button()[0])
        await update.callback_query.edit_message_text(
            text="إعدادات إعلان التداول 📊",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return ConversationHandler.END


currency_listing_countdown_post_settings_handler = CallbackQueryHandler(
    currency_listing_countdown_post_settings,
    r"^currency_listing_countdown_post_settings$|^back_to_currency_listing_countdown_post_settings$",
)


async def add_currency_listing_countdown_post(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        back_buttons = [
            build_back_button("back_to_currency_listing_countdown_post_settings"),
            build_back_to_home_page_button()[0],
        ]
        await update.callback_query.edit_message_text(
            text="أرسل اسم العملة",
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )
        return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        back_buttons = [
            build_back_button("back_to_get_name"),
            build_back_to_home_page_button()[0],
        ]
        if update.message:
            context.user_data["currency_listing_countdown_post_name"] = (
                update.message.text
            )
            await update.message.reply_text(
                text="أرسل لوغو العملة",
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
        else:
            await update.callback_query.edit_message_text(
                text="أرسل لوغو العملة",
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
        return LOGO


back_to_get_name = add_currency_listing_countdown_post


async def get_logo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        back_buttons = [
            build_back_button("back_to_get_logo"),
            build_back_to_home_page_button()[0],
        ]
        if update.message.photo:
            context.user_data["currency_listing_countdown_post_logo"] = (
                update.message.photo[-1].file_id
            )
            await update.message.reply_text(
                text="أرسل تاريخ الإطلاق بالصيغة <b>DD/MM/YYYY HH:MM</b>",
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
        else:
            await update.callback_query.edit_message_text(
                text="أرسل تاريخ الإطلاق بالصيغة <b>DD/MM/YYYY HH:MM</b>",
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
        return LISTING_DATE


back_to_get_logo = get_name


async def get_listing_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        context.user_data["currency_listing_countdown_post_listing_date"] = (
            update.message.text
        )
        await update.message.reply_text(
            text=(
                "اختر المجموعة التي سيتم إرسال المنشور فيها بالضغط على الزر أدناه\n\n"
                "أو قم بإرسال ID المجموعة مباشرة\n\n"
                "للرجوع اضغط /back"
            ),
            reply_markup=ReplyKeyboardMarkup.from_button(
                KeyboardButton(
                    text="اختيار مجموعة",
                    request_chat=KeyboardButtonRequestChat(
                        request_id=6,
                        chat_is_channel=False,
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
            if bot_member.status not in ["administrator", "creator"]:
                await update.message.reply_text(
                    "يجب أن يكون البوت مشرفًا في المجموعة المحددة. يرجى تعيين البوت كمسؤول ثم إعادة المحاولة."
                )
                return
        except:
            await update.message.reply_text(
                "تعذر التحقق من حالة البوت أو المجموعة. تأكد من أن البوت متواجد في المجموعة وأن الرقم صحيح."
            )
            return
        with models.session_scope() as s:
            logo_message = await context.bot.send_photo(
                chat_id=Config.LOGOS_CHANNEL,
                photo=context.user_data["currency_listing_countdown_post_logo"],
            )
            currency_listing_countdown_post = models.CurrencyListingCountdownPost(
                name=context.user_data["currency_listing_countdown_post_name"],
                logo=logo_message.photo[-1].file_id,
                listing_date=datetime.strptime(
                    context.user_data["currency_listing_countdown_post_listing_date"],
                    "%d/%m/%Y %H:%M",
                ),
                group_id=group_id,
            )
            s.add(currency_listing_countdown_post)
            s.commit()
        await update.message.reply_text(
            text="تمت إضافة المنشور بنجاح ✅",
            reply_markup=ReplyKeyboardRemove(),
        )
        await update.message.reply_text(
            text=HOME_PAGE_TEXT,
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


add_currency_listing_countdown_post_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            add_currency_listing_countdown_post,
            r"^add_currency_listing_countdown_post$",
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
                filters=filters.Regex(r"^\d{2}/\d{2}/\d{4} \d{2}:\d{2}$"),
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
        currency_listing_countdown_post_settings_handler,
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


POST_TO_DELETE = range(1)


async def delete_currency_listing_countdown_post(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        with models.session_scope() as s:
            posts = s.query(models.CurrencyListingCountdownPost).all()
            if not posts:
                await update.callback_query.answer(
                    text="لا يوجد منشورات ❗️",
                    show_alert=True,
                )
                return ConversationHandler.END
            keyboard = build_keyboard(
                columns=1,
                texts=[post.name for post in posts],
                buttons_data=[post.id for post in posts],
            )
            keyboard.append(
                build_back_button("back_to_currency_listing_countdown_post_settings")
            )
            keyboard.append(build_back_to_home_page_button()[0])
            await update.callback_query.edit_message_text(
                text=(
                    "اختر المنشور الذي تريد حذفه\n\n"
                    "<i><b>تنبيه</b></i>: سيتم حذف المنشور من المجموعة أيضاً"
                ),
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            return POST_TO_DELETE


async def choose_post_to_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        post_id = int(update.callback_query.data)
        with models.session_scope() as s:
            post = s.get(models.CurrencyListingCountdownPost, post_id)
            try:
                await context.bot.delete_message(
                    chat_id=post.group_id,
                    message_id=post.post_message_id,
                )
            except:
                pass
            s.delete(post)
            s.commit()
        await update.callback_query.answer(
            text="تم حذف المنشور بنجاح ✅",
            show_alert=True,
        )
        await update.callback_query.edit_message_text(
            text=HOME_PAGE_TEXT,
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


delete_currency_listing_countdown_post_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            delete_currency_listing_countdown_post,
            r"^delete_currency_listing_countdown_post$",
        )
    ],
    states={
        POST_TO_DELETE: [
            CallbackQueryHandler(
                choose_post_to_delete,
                r"^[0-9]+$",
            )
        ]
    },
    fallbacks=[
        admin_command,
        back_to_admin_home_page_handler,
        currency_listing_countdown_post_settings_handler,
    ],
)

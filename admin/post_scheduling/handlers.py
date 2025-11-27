from telegram import (
    Update,
    Chat,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    KeyboardButtonRequestChat,
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
from common.constants import HOME_PAGE_TEXT
from custom_filters import Admin
from start import admin_command
from admin.post_scheduling.keyboards import (
    build_post_scheduling_keyboard,
    build_edit_post_scheduling_keyboard,
)
from common.keyboards import (
    build_back_to_home_page_button,
    build_back_button,
    build_admin_keyboard,
    build_keyboard,
)
from common.back_to_home_page import back_to_admin_home_page_handler
from Config import Config
import models
from jobs import post_scheduling_poster
from datetime import datetime


async def post_scheduling_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await update.callback_query.answer()
        keyboard = build_post_scheduling_keyboard()
        keyboard.append(build_back_to_home_page_button()[0])
        await update.callback_query.edit_message_text(
            text="إعدادات المنشورات المجدولة 📊",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return ConversationHandler.END


post_scheduling_settings_handler = CallbackQueryHandler(
    post_scheduling_settings,
    r"^post_scheduling_settings$|^back_to_post_scheduling_settings$",
)

MESSAGE, INTERVAL, GROUP_ID = range(3)


async def add_post_scheduling(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        back_buttons = [
            build_back_button("back_to_post_scheduling_settings"),
            build_back_to_home_page_button()[0],
        ]
        await update.callback_query.edit_message_text(
            text="أرسل الرسالة المجدولة",
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )
        return MESSAGE


async def get_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        back_buttons = [
            build_back_button("back_to_message"),
            build_back_to_home_page_button()[0],
        ]
        if update.message.photo:
            context.user_data["post_scheduling_message_photo"] = update.message.photo[
                -1
            ].file_id
            context.user_data["post_scheduling_message_text"] = (
                update.message.caption_html
            )
        elif update.message.text != "/back":
            context.user_data["post_scheduling_message_photo"] = None
            context.user_data["post_scheduling_message_text"] = update.message.text_html
        await update.message.reply_text(
            text="أرسل الفاصل الزمني بالدقائق",
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )
        return INTERVAL


back_to_message = add_post_scheduling


async def get_interval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.message:
            context.user_data["post_scheduling_interval"] = (
                int(update.message.text) * 60
            )
        else:
            await update.callback_query.delete_message()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                "اختر المجموعة/القناة التي سيتم إرسال المنشور فيها بالضغط على الزر أدناه\n\n"
                "أو قم بإرسال ID مباشرة\n\n"
                "للرجوع اضغط /back"
            ),
            reply_markup=ReplyKeyboardMarkup.from_row(
                [
                    KeyboardButton(
                        text="اختيار مجموعة",
                        request_chat=KeyboardButtonRequestChat(
                            request_id=7,
                            chat_is_channel=False,
                        ),
                    ),
                    KeyboardButton(
                        text="اختيار قناة",
                        request_chat=KeyboardButtonRequestChat(
                            request_id=8,
                            chat_is_channel=True,
                        ),
                    ),
                ],
                resize_keyboard=True,
            ),
        )
        return GROUP_ID


back_to_get_interval = get_message


async def get_group_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        group_title = None
        if update.message.chat_shared:
            group_id = update.message.chat_shared.chat_id
        else:
            group_id = int(update.message.text)
        try:
            chat = await context.bot.get_chat(group_id)
            bot_member = await chat.get_member(context.bot.id)
            if bot_member.status not in ["administrator", "creator"]:
                await update.message.reply_text(
                    "يجب أن يكون البوت مشرفًا في المجموعة/القناة المحددة. يرجى تعيين البوت كمسؤول ثم إعادة المحاولة."
                )
                return
            group_title = chat.title
        except:
            await update.message.reply_text(
                "تعذر التحقق من حالة البوت أو المجموعة/القناة. تأكد من أن البوت متواجد في المجموعة/القناة وأن الرقم صحيح."
            )
            return

        with models.session_scope() as s:
            photo_file_id = None
            if context.user_data["post_scheduling_message_photo"]:
                photo_message = await context.bot.send_photo(
                    chat_id=Config.LOGOS_CHANNEL,
                    photo=context.user_data["post_scheduling_message_photo"],
                )
                photo_file_id = photo_message.photo[-1].file_id
            post = models.SchedulingPost(
                text=context.user_data["post_scheduling_message_text"],
                photo=photo_file_id,
                interval=context.user_data["post_scheduling_interval"],
                group_id=group_id,
                group_title=group_title,
            )
            s.add(post)
            s.commit()
            context.job_queue.run_repeating(
                callback=post_scheduling_poster,
                interval=post.interval,
                name=f"post_scheduling_poster_{post.id}",
                user_id=update.effective_user.id,
                chat_id=update.effective_chat.id,
                data={"post_id": post.id},
                job_kwargs={
                    "id": f"post_scheduling_poster_{post.id}",
                    "replace_existing": True,
                    "misfire_grace_time": None,
                },
            )
        await update.message.reply_text(
            text="تمت إضافة المنشور بنجاح ✅",
            reply_markup=ReplyKeyboardRemove(),
        )
        await update.message.reply_text(
            text=HOME_PAGE_TEXT,
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


add_post_scheduling_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            add_post_scheduling,
            r"^add_post_scheduling$",
        )
    ],
    states={
        MESSAGE: [
            MessageHandler(
                filters=(filters.TEXT & ~filters.COMMAND) | filters.PHOTO,
                callback=get_message,
            )
        ],
        INTERVAL: [
            MessageHandler(
                filters=filters.Regex(r"^[0-9]+$"),
                callback=get_interval,
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
        post_scheduling_settings_handler,
        CommandHandler("back", back_to_get_interval),
        CallbackQueryHandler(back_to_message, r"^back_to_message$"),
    ],
)


POST_TO_DELETE = range(1)


async def delete_post_scheduling(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        with models.session_scope() as s:
            posts = s.query(models.SchedulingPost).all()
            if not posts:
                await update.callback_query.answer(
                    text="لا يوجد منشورات مجدولة",
                    show_alert=True,
                )
                return ConversationHandler.END
            keyboard = build_keyboard(
                columns=1,
                texts=[post.text for post in posts],
                buttons_data=[post.id for post in posts],
            )
            keyboard.append(build_back_button("back_to_post_scheduling_settings"))
            keyboard.append(build_back_to_home_page_button()[0])
            await update.callback_query.edit_message_text(
                text="اختر المنشور الذي تريد حذفه وإلغاء جدولته",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            return POST_TO_DELETE


async def choose_post_to_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        post_id = int(update.callback_query.data)
        with models.session_scope() as s:
            post = s.get(models.SchedulingPost, post_id)
            jobs = context.job_queue.get_jobs_by_name(
                f"post_scheduling_poster_{post.id}"
            )
            if jobs:
                for job in jobs:
                    job.schedule_removal()
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


delete_post_scheduling_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            delete_post_scheduling,
            r"^delete_post_scheduling$",
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
        post_scheduling_settings_handler,
    ],
)

POST_TO_EDIT, FIELD_TO_EDIT, NEW_VALUE = range(3)


async def edit_post_scheduling(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        with models.session_scope() as s:
            posts = s.query(models.SchedulingPost).all()
            if not posts:
                await update.callback_query.answer(
                    text="لا يوجد منشورات مجدولة",
                    show_alert=True,
                )
                return ConversationHandler.END
            keyboard = build_keyboard(
                columns=1,
                texts=[post.text for post in posts],
                buttons_data=[post.id for post in posts],
            )
            keyboard.append(build_back_button("back_to_post_scheduling_settings"))
            keyboard.append(build_back_to_home_page_button()[0])
            await update.callback_query.edit_message_text(
                text="اختر المنشور الذي تريد تعديله",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            return POST_TO_EDIT


async def choose_post_to_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if not update.callback_query.data.startswith("back"):
            post_id = int(update.callback_query.data)
            context.user_data["post_to_edit_id"] = post_id
        with models.session_scope() as s:
            post = s.get(models.SchedulingPost, post_id)
            keyboard = build_edit_post_scheduling_keyboard(is_paused=post.is_paused)
            keyboard.append(build_back_button("back_to_choose_post_to_edit"))
            keyboard.append(build_back_to_home_page_button()[0])
            await update.callback_query.edit_message_text(
                text=str(post) + f"\n\nاختر الحقل الذي تريد تعديله",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            return FIELD_TO_EDIT


back_to_choose_post_to_edit = edit_post_scheduling


async def choose_field_to_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        back_buttons = [
            build_back_button("back_to_choose_field_to_edit"),
            build_back_to_home_page_button()[0],
        ]

        if not update.callback_query.data.startswith("back"):
            field_to_edit = update.callback_query.data
            context.user_data["field_to_edit"] = field_to_edit
        else:
            field_to_edit = context.user_data["field_to_edit"]
        if field_to_edit == "edit_scheduling":
            post_id = context.user_data["post_to_edit_id"]
            with models.session_scope() as s:
                post = s.get(models.SchedulingPost, post_id)
                if post.is_paused:
                    context.job_queue.run_repeating(
                        callback=post_scheduling_poster,
                        interval=post.interval,
                        name=f"post_scheduling_poster_{post.id}",
                        user_id=update.effective_user.id,
                        chat_id=update.effective_chat.id,
                        data={"post_id": post.id},
                        job_kwargs={
                            "id": f"post_scheduling_poster_{post.id}",
                            "replace_existing": True,
                            "misfire_grace_time": None,
                        },
                    )
                    post.is_paused = False
                else:
                    jobs = context.job_queue.get_jobs_by_name(
                        f"post_scheduling_poster_{post.id}"
                    )
                    if jobs:
                        for job in jobs:
                            job.schedule_removal()
                    post.is_paused = True
                s.commit()
                keyboard = build_edit_post_scheduling_keyboard(is_paused=post.is_paused)
                keyboard.append(build_back_button("back_to_choose_post_to_edit"))
                keyboard.append(build_back_to_home_page_button()[0])
                await update.callback_query.answer(
                    text="تم تعديل حالة الجدولة بنجاح ✅",
                    show_alert=True,
                )
                await update.callback_query.edit_message_text(
                    text=str(post) + f"\n\nاختر الحقل الذي تريد تعديله",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                )
                return FIELD_TO_EDIT
        elif field_to_edit == "edit_message":
            text = "أرسل الرسالة الجديدة"
        elif field_to_edit == "edit_scheduling":
            text = "أرسل الرسالة الجديدة"
        elif field_to_edit == "edit_interval":
            text = "أرسل الفاصل الزمني الجديد بالدقائق"
        elif field_to_edit == "edit_group":
            await update.callback_query.delete_message()
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="اختر المجموعة/القناة الجديدة",
                reply_markup=ReplyKeyboardMarkup.from_row(
                    [
                        KeyboardButton(
                            text="اختيار مجموعة",
                            request_chat=KeyboardButtonRequestChat(
                                request_id=9,
                                chat_is_channel=False,
                            ),
                        ),
                        KeyboardButton(
                            text="اختيار قناة",
                            request_chat=KeyboardButtonRequestChat(
                                request_id=10,
                                chat_is_channel=True,
                            ),
                        ),
                    ],
                    resize_keyboard=True,
                ),
            )
            return NEW_VALUE
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )
        return NEW_VALUE


back_to_choose_field_to_edit = choose_post_to_edit


async def get_new_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        field_to_edit = context.user_data["field_to_edit"]
        post_id = context.user_data["post_to_edit_id"]
        with models.session_scope() as s:
            post = s.get(models.SchedulingPost, post_id)
            if field_to_edit == "edit_message":
                if update.message.photo:
                    post.photo = update.message.photo[-1].file_id
                    post.text = update.message.caption_html
                elif update.message.text != "/back":
                    post.photo = None
                    post.text = update.message.text_html
            elif field_to_edit == "edit_interval":
                new_interval = int(update.message.text) * 60
                post.interval = new_interval
                jobs = context.job_queue.get_jobs_by_name(
                    f"post_scheduling_poster_{post.id}"
                )
                if jobs:
                    for job in jobs:
                        job.schedule_removal()
                context.job_queue.run_repeating(
                    callback=post_scheduling_poster,
                    interval=new_interval,
                    name=f"post_scheduling_poster_{post.id}",
                    user_id=update.effective_user.id,
                    chat_id=update.effective_chat.id,
                    data={"post_id": post.id},
                    job_kwargs={
                        "id": f"post_scheduling_poster_{post.id}",
                        "replace_existing": True,
                        "misfire_grace_time": None,
                    },
                )
            elif field_to_edit == "edit_group":
                new_group_title = None
                if update.message.chat_shared:
                    new_group_id = update.message.chat_shared.chat_id
                else:
                    new_group_id = int(update.message.text)
                try:
                    chat = await context.bot.get_chat(new_group_id)
                    bot_member = await chat.get_member(context.bot.id)
                    if bot_member.status not in ["administrator", "creator"]:
                        await update.message.reply_text(
                            "يجب أن يكون البوت مشرفًا في المجموعة/القناة المحددة. يرجى تعيين البوت كمسؤول ثم إعادة المحاولة."
                        )
                        return
                    new_group_title = chat.title
                except:
                    await update.message.reply_text(
                        "تعذر التحقق من حالة البوت أو المجموعة/القناة. تأكد من أن البوت متواجد في المجموعة/القناة وأن الرقم صحيح."
                    )
                    return
                post.group_id = new_group_id
                post.group_title = new_group_title
            post.updated_at = datetime.now()
            s.commit()

        await update.message.reply_text(
            text="تم تعديل المنشور بنجاح ✅",
            reply_markup=ReplyKeyboardRemove(),
        )
        await update.message.reply_text(
            text=HOME_PAGE_TEXT,
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


edit_post_scheduling_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            edit_post_scheduling,
            r"^edit_post_scheduling$",
        )
    ],
    states={
        POST_TO_EDIT: [
            CallbackQueryHandler(
                choose_post_to_edit,
                r"^[0-9]+$",
            )
        ],
        FIELD_TO_EDIT: [
            CallbackQueryHandler(
                choose_field_to_edit,
                r"^edit_((message)|(interval)|(group)|(scheduling))$",
            )
        ],
        NEW_VALUE: [
            MessageHandler(
                filters=(
                    (filters.StatusUpdate.CHAT_SHARED | filters.Regex(r"-?[0-9]+"))
                    | (
                        (filters.TEXT & ~filters.COMMAND)
                        | filters.PHOTO
                        | filters.Document.GIF
                    )
                    | filters.Regex(r"^[0-9]+$")
                ),
                callback=get_new_value,
            )
        ],
    },
    fallbacks=[
        admin_command,
        back_to_admin_home_page_handler,
        post_scheduling_settings_handler,
        CallbackQueryHandler(
            back_to_choose_post_to_edit, r"^back_to_choose_post_to_edit$"
        ),
        CallbackQueryHandler(
            back_to_choose_field_to_edit, r"^back_to_choose_field_to_edit$"
        ),
    ],
)

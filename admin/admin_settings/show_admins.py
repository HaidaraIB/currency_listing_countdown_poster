from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from common.constants import *
import os
import models


async def show_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with models.session_scope() as s:
        admins = s.query(models.User).filter(models.User.is_admin == True).all()
        text = ""
        for admin in admins:
            if admin.user_id == int(os.getenv("OWNER_ID")):
                text += "<b>مالك البوت</b>\n" + str(admin)
                continue
            text += str(admin)
    text += "للمتابعة اضغط /admin"
    await update.callback_query.edit_message_text(text=text)


show_admins_handler = CallbackQueryHandler(
    callback=show_admins,
    pattern="^show_admins$",
)

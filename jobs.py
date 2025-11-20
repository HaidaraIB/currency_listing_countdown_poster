from telegram.ext import ContextTypes
from telegram.error import RetryAfter, BadRequest, ChatMigrated
import models
import asyncio
from sqlalchemy.orm import Session
import traceback
from common.error_handler import write_error


async def currency_listing_countdown_poster_and_updater(
    context: ContextTypes.DEFAULT_TYPE,
):
    with models.session_scope() as s:
        posts = s.query(models.CurrencyListingCountdownPost).all()
        for post in posts:
            try:
                await post_or_update(context, post.id, s)
            except RetryAfter as r:
                await asyncio.sleep(r.retry_after)
                await post_or_update(context, post.id, s)
            except BadRequest as b:
                if "Message to edit not found" in str(b):
                    post.is_posted = False
                    post.post_message_id = None
                    s.commit()
                elif "Not enough rights to manage pinned messages in the chat" in str(b):
                    post.is_pinned = False
                    s.commit()
            except ChatMigrated as cm:
                post.group_id = cm.new_chat_id
                s.commit()
            except Exception as e:
                tb_list = traceback.format_exception(None, e, e.__traceback__)
                tb_string = "".join(tb_list)
                write_error(tb_string)


async def post_or_update(context: ContextTypes.DEFAULT_TYPE, post_id: int, s: Session):
    post = s.get(models.CurrencyListingCountdownPost, post_id)
    post_message_id = post.post_message_id
    if not post.is_posted:
        post_message = await context.bot.send_photo(
            chat_id=post.group_id,
            photo=post.logo,
            caption=str(post),
        )
        post_message_id = post_message.message_id
        post.is_posted = True
        post.post_message_id = post_message_id
        s.commit()
    else:
        await context.bot.edit_message_caption(
            chat_id=post.group_id,
            message_id=post_message_id,
            caption=str(post),
        )
    if not post.is_pinned:
        await context.bot.pin_chat_message(
            chat_id=post.group_id,
            message_id=post_message_id,
        )
        post.is_pinned = True
        s.commit()

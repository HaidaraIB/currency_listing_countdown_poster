
from telegram.ext import ContextTypes
from telegram.error import RetryAfter, ChatMigrated, BadRequest
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
            except ChatMigrated as cm:
                post.group_id = cm.new_chat_id
                s.commit()
            except Exception as e:
                tb_list = traceback.format_exception(None, e, e.__traceback__)
                tb_string = "".join(tb_list)
                write_error(tb_string)


async def post_or_update(context: ContextTypes.DEFAULT_TYPE, post_id: int, s: Session):
    post = s.get(models.CurrencyListingCountdownPost, post_id)
    if post.is_posted:
        try:
            await context.bot.delete_message(
                chat_id=post.group_id,
                message_id=post.post_message_id,
            )
        except BadRequest as b:
            if "Message can't be deleted" in str(b):
                pass
    post_message = await context.bot.send_photo(
        chat_id=post.group_id,
        photo=post.logo,
        caption=str(post),
    )
    if not post.is_posted:
        post.is_posted = True
    post.post_message_id = post_message.message_id
    s.commit()


async def post_scheduling_poster(
    context: ContextTypes.DEFAULT_TYPE,
):
    post_id = context.job.data["post_id"]
    with models.session_scope() as s:
        post = s.get(models.SchedulingPost, post_id)
        if post.photo:
            await context.bot.send_photo(
                chat_id=post.group_id,
                photo=post.photo,
                caption=post.text,
            )
        elif post.doc:
            await context.bot.send_document(
                chat_id=post.group_id,
                document=post.doc,
                caption=post.text,
            )
        else:
            await context.bot.send_message(
                chat_id=post.group_id,
                text=post.text,
            )

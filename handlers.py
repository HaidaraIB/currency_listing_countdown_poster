from telegram import Update
from start import start_command, admin_command
from common.common import create_folders
from common.back_to_home_page import (
    back_to_admin_home_page_handler,
    back_to_user_home_page_handler,
)
from common.error_handler import error_handler
from common.force_join import check_joined_handler

from user.user_calls import *
from user.user_settings import *

from admin.admin_calls import *
from admin.admin_settings import *
from admin.broadcast import *
from admin.ban import *
from admin.currency_listing_countdown_post_settings import *

from models import init_db
from jobs import currency_listing_countdown_poster_and_updater
from MyApp import MyApp


def setup_and_run():
    create_folders()
    init_db()

    app = MyApp.build_app()

    app.add_handler(add_currency_listing_countdown_post_handler)
    app.add_handler(delete_currency_listing_countdown_post_handler)
    app.add_handler(currency_listing_countdown_post_settings_handler)

    app.add_handler(user_settings_handler)
    app.add_handler(change_lang_handler)

    # ADMIN SETTINGS
    app.add_handler(show_admins_handler)
    app.add_handler(add_admin_handler)
    app.add_handler(remove_admin_handler)
    app.add_handler(admin_settings_handler)

    app.add_handler(broadcast_message_handler)

    app.add_handler(check_joined_handler)

    app.add_handler(ban_unban_user_handler)

    app.add_handler(admin_command)
    app.add_handler(start_command)
    app.add_handler(find_id_handler)
    app.add_handler(hide_ids_keyboard_handler)
    app.add_handler(back_to_user_home_page_handler)
    app.add_handler(back_to_admin_home_page_handler)

    app.add_error_handler(error_handler)

    app.job_queue.run_repeating(
        currency_listing_countdown_poster_and_updater,
        interval=60,
        job_kwargs={
            "id": "currency_listing_countdown_poster_and_updater",
            "replace_existing": True,
        },
    )

    app.run_polling(allowed_updates=Update.ALL_TYPES)

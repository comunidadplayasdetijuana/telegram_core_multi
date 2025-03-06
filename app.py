#!/usr/bin/env python
import logging
import asyncio
from telegram import Update
from telegram.ext import Application
from lib import (
    lib_telegram_cmds,
    lib_telegram_usr_settings,
    lib_telegram_admin,
    lib_telegram_pyramid,
    lib_settings
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

def main() -> None:
    application = Application.builder().token(lib_settings.API_KEY).build()

    # Command handlers
    application.add_handler(lib_telegram_cmds.start_handler())
    application.add_handler(lib_telegram_cmds.help_handler())
    application.add_handler(lib_telegram_cmds.cmds_handler())
    application.add_handler(lib_telegram_cmds.photo_handler())


    # User handlers
    application.add_handler(lib_telegram_usr_settings.register_handler())
    application.add_handler(lib_telegram_usr_settings.config_handler())
    application.add_handler(lib_telegram_usr_settings.credits_handler())


    # User Pyramid Reference
    application.add_handler(lib_telegram_pyramid.gen_ref_handler())


    # Admin handlers
    application.add_handler(lib_telegram_admin.credit_handler())
    application.add_handler(lib_telegram_admin.ban_handler())
    application.add_handler(lib_telegram_admin.message_handler())

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    asyncio.run(main())

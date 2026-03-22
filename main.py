"""
Bot entry point.
Starts the Telegram application and background pollers.
"""
from __future__ import annotations

import asyncio
import logging

import aiohttp
from telegram.ext import Application, CommandHandler

from config import DB_PATH, TELEGRAM_TOKEN
from database import init_db
from handlers import (
    add_pro_player,
    help_command,
    list_pros,
    load_pros,
    player_stats,
    remove_pro_player,
    set_summoner,
    start,
    status,
    toggle_notifs,
)
from logging_setup import setup_logging
from poller import poll_pros, poll_users

setup_logging()
logger = logging.getLogger(__name__)


async def main() -> None:
    await init_db(DB_PATH)

    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN not set — aborting")
        return

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("set_summoner", set_summoner))
    # Keep old command as alias for backwards compat
    app.add_handler(CommandHandler("set_lol_summoner", set_summoner))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("toggle", toggle_notifs))
    # Keep old command as alias
    app.add_handler(CommandHandler("stop_notifications", toggle_notifs))
    app.add_handler(CommandHandler("stats", player_stats))
    app.add_handler(CommandHandler("add_pro", add_pro_player))
    app.add_handler(CommandHandler("list_pros", list_pros))
    app.add_handler(CommandHandler("remove_pro", remove_pro_player))
    app.add_handler(CommandHandler("load_pros", load_pros))

    async with aiohttp.ClientSession() as session:
        async with app:
            await app.start()
            await app.updater.start_polling()

            user_task = asyncio.create_task(poll_users(session, app.bot, DB_PATH))
            pro_task = asyncio.create_task(poll_pros(session, app.bot, DB_PATH))

            logger.info("Bot started. Polling active.")
            try:
                # Run until interrupted
                await asyncio.Event().wait()
            finally:
                user_task.cancel()
                pro_task.cancel()
                await app.updater.stop()
                await app.stop()


if __name__ == "__main__":
    asyncio.run(main())

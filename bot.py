import logging
import os
import sqlite3
from contextlib import contextmanager

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_NAME = "Drew Bot"
DB_PATH = os.getenv("DATABASE_PATH", "tasks.db")
TOKEN = os.getenv("BOT_TOKEN")
START_MESSAGE = "Get XAUUSD Daily 5-8 Free Signals Free Available Join Now 👊👇👇👇👇https://t.me/Drewcommunity"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


@contextmanager
def db():
    connection = sqlite3.connect(DB_PATH)
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()
        yield connection
    finally:
        connection.close()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(START_MESSAGE)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Unhandled bot error", exc_info=context.error)


def run() -> None:
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN environment variable is required")

    with db():
        pass

    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_error_handler(error_handler)

    logger.info("Starting %s", BOT_NAME)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    run()

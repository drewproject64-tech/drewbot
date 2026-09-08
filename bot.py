import logging
import os

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_NAME = "Drew Bot"
TOKEN = os.getenv("BOT_TOKEN")

START_MESSAGE = (
    "Get XAUUSD Daily 5-8 Free Signals Free Available Join Now 👊👇👇👇👇"
    "https://t.me/Drewcommunity"
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send only the requested promotional message."""
    if update.message:
        await update.message.reply_text(START_MESSAGE)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Unhandled bot error", exc_info=context.error)


def run() -> None:
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN environment variable is required")

    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_error_handler(error_handler)

    logger.info("Starting %s", BOT_NAME)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    run()

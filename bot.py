import logging
import os
import sqlite3
from contextlib import contextmanager

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

BOT_NAME = "Drew Bot"
DB_PATH = os.getenv("DATABASE_PATH", "tasks.db")
TOKEN = os.getenv("BOT_TOKEN")

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


def add_task(user_id: int, text: str) -> None:
    with db() as connection:
        connection.execute("INSERT INTO tasks (user_id, text) VALUES (?, ?)", (user_id, text))
        connection.commit()


def get_tasks(user_id: int):
    with db() as connection:
        return connection.execute(
            "SELECT id, text, completed FROM tasks WHERE user_id = ? ORDER BY completed, id DESC",
            (user_id,),
        ).fetchall()


def set_completed(user_id: int, task_id: int) -> bool:
    with db() as connection:
        cursor = connection.execute(
            "UPDATE tasks SET completed = 1 WHERE id = ? AND user_id = ? AND completed = 0",
            (task_id, user_id),
        )
        connection.commit()
        return cursor.rowcount > 0


def delete_task(user_id: int, task_id: int) -> bool:
    with db() as connection:
        cursor = connection.execute(
            "DELETE FROM tasks WHERE id = ? AND user_id = ?",
            (task_id, user_id),
        )
        connection.commit()
        return cursor.rowcount > 0


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("➕ Add Task", callback_data="add")],
            [InlineKeyboardButton("📋 My Tasks", callback_data="list")],
            [InlineKeyboardButton("❓ How to Use", callback_data="help")],
        ]
    )


def task_keyboard(tasks) -> InlineKeyboardMarkup:
    rows = []
    for task_id, text, completed in tasks:
        if not completed:
            rows.append([InlineKeyboardButton(f"✅ {text[:35]}", callback_data=f"done:{task_id}")])
        rows.append([InlineKeyboardButton(f"🗑️ Delete: {text[:30]}", callback_data=f"delete:{task_id}")])
    rows.append([InlineKeyboardButton("⬅️ Main Menu", callback_data="menu")])
    return InlineKeyboardMarkup(rows)


def format_tasks(tasks) -> str:
    if not tasks:
        return "📋 <b>Your Tasks</b>\n\nYou don't have any tasks yet."

    lines = ["📋 <b>Your Tasks</b>", ""]
    for index, (_, text, completed) in enumerate(tasks, start=1):
        marker = "✅" if completed else "⬜"
        lines.append(f"{index}. {marker} {text}")
    return "\n".join(lines)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop("awaiting_task", None)
    await update.message.reply_text(
        "👋 <b>Welcome to Drew Bot!</b>\n\n"
        "A simple to-do list utility that helps you organize tasks directly in Telegram.\n\n"
        "➕ <b>Add Task</b> — Save something you need to do.\n"
        "📋 <b>My Tasks</b> — View and manage your saved tasks.\n\n"
        "Choose an option below to get started.",
        parse_mode="HTML",
        reply_markup=main_menu(),
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    action = query.data

    if action == "add":
        context.user_data["awaiting_task"] = True
        await query.edit_message_text(
            "➕ <b>Add Task</b>\n\nSend me the task you want to save.\n\n"
            "Example: <i>Finish the project proposal</i>\n\n"
            "Send /cancel to stop.",
            parse_mode="HTML",
        )
        return

    if action == "list":
        tasks = get_tasks(user_id)
        await query.edit_message_text(
            format_tasks(tasks), parse_mode="HTML", reply_markup=task_keyboard(tasks)
        )
        return

    if action == "help":
        await query.edit_message_text(
            "❓ <b>How to Use Drew Bot</b>\n\n"
            "1. Tap <b>➕ Add Task</b> and send your task.\n"
            "2. Tap <b>📋 My Tasks</b> to see your list.\n"
            "3. Tap a task's ✅ button to mark it completed.\n"
            "4. Use 🗑️ to delete a task.\n\n"
            "Your tasks are stored separately for your Telegram account.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Main Menu", callback_data="menu")]]),
        )
        return

    if action == "menu":
        await query.edit_message_text(
            "👋 <b>Drew Bot</b>\n\nWhat would you like to do?",
            parse_mode="HTML",
            reply_markup=main_menu(),
        )
        return

    if action.startswith("done:"):
        task_id = int(action.split(":", 1)[1])
        set_completed(user_id, task_id)
        tasks = get_tasks(user_id)
        await query.edit_message_text(
            format_tasks(tasks), parse_mode="HTML", reply_markup=task_keyboard(tasks)
        )
        return

    if action.startswith("delete:"):
        task_id = int(action.split(":", 1)[1])
        delete_task(user_id, task_id)
        tasks = get_tasks(user_id)
        await query.edit_message_text(
            format_tasks(tasks), parse_mode="HTML", reply_markup=task_keyboard(tasks)
        )


async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.user_data.get("awaiting_task"):
        await update.message.reply_text("Please choose an option below.", reply_markup=main_menu())
        return

    text = update.message.text.strip()
    if not text:
        await update.message.reply_text("Please send a task with some text.")
        return

    add_task(update.effective_user.id, text)
    context.user_data.pop("awaiting_task", None)
    await update.message.reply_text(
        f"✅ <b>Task added!</b>\n\n{text}",
        parse_mode="HTML",
        reply_markup=main_menu(),
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop("awaiting_task", None)
    await update.message.reply_text("Cancelled.", reply_markup=main_menu())


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Unhandled bot error", exc_info=context.error)


def run() -> None:
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN environment variable is required")

    with db():
        pass

    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message))
    application.add_error_handler(error_handler)

    logger.info("Starting %s", BOT_NAME)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    run()

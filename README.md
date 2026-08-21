# Drew Bot 🤖

Telegram to-do list bot for **@Drew_AcademyBot**.

## Features

- ➕ Add tasks
- 📋 View personal tasks
- ✅ Mark tasks complete
- 🗑️ Delete tasks
- ❓ Built-in usage guide
- Per-user task storage with SQLite

## Run locally

1. Create a bot with [@BotFather](https://t.me/BotFather) and obtain the bot token.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set the token:

```bash
export BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
```

On Windows PowerShell:

```powershell
$env:BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
```

4. Start the bot:

```bash
python bot.py
```

The bot uses `tasks.db` by default. Set `DATABASE_PATH` to use another SQLite path.

## Bot profile

- **Name:** Drew Bot
- **Username:** @Drew_AcademyBot

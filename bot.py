import aiosqlite
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"Hii ni demo! Karibu {user.first_name}.")

if __name__ == '__main__':
    app = ApplicationBuilder().token("8192573503:AAGkm4M2XV922PViP8Gc2cVQEWoP0MVwvMI").build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()
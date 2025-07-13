import aiosqlite
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 🔐 Bot Token
TOKEN = "8192573503:AAGkm4M2XV922PViP8Gc2cVQEWoP0MVwvMI"

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name

    async with aiosqlite.connect("database.db") as db:
        await db.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, points INTEGER)")
        await db.commit()

        cursor = await db.execute("SELECT points FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()

        if row is None:
            await db.execute("INSERT INTO users (user_id, points) VALUES (?, ?)", (user_id, 1000))
            await db.commit()
            await update.message.reply_text(
                f"Hii ni demo! Karibu {first_name}.\n\n🎁 Umepewa 1000 points bure!"
            )
        else:
            await update.message.reply_text(
                f"Karibu tena {first_name}!\n\n📌 Points zako: {row[0]}"
            )

# /videos
async def videos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Orodha ya Video:\n"
        "1. 🔥 Video A - 250 points → /get_1\n"
        "2. 🍑 Video B - 250 points → /get_2\n"
        "3. 💦 Video C - 250 points → /get_3"
    )

# /get_1, /get_2, /get_3
async def get_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    command = update.message.text

    async with aiosqlite.connect("database.db") as db:
        cursor = await db.execute("SELECT points FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()

        if row is None:
            await update.message.reply_text("Hujapewa points bado. Tuma /start kwanza.")
            return

        points = row[0]

        if points < 250:
            await update.message.reply_text("😥 Huna points za kutosha. Tuma /ongeza kupata points zaidi.")
            return

        await db.execute("UPDATE users SET points = ? WHERE user_id = ?", (points - 250, user_id))
        await db.commit()

        video_name = {
            "/get_1": "Video A: https://t.me/c/2340537863/5",
            "/get_2": "Video B: https://t.me/c/2340537863/6",
            "/get_3": "Video C: https://t.me/c/2340537863/7",
        }.get(command, "Haipo")

        await update.message.reply_text(
            f"✅ Umepokea {video_name}\n\n📉 Salio: {points - 250} points"
        )

# /ongeza
async def ongeza(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💳 Lipia Tsh 1,000 au zaidi ili kupata points.\n\n(Coming soon 💰)"
    )

# /salio
async def salio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    async with aiosqlite.connect("database.db") as db:
        cursor = await db.execute("SELECT points FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        if row:
            await update.message.reply_text(f"📌 Salio lako ni: {row[0]} points")
        else:
            await update.message.reply_text("Tuma /start kwanza ili upate points.")

# 👉 MAIN FUNCTION
async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("videos", videos))
    app.add_handler(CommandHandler("get_1", get_video))
    app.add_handler(CommandHandler("get_2", get_video))
    app.add_handler(CommandHandler("get_3", get_video))
    app.add_handler(CommandHandler("ongeza", ongeza))
    app.add_handler(CommandHandler("salio", salio))

    await app.run_polling()

# Run it
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
import aiosqlite
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import datetime

TOKEN = "weka_token_yako_hapa"

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name

    async with aiosqlite.connect("database.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                points INTEGER,
                last_daily TEXT
            )
        """)
        await db.commit()

        cursor = await db.execute("SELECT points FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()

        if row is None:
            await db.execute("INSERT INTO users (user_id, points, last_daily) VALUES (?, ?, ?)", (user_id, 1000, ""))
            await db.commit()
            await update.message.reply_text(f"Hii ni demo! Karibu {first_name}.\n🎁 Umepewa 1000 points bure!")
        else:
            await update.message.reply_text(f"Karibu tena {first_name}!\n📌 Points zako: {row[0]}")

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

# /daily
async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    today = datetime.date.today().isoformat()

    async with aiosqlite.connect("database.db") as db:
        cursor = await db.execute("SELECT points, last_daily FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()

        if row:
            points, last_daily = row
            if last_daily == today:
                await update.message.reply_text("🎁 Leo tayari umeshapokea bonus yako ya kila siku!")
            else:
                points += 300
                await db.execute("UPDATE users SET points = ?, last_daily = ? WHERE user_id = ?", (points, today, user_id))
                await db.commit()
                await update.message.reply_text(f"✅ Umepewa daily bonus ya 300 points!\n📌 Salio jipya: {points} points")
        else:
            await update.message.reply_text("Tuma /start kwanza kupata points zako!")

# /videos
async def videos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Orodha ya Video:\n"
        "1. 🔥 Video A - 250 points → /get_1\n"
        "2. 🍑 Video B - 250 points → /get_2\n"
        "3. 💦 Video C - 250 points → /get_3"
    )

# /get commands
async def get_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    command = update.message.text

    async with aiosqlite.connect("database.db") as db:
        cursor = await db.execute("SELECT points FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()

        if not row:
            await update.message.reply_text("Tuma /start kwanza kupata points.")
            return

        points = row[0]
        if points < 250:
            await update.message.reply_text("😢 Huna points za kutosha. Tuma /nunua kuongeza points.")
            return

        await db.execute("UPDATE users SET points = ? WHERE user_id = ?", (points - 250, user_id))
        await db.commit()

    links = {
        "/get_1": "Video A: https://t.me/c/2340537863/5",
        "/get_2": "Video B: https://t.me/c/2340537863/6",
        "/get_3": "Video C: https://t.me/c/2340537863/7"
    }

    await update.message.reply_text(f"✅ {links.get(command)}\n📉 Salio: {points - 250} points")

# /nunua
async def nunua(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💳 Nunua points kwa kulipa TigoPesa/M-Pesa/Airtel Money.\n\n"
        "✅ 1000 Tsh = 1000 points.\n"
        "⚠️ Tuma risiti kwa admin @jinalako baada ya malipo."
    )

# Run App
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("salio", salio))
    app.add_handler(CommandHandler("daily", daily))
    app.add_handler(CommandHandler("videos", videos))
    app.add_handler(CommandHandler("get_1", get_video))
    app.add_handler(CommandHandler("get_2", get_video))
    app.add_handler(CommandHandler("get_3", get_video))
    app.add_handler(CommandHandler("nunua", nunua))

    app.run_polling()
import aiosqlite
import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8192573503:AAGkm4M2XV922PViP8Gc2cVQEWoP0MVwvMI"

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name

    async with aiosqlite.connect("database.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                points INTEGER
            )
        """)
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

# /videos command
async def videos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Orodha ya Video:\n"
        "1. 🔥 Video A - 250 points → /get_1\n"
        "2. 🍑 Video B - 250 points → /get_2\n"
        "3. 💦 Video C - 250 points → /get_3"
    )

# /get_x commands handler
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

# /ongeza command
async def ongeza(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💳 Lipia Tsh 1,000 au zaidi ili kupata points.\n\n(Coming soon 💰)"
    )

# /salio command
async def salio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    async with aiosqlite.connect("database.db") as db:
        cursor = await db.execute("SELECT points FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        if row:
            await update.message.reply_text(f"📌 Salio lako ni: {row[0]} points")
        else:
            await update.message.reply_text("Tuma /start kwanza ili upate points.")

# /daily command - bonus points kila siku
async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    today = datetime.date.today().isoformat()

    async with aiosqlite.connect("database.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS daily_bonus (
                user_id INTEGER PRIMARY KEY,
                last_claim TEXT
            )
        """)
        await db.commit()

        cursor = await db.execute("SELECT last_claim FROM daily_bonus WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()

        if row and row[0] == today:
            await update.message.reply_text("💤 Umeshatoa bonus yako ya leo tayari, jaribu kesho.")
            return

        cursor2 = await db.execute("SELECT points FROM users WHERE user_id = ?", (user_id,))
        user_row = await cursor2.fetchone()
        if user_row is None:
            await update.message.reply_text("Tuma /start kwanza ili upate points.")
            return

        new_points = user_row[0] + 500
        await db.execute("UPDATE users SET points = ? WHERE user_id = ?", (new_points, user_id))
        await db.execute("INSERT OR REPLACE INTO daily_bonus (user_id, last_claim) VALUES (?, ?)", (user_id, today))
        await db.commit()

        await update.message.reply_text(f"🎉 Umeshapata bonus ya 500 points!\n📌 Salio lako sasa ni: {new_points} points")

# /msaada command - help
async def msaada(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🤖 Msaada kwa bot:\n\n"
        "/start - Anza bot na pata points\n"
        "/videos - Orodha ya video za kununua\n"
        "/get_1, /get_2, /get_3 - Nunua video kwa points\n"
        "/ongeza - Maelezo ya jinsi ya kuongeza points\n"
        "/salio - Angalia salio lako la points\n"
        "/daily - Pata bonus ya points kila siku\n"
        "/msaada - Hii meseji ya msaada"
    )
    await update.message.reply_text(msg)

# Create tables on startup
async def create_tables():
    async with aiosqlite.connect("database.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                points INTEGER
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS daily_bonus (
                user_id INTEGER PRIMARY KEY,
                last_claim TEXT
            )
        """)
        await db.commit()

def main():
    import asyncio
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("videos", videos))
    app.add_handler(CommandHandler("get_1", get_video))
    app.add_handler(CommandHandler("get_2", get_video))
    app.add_handler(CommandHandler("get_3", get_video))
    app.add_handler(CommandHandler("ongeza", ongeza))
    app.add_handler(CommandHandler("salio", salio))
    app.add_handler(CommandHandler("daily", daily))
    app.add_handler(CommandHandler("msaada", msaada))

    asyncio.run(create_tables())

    app.run_polling()

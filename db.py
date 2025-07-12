import aiosqlite

async def create_db():
    async with aiosqlite.connect("users.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT,
                points INTEGER DEFAULT 1000
            )
        """)
        await db.commit()

async def get_user(user_id):
    async with aiosqlite.connect("users.db") as db:
        async with db.execute("SELECT points FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def add_user(user_id, first_name):
    async with aiosqlite.connect("users.db") as db:
        await db.execute("INSERT OR IGNORE INTO users (user_id, first_name) VALUES (?, ?)", (user_id, first_name))
        await db.commit()

async def deduct_points(user_id, amount):
    async with aiosqlite.connect("users.db") as db:
        await db.execute("UPDATE users SET points = points - ? WHERE user_id = ?", (amount, user_id))
        await db.commit()

async def add_points(user_id, amount):
    async with aiosqlite.connect("users.db") as db:
        await db.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (amount, user_id))
        await db.commit() 
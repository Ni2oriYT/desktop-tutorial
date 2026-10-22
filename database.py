import aiosqlite
from pathlib import Path

DB_PATH = Path("bot.db")

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            '''CREATE TABLE IF NOT EXISTS warnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                moderator_id INTEGER NOT NULL,
                reason TEXT NOT NULL,
                created_at TEXT NOT NULL
            )'''
        )
        await db.execute(
            '''CREATE TABLE IF NOT EXISTS counters (
                name TEXT PRIMARY KEY,
                value INTEGER NOT NULL
            )'''
        )
        await db.commit()

async def next_number(name: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT value FROM counters WHERE name = ?", (name,))
        row = await cur.fetchone()
        value = (row[0] if row else 0) + 1
        await db.execute(
            "INSERT INTO counters(name, value) VALUES(?, ?) "
            "ON CONFLICT(name) DO UPDATE SET value=excluded.value",
            (name, value),
        )
        await db.commit()
        return value

async def add_warning(guild_id, user_id, moderator_id, reason, created_at):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO warnings(guild_id,user_id,moderator_id,reason,created_at) VALUES(?,?,?,?,?)",
            (guild_id, user_id, moderator_id, reason, created_at),
        )
        await db.commit()

async def get_warnings(guild_id, user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT reason, moderator_id, created_at FROM warnings "
            "WHERE guild_id=? AND user_id=? ORDER BY id DESC",
            (guild_id, user_id),
        )
        return await cur.fetchall()

import aiosqlite
import datetime

DB_PATH = "ferma.db"

CREATE_TABLES = [
    """
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        coins INTEGER DEFAULT 100,
        crystals INTEGER DEFAULT 10,
        energy INTEGER DEFAULT 50,
        max_energy INTEGER DEFAULT 50,
        level INTEGER DEFAULT 1,
        xp INTEGER DEFAULT 0,
        xp_to_level INTEGER DEFAULT 100,
        daily_ts INTEGER DEFAULT 0,
        created_at TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS plots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        plot_index INTEGER,
        crop TEXT,
        planted_at INTEGER,
        grow_time INTEGER,
        watered BOOLEAN DEFAULT 0
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS animals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        animal_type TEXT,
        owned INTEGER,
        last_collect INTEGER
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS buildings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        building_type TEXT,
        built INTEGER DEFAULT 0
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS upgrades (
        user_id INTEGER,
        upgrade_type TEXT,
        level INTEGER DEFAULT 0
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        event_type TEXT,
        ts INTEGER
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS misc (
        user_id INTEGER PRIMARY KEY,
        beehives INTEGER DEFAULT 0,
        honey INTEGER DEFAULT 0,
        fish INTEGER DEFAULT 0,
        tickets INTEGER DEFAULT 0
    );
    """
]

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        for sql in CREATE_TABLES:
            await db.execute(sql)
        await db.commit()

async def create_user(user_id, username):
    now = datetime.datetime.now()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username, created_at) VALUES (?, ?, ?)",
            (user_id, username, now)
        )
        await db.execute(
            "INSERT OR IGNORE INTO misc (user_id) VALUES (?)", (user_id,)
        )
        await db.commit()

async def get_user(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        res = await cur.fetchone()
        return res

async def get_full_state(user_id):
    # Вытаскивает всё для sync — для фронта!
    async with aiosqlite.connect(DB_PATH) as db:
        users = await db.execute_fetchall("SELECT * FROM users WHERE user_id=?", (user_id,))
        plots = await db.execute_fetchall("SELECT * FROM plots WHERE user_id=?", (user_id,))
        animals = await db.execute_fetchall("SELECT * FROM animals WHERE user_id=?", (user_id,))
        buildings = await db.execute_fetchall("SELECT * FROM buildings WHERE user_id=?", (user_id,))
        upgrades = await db.execute_fetchall("SELECT * FROM upgrades WHERE user_id=?", (user_id,))
        misc = await db.execute_fetchall("SELECT * FROM misc WHERE user_id=?", (user_id,))
        return {
            "user": users,
            "plots": plots,
            "animals": animals,
            "buildings": buildings,
            "upgrades": upgrades,
            "misc": misc
        }

async def add_coins(user_id, amount):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET coins = coins + ? WHERE user_id=?", (amount, user_id))
        await db.commit()
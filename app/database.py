from __future__ import annotations
import aiosqlite
import os
from pathlib import Path
from typing import Optional

DB_PATH = Path(os.getenv("DATA_DIR", "data")) / "bot.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


async def init_db() -> None:
    """Initialize database schema"""
    async with aiosqlite.connect(str(DB_PATH)) as db:
        # Users table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                is_premium INTEGER DEFAULT 0,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Downloads tracking
        await db.execute("""
            CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                url TEXT NOT NULL,
                downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # Stats table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY,
                total_downloads INTEGER DEFAULT 0,
                total_users INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.commit()


async def add_user(user_id: int, username: Optional[str] = None) -> None:
    """Add or update user"""
    async with aiosqlite.connect(str(DB_PATH)) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username)
        )
        await db.commit()


async def add_download(user_id: int, url: str) -> None:
    """Log a download"""
    async with aiosqlite.connect(str(DB_PATH)) as db:
        await db.execute(
            "INSERT INTO downloads (user_id, url) VALUES (?, ?)",
            (user_id, url)
        )
        await db.commit()


async def get_total_downloads() -> int:
    """Get total download count"""
    async with aiosqlite.connect(str(DB_PATH)) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM downloads")
        result = await cursor.fetchone()
        return result[0] if result else 0


async def get_total_users() -> int:
    """Get total unique users"""
    async with aiosqlite.connect(str(DB_PATH)) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        result = await cursor.fetchone()
        return result[0] if result else 0


async def get_user_download_count(user_id: int) -> int:
    """Get number of downloads by a user"""
    async with aiosqlite.connect(str(DB_PATH)) as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM downloads WHERE user_id = ?",
            (user_id,)
        )
        result = await cursor.fetchone()
        return result[0] if result else 0


async def set_premium(user_id: int, is_premium: bool) -> None:
    """Set premium status for user"""
    async with aiosqlite.connect(str(DB_PATH)) as db:
        await db.execute(
            "UPDATE users SET is_premium = ? WHERE user_id = ?",
            (1 if is_premium else 0, user_id)
        )
        await db.commit()


async def is_premium(user_id: int) -> bool:
    """Check if user is premium"""
    async with aiosqlite.connect(str(DB_PATH)) as db:
        cursor = await db.execute(
            "SELECT is_premium FROM users WHERE user_id = ?",
            (user_id,)
        )
        result = await cursor.fetchone()
        return bool(result[0]) if result else False


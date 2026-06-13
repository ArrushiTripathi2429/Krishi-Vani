# ============================================================
# backend/db.py
# Goal: SQLite database for persistent chat threads
# ============================================================

import aiosqlite
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "krishivani.db")

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS threads (
                id TEXT PRIMARY KEY,
                title TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id TEXT,
                role TEXT,
                content TEXT,
                is_farming INTEGER DEFAULT 0,
                sources TEXT DEFAULT '[]',
                created_at TEXT,
                FOREIGN KEY (thread_id) REFERENCES threads(id)
            )
        """)
        await db.commit()

async def create_thread(thread_id: str, title: str = "New Chat"):
    async with aiosqlite.connect(DB_PATH) as db:
        now = datetime.now().isoformat()
        await db.execute(
            "INSERT OR IGNORE INTO threads (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (thread_id, title, now, now)
        )
        await db.commit()

async def save_message(thread_id: str, role: str, content: str, is_farming: bool = False, sources: list = []):
    async with aiosqlite.connect(DB_PATH) as db:
        now = datetime.now().isoformat()
        await db.execute(
            "INSERT INTO messages (thread_id, role, content, is_farming, sources, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (thread_id, role, content, int(is_farming), json.dumps(sources), now)
        )
        await db.execute(
            "UPDATE threads SET updated_at = ? WHERE id = ?",
            (now, thread_id)
        )
        await db.commit()

async def get_thread_messages(thread_id: str) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT role, content, is_farming, sources FROM messages WHERE thread_id = ? ORDER BY id ASC",
            (thread_id,)
        )
        rows = await cursor.fetchall()
        return [
            {
                "role": row[0],
                "content": row[1],
                "is_farming": bool(row[2]),
                "sources": json.loads(row[3]),
            }
            for row in rows
        ]

async def get_all_threads() -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id, title, created_at, updated_at FROM threads ORDER BY updated_at DESC"
        )
        rows = await cursor.fetchall()
        return [
            {"id": row[0], "title": row[1], "created_at": row[2], "updated_at": row[3]}
            for row in rows
        ]

async def delete_thread(thread_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM messages WHERE thread_id = ?", (thread_id,))
        await db.execute("DELETE FROM threads WHERE id = ?", (thread_id,))
        await db.commit()

async def update_thread_title(thread_id: str, title: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE threads SET title = ? WHERE id = ?", (title, thread_id))
        await db.commit()
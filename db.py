from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path(os.getenv("DATABASE_PATH", "/tmp/reviews.sqlite3" if os.getenv("VERCEL") else str(Path(__file__).with_name("reviews.sqlite3"))))


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                external_id TEXT NOT NULL UNIQUE,
                source TEXT NOT NULL DEFAULT 'demo',
                author TEXT NOT NULL,
                rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
                text TEXT NOT NULL,
                reviewed_at TEXT NOT NULL,
                suggested_reply TEXT,
                approved_reply TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                published_at TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                review_id INTEGER NOT NULL REFERENCES reviews(id),
                action TEXT NOT NULL,
                detail TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )


def seed_demo() -> None:
    demo = [
        ("demo-1", "Google (demo)", "Ana Paula", 5, "Atendimento excelente e equipe muito atenciosa.", "2026-10-07T10:15:00"),
        ("demo-2", "Google (demo)", "Carlos Mendes", 3, "O serviço foi bom, mas demorou um pouco.", "2026-10-06T16:40:00"),
        ("demo-3", "Google (demo)", "Juliana Costa", 1, "Tive um problema e não consegui retorno.", "2026-10-05T09:20:00"),
    ]
    with connect() as conn:
        conn.executemany(
            "INSERT OR IGNORE INTO reviews (external_id, source, author, rating, text, reviewed_at) VALUES (?, ?, ?, ?, ?, ?)",
            demo,
        )


def list_reviews(status: str | None = None) -> list[sqlite3.Row]:
    with connect() as conn:
        if status and status != "all":
            return conn.execute("SELECT * FROM reviews WHERE status = ? ORDER BY reviewed_at DESC", (status,)).fetchall()
        return conn.execute("SELECT * FROM reviews ORDER BY reviewed_at DESC").fetchall()


def get_review(review_id: int) -> sqlite3.Row | None:
    with connect() as conn:
        return conn.execute("SELECT * FROM reviews WHERE id = ?", (review_id,)).fetchone()


def upsert_reviews(reviews: list[dict[str, Any]]) -> int:
    count = 0
    with connect() as conn:
        for review in reviews:
            conn.execute(
                """INSERT INTO reviews (external_id, source, author, rating, text, reviewed_at)
                   VALUES (?, ?, ?, ?, ?, ?)
                   ON CONFLICT(external_id) DO UPDATE SET author=excluded.author, rating=excluded.rating,
                   text=excluded.text, reviewed_at=excluded.reviewed_at, updated_at=CURRENT_TIMESTAMP""",
                (review["external_id"], review.get("source", "import"), review["author"], int(review["rating"]), review["text"], review["reviewed_at"]),
            )
            count += 1
    return count


def set_reply(review_id: int, reply: str, status: str = "draft") -> None:
    with connect() as conn:
        conn.execute("UPDATE reviews SET suggested_reply = ?, approved_reply = NULL, status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (reply, status, review_id))
        conn.execute("INSERT INTO actions (review_id, action, detail) VALUES (?, 'reply_generated', ?)", (review_id, reply))


def approve(review_id: int, reply: str) -> None:
    with connect() as conn:
        conn.execute("UPDATE reviews SET approved_reply = ?, status = 'approved', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (reply, review_id))
        conn.execute("INSERT INTO actions (review_id, action, detail) VALUES (?, 'approved', ?)", (review_id, reply))


def publish(review_id: int) -> None:
    with connect() as conn:
        row = conn.execute("SELECT approved_reply, status FROM reviews WHERE id = ?", (review_id,)).fetchone()
        if not row or row["status"] != "approved" or not row["approved_reply"]:
            raise ValueError("A avaliação precisa estar aprovada antes da publicação.")
        conn.execute("UPDATE reviews SET status = 'published', published_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (review_id,))
        conn.execute("INSERT INTO actions (review_id, action, detail) VALUES (?, 'published', ?)", (review_id, row["approved_reply"]))

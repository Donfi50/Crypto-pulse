import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def database_path():
    """Return the configured SQLite file path, creating its parent directory."""
    configured = os.getenv("CREATELAB_DB_PATH", "data/createlab.sqlite3")
    path = Path(configured).expanduser()
    if not path.is_absolute():
        path = Path(__file__).resolve().parent / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def connect(path=None):
    connection = sqlite3.connect(str(path or database_path()), timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(path=None):
    with connect(path) as connection:
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS creations (
                id TEXT PRIMARY KEY,
                kind TEXT NOT NULL CHECK (kind IN ('Video', 'Game')),
                prompt TEXT NOT NULL,
                style TEXT NOT NULL,
                detail TEXT NOT NULL,
                result TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_creations_created_at ON creations(created_at DESC)"
        )


def save_creation(creation, path=None):
    """Persist a generated project and return its stored representation."""
    record = dict(creation)
    record.setdefault("created_at", datetime.now(timezone.utc).isoformat(timespec="seconds"))
    required = ("id", "kind", "prompt", "style", "detail", "result", "created_at")
    missing = [key for key in required if not record.get(key)]
    if missing:
        raise ValueError(f"Creation is missing required fields: {', '.join(missing)}")

    initialize_database(path)
    with connect(path) as connection:
        connection.execute(
            """INSERT INTO creations (id, kind, prompt, style, detail, result, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            tuple(record[key] for key in required),
        )
    return record


def list_creations(kind=None, limit=100, path=None):
    initialize_database(path)
    limit = max(1, min(int(limit), 500))
    with connect(path) as connection:
        if kind in ("Video", "Game"):
            rows = connection.execute(
                "SELECT * FROM creations WHERE kind = ? ORDER BY created_at DESC LIMIT ?",
                (kind, limit),
            ).fetchall()
        else:
            rows = connection.execute(
                "SELECT * FROM creations ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
    return [dict(row) for row in rows]


def get_creation(creation_id, path=None):
    initialize_database(path)
    with connect(path) as connection:
        row = connection.execute(
            "SELECT * FROM creations WHERE id = ?", (creation_id,)
        ).fetchone()
    return dict(row) if row else None


def delete_creation(creation_id, path=None):
    initialize_database(path)
    with connect(path) as connection:
        cursor = connection.execute("DELETE FROM creations WHERE id = ?", (creation_id,))
    return cursor.rowcount > 0


def creation_counts(path=None):
    initialize_database(path)
    with connect(path) as connection:
        rows = connection.execute(
            "SELECT kind, COUNT(*) AS total FROM creations GROUP BY kind"
        ).fetchall()
    counts = {"Video": 0, "Game": 0}
    counts.update({row["kind"]: row["total"] for row in rows})
    return counts

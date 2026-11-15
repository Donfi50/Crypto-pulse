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
    """Create tables and add owner_id to older shared-project databases.

    Existing projects are left unowned during migration and are not exposed in
    any signed-in user's dashboard.
    """
    with connect(path) as connection:
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute(
            """CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                display_name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )"""
        )
        connection.execute(
            """CREATE TABLE IF NOT EXISTS creations (
                id TEXT PRIMARY KEY,
                owner_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                kind TEXT NOT NULL CHECK (kind IN ('Video', 'Game')),
                prompt TEXT NOT NULL,
                style TEXT NOT NULL,
                detail TEXT NOT NULL,
                result TEXT NOT NULL,
                created_at TEXT NOT NULL
            )"""
        )
        columns = {row["name"] for row in connection.execute("PRAGMA table_info(creations)")}
        if "owner_id" not in columns:
            # Old shared projects have no trustworthy owner. Keep them private
            # from accounts instead of assigning them to an arbitrary user.
            connection.execute(
                "ALTER TABLE creations ADD COLUMN owner_id TEXT REFERENCES users(id) ON DELETE CASCADE"
            )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_creations_owner_created "
            "ON creations(owner_id, created_at DESC)"
        )
        connection.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")


def create_user(user_id, email, display_name, password_hash, path=None):
    initialize_database(path)
    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        with connect(path) as connection:
            connection.execute(
                "INSERT INTO users (id, email, display_name, password_hash, created_at) VALUES (?, ?, ?, ?, ?)",
                (user_id, email.strip().lower(), display_name.strip(), password_hash, created_at),
            )
    except sqlite3.IntegrityError as error:
        if "email" in str(error).lower():
            raise ValueError("An account with that email already exists.") from error
        raise
    return get_user_by_id(user_id, path)


def get_user_by_email(email, path=None):
    initialize_database(path)
    with connect(path) as connection:
        row = connection.execute(
            "SELECT id, email, display_name, password_hash, created_at FROM users WHERE email = ? COLLATE NOCASE",
            (email.strip().lower(),),
        ).fetchone()
    return dict(row) if row else None


def get_user_by_id(user_id, path=None):
    initialize_database(path)
    with connect(path) as connection:
        row = connection.execute(
            "SELECT id, email, display_name, created_at FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    return dict(row) if row else None


def save_creation(creation, path=None):
    """Persist a creation owned by the authenticated account."""
    record = dict(creation)
    record.setdefault("created_at", datetime.now(timezone.utc).isoformat(timespec="seconds"))
    required = ("id", "owner_id", "kind", "prompt", "style", "detail", "result", "created_at")
    missing = [key for key in required if not record.get(key)]
    if missing:
        raise ValueError(f"Creation is missing required fields: {', '.join(missing)}")
    initialize_database(path)
    with connect(path) as connection:
        connection.execute(
            """INSERT INTO creations (id, owner_id, kind, prompt, style, detail, result, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            tuple(record[key] for key in required),
        )
    return record


def list_creations(owner_id, kind=None, limit=100, path=None):
    initialize_database(path)
    limit = max(1, min(int(limit), 500))
    with connect(path) as connection:
        if kind in ("Video", "Game"):
            rows = connection.execute(
                "SELECT * FROM creations WHERE owner_id = ? AND kind = ? ORDER BY created_at DESC LIMIT ?",
                (owner_id, kind, limit),
            ).fetchall()
        else:
            rows = connection.execute(
                "SELECT * FROM creations WHERE owner_id = ? ORDER BY created_at DESC LIMIT ?",
                (owner_id, limit),
            ).fetchall()
    return [dict(row) for row in rows]


def get_creation(owner_id, creation_id, path=None):
    initialize_database(path)
    with connect(path) as connection:
        row = connection.execute(
            "SELECT * FROM creations WHERE owner_id = ? AND id = ?", (owner_id, creation_id)
        ).fetchone()
    return dict(row) if row else None


def delete_creation(owner_id, creation_id, path=None):
    initialize_database(path)
    with connect(path) as connection:
        cursor = connection.execute(
            "DELETE FROM creations WHERE owner_id = ? AND id = ?", (owner_id, creation_id)
        )
    return cursor.rowcount > 0


def creation_counts(owner_id, path=None):
    initialize_database(path)
    with connect(path) as connection:
        rows = connection.execute(
            "SELECT kind, COUNT(*) AS total FROM creations WHERE owner_id = ? GROUP BY kind",
            (owner_id,),
        ).fetchall()
    counts = {"Video": 0, "Game": 0}
    counts.update({row["kind"]: row["total"] for row in rows})
    return counts

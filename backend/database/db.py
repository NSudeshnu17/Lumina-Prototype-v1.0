import sqlite3
import os
from config import DATABASE_PATH, DATABASE_DIR

def get_db():
    """Get a database connection with row factory and foreign keys enabled."""
    os.makedirs(DATABASE_DIR, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn

def dict_from_row(row):
    """Convert a sqlite3.Row to a dict."""
    if row is None:
        return None
    return dict(row)

def dicts_from_rows(rows):
    """Convert a list of sqlite3.Row to a list of dicts."""
    return [dict(row) for row in rows]

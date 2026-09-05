"""
Database Initialization Script for NotesVault (SQLite)
Ensures tables are created automatically in the SQLite database.
"""

import os
import sqlite3

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.environ.get(
    "SQLITE_DB_PATH",
    os.path.join(
        "/tmp" if os.environ.get("AWS_LAMBDA_FUNCTION_NAME") or os.environ.get("NETLIFY") else BASE_DIR,
        "notes.db"
    )
)


def init_database():
    print(f"Initializing SQLite database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_notes_user_id ON notes(user_id);")
    conn.commit()
    conn.close()
    print("SQLite database initialization completed successfully! All tables ready.")


if __name__ == "__main__":
    init_database()

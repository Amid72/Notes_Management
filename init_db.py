"""
Database Initialization Script for NotesVault
Connects to the configured MySQL database (local or cloud)
and ensures all necessary tables exist.
"""

import os
import sys
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

load_dotenv()

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "root"),
    "database": os.environ.get("DB_NAME", "notes_db"),
    "port": int(os.environ.get("DB_PORT", 3306))
}

TABLES = [
    """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(100) NOT NULL UNIQUE,
        email VARCHAR(100) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS notes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(100) NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        user_id INT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """,
    """
    CREATE INDEX idx_notes_user_id ON notes(user_id);
    """
]


def init_database():
    print(f"Connecting to MySQL database '{DB_CONFIG['database']}' at {DB_CONFIG['host']}:{DB_CONFIG['port']}...")
    try:
        config = DB_CONFIG.copy()
        ssl_ca = os.environ.get("DB_SSL_CA")
        if ssl_ca:
            config["ssl_ca"] = ssl_ca

        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        print("Creating tables if they do not exist...")
        for query in TABLES:
            try:
                cursor.execute(query)
            except mysql.connector.Error as err:
                # If index already exists, ignore
                if "Duplicate key name" in str(err) or "already exists" in str(err):
                    continue
                else:
                    print(f"Notice: {err}")

        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialization completed successfully! All tables are ready.")
    except Error as e:
        print(f"Database connection error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    init_database()

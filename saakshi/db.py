import sqlite3
import os

DB_PATH = "out/saakshi.db"

def get_db():
    os.makedirs("out", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS custody_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            stage TEXT,
            description TEXT,
            data_hash TEXT,
            prev_hash TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS segments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel INTEGER,
            offset INTEGER,
            length INTEGER,
            timestamp TEXT,
            is_recovered BOOLEAN,
            confidence REAL,
            file_path TEXT,
            file_hash TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS motion_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            segment_id INTEGER,
            channel INTEGER,
            timestamp TEXT,
            frame_index INTEGER
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()

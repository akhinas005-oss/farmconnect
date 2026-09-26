import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "farmconnect.db")

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Equipment Table (Vendor & Equipment details)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS equipment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        purpose TEXT,
        condition TEXT,
        rent_per_day REAL NOT NULL,
        location TEXT NOT NULL,
        contact TEXT NOT NULL,
        vendor_name TEXT,
        image_url TEXT,
        available BOOLEAN NOT NULL DEFAULT 1
    );
    """)

    # Workers Table (Worker & Skilled Labor details)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS workers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        skill TEXT NOT NULL,
        experience TEXT,
        daily_wage REAL NOT NULL,
        location TEXT NOT NULL,
        contact TEXT NOT NULL,
        image_url TEXT,
        available_from TEXT,
        available_to TEXT
    );
    """)

    conn.commit()
    conn.close()

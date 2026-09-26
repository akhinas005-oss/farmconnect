import sqlite3
import os
import logging
from contextlib import contextmanager
from config import settings

logger = logging.getLogger("farmconnect.database")

@contextmanager
def get_db_connection(db_path: str = None):
    """Context manager for SQLite connections ensuring clean commit/rollback and closure."""
    target_db = db_path or settings.DB_PATH
    conn = sqlite3.connect(target_db)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error occurred: {e}")
        raise e
    finally:
        conn.close()


def init_db(db_path: str = None):
    """Initializes database schema, indexes, and applies lightweight version migrations."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # 1. Versioned migrations tracking table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 2. Equipment Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            purpose TEXT,
            condition TEXT,
            rent_per_day REAL NOT NULL CHECK(rent_per_day >= 0),
            location TEXT NOT NULL,
            contact TEXT NOT NULL,
            vendor_name TEXT,
            image_url TEXT,
            available BOOLEAN NOT NULL DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 3. Workers Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS workers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            skill TEXT NOT NULL,
            experience TEXT,
            daily_wage REAL NOT NULL CHECK(daily_wage >= 0),
            location TEXT NOT NULL,
            contact TEXT NOT NULL,
            image_url TEXT,
            available_from TEXT,
            available_to TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 4. Frequently queried Indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_equipment_location ON equipment(location);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_equipment_type ON equipment(type);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_workers_location ON workers(location);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_workers_skill ON workers(skill);")

        # Record migration version
        cursor.execute("INSERT OR IGNORE INTO schema_migrations (version) VALUES (1);")
        logger.info("Database initialized successfully with migration version 1.")

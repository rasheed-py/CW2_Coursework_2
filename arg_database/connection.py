import sqlite3
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent.parent / "DATA" / "platform.db"


def get_db_connection():
    """Create and return a database connection"""
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def setup_database():
    """Initialize the database and create all tables"""
    from arg_database.tables import initialize_all_tables

    conn = get_db_connection()
    initialize_all_tables(conn)
    conn.close()
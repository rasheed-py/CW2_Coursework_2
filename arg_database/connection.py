import sqlite3
from pathlib import Path

# Define the path to the SQLite database file
DB_PATH = Path(__file__).parent.parent / "DATA" / "platform.db"


def get_db_connection():
    """
    Create and return a database connection

    Returns:
        sqlite3.Connection: A connection object to the SQLite database
    """
    # Ensure the DATA directory exists
    DB_PATH.parent.mkdir(exist_ok=True)

    # Create database connection with row factory for dict-like access
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row

    return conn


def setup_database():
    """
    Initialize the database and create all tables
    This function is called on application startup
    """
    from arg_database.tables import initialize_all_tables

    # Open connection, initialize tables, then close
    conn = get_db_connection()
    initialize_all_tables(conn)
    conn.close()
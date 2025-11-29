def create_users_table(conn):
    """Create users table for authentication"""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)
    conn.commit()


def create_cyber_incidents_table(conn):
    """Create cyber incidents table"""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cyber_incidents (
            incident_id INTEGER PRIMARY KEY,
            timestamp TEXT NOT NULL,
            severity TEXT NOT NULL,
            category TEXT NOT NULL,
            status TEXT NOT NULL,
            description TEXT
        )
    """)
    conn.commit()


def create_datasets_table(conn):
    """Create datasets metadata table"""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS datasets_metadata (
            dataset_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            rows INTEGER NOT NULL,
            columns INTEGER NOT NULL,
            uploaded_by TEXT NOT NULL,
            upload_date TEXT NOT NULL
        )
    """)
    conn.commit()


def create_tickets_table(conn):
    """Create IT tickets table"""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS it_tickets (
            ticket_id INTEGER PRIMARY KEY,
            priority TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL,
            assigned_to TEXT NOT NULL,
            created_at TEXT NOT NULL,
            resolution_time_hours REAL
        )
    """)
    conn.commit()


def initialize_all_tables(conn):
    """Initialize all database tables"""
    create_users_table(conn)
    create_cyber_incidents_table(conn)
    create_datasets_table(conn)
    create_tickets_table(conn)
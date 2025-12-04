import pandas as pd
from pathlib import Path
from arg_database.connection import get_db_connection

# CSV paths
DATA_DIR = Path(__file__).parent.parent / "DATA"
CYBER_CSV = DATA_DIR / "cyber_incidents.csv"
DATASETS_CSV = DATA_DIR / "datasets_metadata.csv"
TICKETS_CSV = DATA_DIR / "it_tickets.csv"


def load_cyber_incidents():
    """Load cyber incidents from database or CSV"""
    conn = get_db_connection()
    try:
        df = pd.read_sql_query("SELECT * FROM cyber_incidents", conn)
        if df.empty:
            # Load from CSV if DB is empty
            df = pd.read_csv(CYBER_CSV)
            df.to_sql('cyber_incidents', conn, if_exists='replace', index=False)
    except:
        df = pd.read_csv(CYBER_CSV)
        df.to_sql('cyber_incidents', conn, if_exists='replace', index=False)
    conn.close()
    return df


def load_datasets_metadata():
    """Load datasets metadata from database or CSV"""
    conn = get_db_connection()
    try:
        df = pd.read_sql_query("SELECT * FROM datasets_metadata", conn)
        if df.empty:
            df = pd.read_csv(DATASETS_CSV)
            df.to_sql('datasets_metadata', conn, if_exists='replace', index=False)
    except:
        df = pd.read_csv(DATASETS_CSV)
        df.to_sql('datasets_metadata', conn, if_exists='replace', index=False)
    conn.close()
    return df


def load_it_tickets():
    """Load IT tickets from database or CSV"""
    conn = get_db_connection()
    try:
        df = pd.read_sql_query("SELECT * FROM it_tickets", conn)
        if df.empty:
            df = pd.read_csv(TICKETS_CSV)
            df.to_sql('it_tickets', conn, if_exists='replace', index=False)
    except:
        df = pd.read_csv(TICKETS_CSV)
        df.to_sql('it_tickets', conn, if_exists='replace', index=False)
    conn.close()
    return df


# CRUD Operations for Cyber Incidents
def create_incident(incident_id, timestamp, severity, category, status, description):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO cyber_incidents VALUES (?, ?, ?, ?, ?, ?)",
        (incident_id, timestamp, severity, category, status, description)
    )
    conn.commit()
    conn.close()


def update_incident(incident_id, **kwargs):
    conn = get_db_connection()
    cursor = conn.cursor()
    set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
    values = list(kwargs.values()) + [incident_id]
    cursor.execute(f"UPDATE cyber_incidents SET {set_clause} WHERE incident_id = ?", values)
    conn.commit()
    conn.close()


def delete_incident(incident_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cyber_incidents WHERE incident_id = ?", (incident_id,))
    conn.commit()
    conn.close()


# CRUD Operations for Datasets
def create_dataset(dataset_id, name, rows, columns, uploaded_by, upload_date):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO datasets_metadata VALUES (?, ?, ?, ?, ?, ?)",
        (dataset_id, name, rows, columns, uploaded_by, upload_date)
    )
    conn.commit()
    conn.close()


def update_dataset(dataset_id, **kwargs):
    conn = get_db_connection()
    cursor = conn.cursor()
    set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
    values = list(kwargs.values()) + [dataset_id]
    cursor.execute(f"UPDATE datasets_metadata SET {set_clause} WHERE dataset_id = ?", values)
    conn.commit()
    conn.close()


def delete_dataset(dataset_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM datasets_metadata WHERE dataset_id = ?", (dataset_id,))
    conn.commit()
    conn.close()


# CRUD Operations for IT Tickets
def create_ticket(ticket_id, priority, description, status, assigned_to, created_at, resolution_time):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO it_tickets VALUES (?, ?, ?, ?, ?, ?, ?)",
        (ticket_id, priority, description, status, assigned_to, created_at, resolution_time)
    )
    conn.commit()
    conn.close()


def update_ticket(ticket_id, **kwargs):
    conn = get_db_connection()
    cursor = conn.cursor()
    set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
    values = list(kwargs.values()) + [ticket_id]
    cursor.execute(f"UPDATE it_tickets SET {set_clause} WHERE ticket_id = ?", values)
    conn.commit()
    conn.close()


def delete_ticket(ticket_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM it_tickets WHERE ticket_id = ?", (ticket_id,))
    conn.commit()
    conn.close()
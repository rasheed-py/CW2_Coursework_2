import pandas as pd
from pathlib import Path
from arg_database.connection import get_db_connection

# Define paths to CSV data files
DATA_DIR = Path(__file__).parent.parent / "DATA"
CYBER_CSV = DATA_DIR / "cyber_incidents.csv"
DATASETS_CSV = DATA_DIR / "datasets_metadata.csv"
TICKETS_CSV = DATA_DIR / "it_tickets.csv"


def load_cyber_incidents():
    """
    Load cyber incidents from database or CSV

    Returns:
        pd.DataFrame: DataFrame containing cyber incident data
    """
    conn = get_db_connection()
    try:
        # Try to load from database
        df = pd.read_sql_query("SELECT * FROM cyber_incidents", conn)
        if df.empty:
            # If database is empty, load from CSV and populate database
            df = pd.read_csv(CYBER_CSV)
            df.to_sql('cyber_incidents', conn, if_exists='replace', index=False)
    except:
        # If table doesn't exist, load from CSV and create table
        df = pd.read_csv(CYBER_CSV)
        df.to_sql('cyber_incidents', conn, if_exists='replace', index=False)
    conn.close()
    return df


def load_datasets_metadata():
    """
    Load datasets metadata from database or CSV

    Returns:
        pd.DataFrame: DataFrame containing dataset metadata
    """
    conn = get_db_connection()
    try:
        # Try to load from database
        df = pd.read_sql_query("SELECT * FROM datasets_metadata", conn)
        if df.empty:
            # If database is empty, load from CSV and populate database
            df = pd.read_csv(DATASETS_CSV)
            df.to_sql('datasets_metadata', conn, if_exists='replace', index=False)
    except:
        # If table doesn't exist, load from CSV and create table
        df = pd.read_csv(DATASETS_CSV)
        df.to_sql('datasets_metadata', conn, if_exists='replace', index=False)
    conn.close()
    return df


def load_it_tickets():
    """
    Load IT tickets from database or CSV

    Returns:
        pd.DataFrame: DataFrame containing IT ticket data
    """
    conn = get_db_connection()
    try:
        # Try to load from database
        df = pd.read_sql_query("SELECT * FROM it_tickets", conn)
        if df.empty:
            # If database is empty, load from CSV and populate database
            df = pd.read_csv(TICKETS_CSV)
            df.to_sql('it_tickets', conn, if_exists='replace', index=False)
    except:
        # If table doesn't exist, load from CSV and create table
        df = pd.read_csv(TICKETS_CSV)
        df.to_sql('it_tickets', conn, if_exists='replace', index=False)
    conn.close()
    return df


# CRUD Operations for Cyber Incidents

def create_incident(incident_id, timestamp, severity, category, status, description):
    """
    Create a new cyber incident record

    Args:
        incident_id: Unique identifier for the incident
        timestamp: Date and time of the incident
        severity: Severity level (Low, Medium, High, Critical)
        category: Type of incident (Phishing, Malware, etc.)
        status: Current status (Open, In Progress, Resolved, Closed)
        description: Description of the incident
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO cyber_incidents VALUES (?, ?, ?, ?, ?, ?)",
        (incident_id, timestamp, severity, category, status, description)
    )
    conn.commit()
    conn.close()


def update_incident(incident_id, **kwargs):
    """
    Update an existing cyber incident record

    Args:
        incident_id: ID of the incident to update
        **kwargs: Fields to update (e.g., status="Resolved", severity="High")
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    # Build SET clause dynamically from kwargs
    set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
    values = list(kwargs.values()) + [incident_id]
    cursor.execute(f"UPDATE cyber_incidents SET {set_clause} WHERE incident_id = ?", values)
    conn.commit()
    conn.close()


def delete_incident(incident_id):
    """
    Delete a cyber incident record

    Args:
        incident_id: ID of the incident to delete
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cyber_incidents WHERE incident_id = ?", (incident_id,))
    conn.commit()
    conn.close()


# CRUD Operations for Datasets

def create_dataset(dataset_id, name, rows, columns, uploaded_by, upload_date):
    """
    Create a new dataset metadata record

    Args:
        dataset_id: Unique identifier for the dataset
        name: Name of the dataset
        rows: Number of rows in the dataset
        columns: Number of columns in the dataset
        uploaded_by: User who uploaded the dataset
        upload_date: Date the dataset was uploaded
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO datasets_metadata VALUES (?, ?, ?, ?, ?, ?)",
        (dataset_id, name, rows, columns, uploaded_by, upload_date)
    )
    conn.commit()
    conn.close()


def update_dataset(dataset_id, **kwargs):
    """
    Update an existing dataset metadata record

    Args:
        dataset_id: ID of the dataset to update
        **kwargs: Fields to update (e.g., name="New Name", rows=5000)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    # Build SET clause dynamically from kwargs
    set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
    values = list(kwargs.values()) + [dataset_id]
    cursor.execute(f"UPDATE datasets_metadata SET {set_clause} WHERE dataset_id = ?", values)
    conn.commit()
    conn.close()


def delete_dataset(dataset_id):
    """
    Delete a dataset metadata record

    Args:
        dataset_id: ID of the dataset to delete
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM datasets_metadata WHERE dataset_id = ?", (dataset_id,))
    conn.commit()
    conn.close()


# CRUD Operations for IT Tickets

def create_ticket(ticket_id, priority, description, status, assigned_to, created_at, resolution_time):
    """
    Create a new IT ticket record

    Args:
        ticket_id: Unique identifier for the ticket
        priority: Priority level (Low, Medium, High, Critical)
        description: Description of the issue
        status: Current status (Open, In Progress, Resolved, etc.)
        assigned_to: Staff member assigned to the ticket
        created_at: Date and time the ticket was created
        resolution_time: Time taken to resolve (in hours)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO it_tickets VALUES (?, ?, ?, ?, ?, ?, ?)",
        (ticket_id, priority, description, status, assigned_to, created_at, resolution_time)
    )
    conn.commit()
    conn.close()


def update_ticket(ticket_id, **kwargs):
    """
    Update an existing IT ticket record

    Args:
        ticket_id: ID of the ticket to update
        **kwargs: Fields to update (e.g., status="Resolved", priority="High")
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    # Build SET clause dynamically from kwargs
    set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
    values = list(kwargs.values()) + [ticket_id]
    cursor.execute(f"UPDATE it_tickets SET {set_clause} WHERE ticket_id = ?", values)
    conn.commit()
    conn.close()


def delete_ticket(ticket_id):
    """
    Delete an IT ticket record

    Args:
        ticket_id: ID of the ticket to delete
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM it_tickets WHERE ticket_id = ?", (ticket_id,))
    conn.commit()
    conn.close()
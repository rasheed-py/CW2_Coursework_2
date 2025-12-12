from arg_database.connection import get_db_connection


def add_user(username, password_hash, role):
    """
    Add a new user to the database

    Args:
        username: The user's username
        password_hash: Hashed password (not plain text)
        role: User's role in the system

    Returns:
        int: The newly created user's ID
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert new user record
    cursor.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, password_hash, role)
    )
    conn.commit()

    # Get the ID of the newly created user
    user_id = cursor.lastrowid
    conn.close()

    return user_id


def get_user(username):
    """
    Get user by username

    Args:
        username: The username to search for

    Returns:
        sqlite3.Row: User record if found, None otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query for user by username
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    conn.close()
    return user


def check_user_exists(username):
    """
    Check if username already exists in database

    Args:
        username: The username to check

    Returns:
        bool: True if username exists, False otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if any user exists with this username
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    exists = cursor.fetchone() is not None

    conn.close()
    return exists
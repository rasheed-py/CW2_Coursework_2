import bcrypt
from arg_database.user_ops import add_user, get_user, check_user_exists


def hash_password(password):
    """
    Hash a password using bcrypt

    Args:
        password: Plain text password to hash

    Returns:
        str: Hashed password as a string
    """
    # Convert password to bytes
    password_bytes = password.encode('utf-8')

    # Generate salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)

    # Return as string for database storage
    return hashed.decode('utf-8')


def verify_password(password, hashed_password):
    """
    Verify a password against its hash

    Args:
        password: Plain text password to verify
        hashed_password: Stored hashed password

    Returns:
        bool: True if password matches, False otherwise
    """
    return bcrypt.checkpw(
        password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def validate_username(username):
    """
    Validate username format

    Rules:
        - Cannot be empty
        - Must be alphanumeric only
        - Must be 3-20 characters long

    Args:
        username: Username to validate

    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    if not username:
        return False, "Username cannot be empty"
    if not username.isalnum():
        return False, "Username must be alphanumeric only"
    if len(username) < 3 or len(username) > 20:
        return False, "Username must be 3-20 characters"
    return True, ""


def validate_password(password):
    """
    Validate password strength

    Rules:
        - At least 6 characters
        - Must contain uppercase letter
        - Must contain lowercase letter
        - Must contain a number

    Args:
        password: Password to validate

    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    if not any(c.isupper() for c in password):
        return False, "Password must contain an uppercase letter"
    if not any(c.islower() for c in password):
        return False, "Password must contain a lowercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain a number"
    return True, ""


def register_user(username, password, role):
    """
    Register a new user

    Args:
        username: Desired username
        password: Plain text password
        role: User's role in the system

    Returns:
        tuple: (bool, result) - (success, user_id or error_message)
    """
    # Check if username already exists
    if check_user_exists(username):
        return False, "Username already exists"

    # Hash the password and add user to database
    hashed = hash_password(password)
    user_id = add_user(username, hashed, role)

    return True, user_id


def login_user(username, password):
    """
    Authenticate user login

    Args:
        username: Username to authenticate
        password: Plain text password to verify

    Returns:
        tuple: (bool, result) - (success, user_data or error_message)
    """
    # Get user from database
    user = get_user(username)
    if not user:
        return False, "Username not found"

    # Verify password against stored hash
    if verify_password(password, user['password_hash']):
        return True, user

    return False, "Invalid password"
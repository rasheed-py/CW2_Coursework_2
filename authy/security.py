import bcrypt
from arg_database.user_ops import add_user, get_user, check_user_exists


def hash_password(password):
    """Hash a password using bcrypt"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(password, hashed_password):
    """Verify a password against its hash"""
    return bcrypt.checkpw(
        password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def validate_username(username):
    """Validate username format"""
    if not username:
        return False, "Username cannot be empty"
    if not username.isalnum():
        return False, "Username must be alphanumeric only"
    if len(username) < 3 or len(username) > 20:
        return False, "Username must be 3-20 characters"
    return True, ""


def validate_password(password):
    """Validate password strength"""
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
    """Register a new user"""
    if check_user_exists(username):
        return False, "Username already exists"

    hashed = hash_password(password)
    user_id = add_user(username, hashed, role)
    return True, user_id


def login_user(username, password):
    """Authenticate user login"""
    user = get_user(username)
    if not user:
        return False, "Username not found"

    if verify_password(password, user['password_hash']):
        return True, user
    return False, "Invalid password"
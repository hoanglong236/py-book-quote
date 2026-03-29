import sqlite3
from database import get_connection
from werkzeug.security import generate_password_hash, check_password_hash


def register_user(username, password):
    """Register a new user with a hashed password.

    Args:
        username: The username for the new account.
        password: The plain text password to hash and store.

    Returns:
        True if registration was successful, False if username already exists.
    """
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO users (username, password)
    VALUES (:username, :password)
    """

    hashed_password = generate_password_hash(password)

    try:
        cursor.execute(sql, {"username": username, "password": hashed_password})

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


def authenticate(username, password):
    """Authenticate a user by checking username and password.

    Args:
        username: The username to authenticate.
        password: The plain text password to verify.

    Returns:
        A user dictionary with id and username if authentication succeeds,
        otherwise None.
    """
    conn = get_connection()
    cursor = conn.cursor()

    sql = "SELECT id, username, password FROM users WHERE username = :username"
    cursor.execute(sql, {"username": username})

    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user["password"], password):
        return user
    return None

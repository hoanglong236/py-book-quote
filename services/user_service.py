from database import get_connection
from werkzeug.security import generate_password_hash


def register_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO users (username, password)
    VALUES (:username, :password)
    """

    hashed_password = generate_password_hash(password)
    cursor.execute(sql, {"username": username, "password": hashed_password})

    conn.commit()
    conn.close()

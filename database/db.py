import sqlite3

DATABASE = "pybook.db"


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # return rows as dictionary-like objects
    return conn

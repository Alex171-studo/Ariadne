import sqlite3

DATABASE = "company.db"

def connect():
    return sqlite3.connect(DATABASE)

def get_users():
    conn = connect()

    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, username, email FROM users"
    )

    return cursor.fetchall()
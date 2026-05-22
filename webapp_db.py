import sqlite3
from pathlib import Path

DATABASE_PATH = Path("./webapp.sqlite")


def create_webapp_response_table(connection):
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS webapp_response (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image BLOB NOT NULL,
            filename TEXT,
            content_type TEXT,
            cat_probability REAL NOT NULL,
            prediction TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    connection.commit()


def ensure_webapp_response_table_exists(db_path=DATABASE_PATH):
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as connection:
        create_webapp_response_table(connection)

def save_webapp_response(image_bytes, filename, content_type, cat_probability, prediction, db_path=DATABASE_PATH):
    ensure_webapp_response_table_exists(db_path)

    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            INSERT INTO webapp_response (image, filename, content_type, cat_probability, prediction, created_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
            """,
            (image_bytes, filename, content_type, cat_probability, prediction)
        )
        connection.commit()

ensure_webapp_response_table_exists()
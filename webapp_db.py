import sqlite3
from pathlib import Path


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
            created_at TEXT NOT NULL,
            user_feedback_correct INTEGER,
            user_label TEXT,
            feedback_submitted_at TEXT
        )
        """
    )
    connection.commit()


def ensure_webapp_response_table_exists(db_path):
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as connection:
        create_webapp_response_table(connection)


def save_webapp_response(image_bytes, filename, content_type, cat_probability, prediction, db_path):
    ensure_webapp_response_table_exists(db_path)

    with sqlite3.connect(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO webapp_response (image, filename, content_type, cat_probability, prediction, created_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
            """,
            (image_bytes, filename, content_type, cat_probability, prediction)
        )
        connection.commit()
        return cursor.lastrowid


def save_user_feedback(response_id, user_feedback_correct, user_label, db_path):
    ensure_webapp_response_table_exists(db_path)

    with sqlite3.connect(db_path) as connection:
        cursor = connection.execute(
            """
            UPDATE webapp_response
            SET user_feedback_correct = ?,
                user_label = ?,
                feedback_submitted_at = datetime('now')
            WHERE id = ?
            """,
            (user_feedback_correct, user_label, response_id)
        )
        connection.commit()
        return cursor.rowcount

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "instance" / "finance.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            date        TEXT    NOT NULL,
            description TEXT    NOT NULL,
            amount      REAL    NOT NULL,
            category    TEXT    NOT NULL DEFAULT 'Others'
        )
        """
    )
    conn.commit()
    conn.close()


def insert_transaction(date: str, description: str, amount: float, category: str) -> int:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO transactions (date, description, amount, category) VALUES (?, ?, ?, ?)",
        (date, description, float(amount), category),
    )
    conn.commit()
    row_id = cur.lastrowid
    conn.close()
    return row_id


def fetch_all_transactions() -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, date, description, amount, category FROM transactions ORDER BY date DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_all_transactions():
    conn = get_connection()
    conn.execute("DELETE FROM transactions")
    conn.commit()
    conn.close()

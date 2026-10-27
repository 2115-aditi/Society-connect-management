"""SQLite database layer for SocietyConnect.

Keeps the existing societyconnect.db and safely adds columns needed by the
connected app. Run from the same folder as app.py.
"""
import sqlite3
from datetime import datetime
from pathlib import Path


DB_PATH = Path(__file__).resolve().with_name("societyconnect.db")
STATUSES = ("Submitted", "In Progress", "Resolved")


def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# def add_complaint(name, flat_number, category, location,
#                   description, priority, user_id):
#     conn = get_connection()
#     try:
#         cursor = conn.cursor()
#         cursor.execute(
#             """
#             INSERT INTO complaints
    #         (resident_user_id, resident_name, flat_number,
    #          category, location, description, priority)
    #         VALUES (%s, %s, %s, %s, %s, %s, %s)
    #         """,
    #         (user_id, name, flat_number, category,
    #          location, description, priority)
    #     )
    #     conn.commit()
    #     return cursor.lastrowid
    # finally:
    #     conn.close()





def create_database():
    """Create tables and migrate older SocietyConnect database versions."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL COLLATE NOCASE UNIQUE,
                flat_number TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'resident'
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS complaints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resident_name TEXT NOT NULL,
                category TEXT NOT NULL,
                location TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Submitted',
                created_at TEXT NOT NULL
            )
        """)
        existing = {r["name"] for r in conn.execute("PRAGMA table_info(complaints)")}
        migrations = {
            "user_id": "INTEGER REFERENCES users(id)",
            "flat_number": "TEXT NOT NULL DEFAULT ''",
            "priority": "TEXT NOT NULL DEFAULT 'Normal'",
            "updated_at": "TEXT",
        }
        for col, definition in migrations.items():
            if col not in existing:
                conn.execute(f"ALTER TABLE complaints ADD COLUMN {col} {definition}")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_complaints_user_id ON complaints(user_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_complaints_status ON complaints(status)")


def add_complaint(resident_name, flat_number, category, location, description,
                  priority="Normal", user_id=None):
    create_database()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cur = conn.execute("""
            INSERT INTO complaints
                (resident_name, flat_number, category, location, description,
                 priority, status, created_at, updated_at, user_id)
            VALUES (?, ?, ?, ?, ?, ?, 'Submitted', ?, ?, ?)
        """, (resident_name.strip(), flat_number.strip(), category, location.strip(),
              description.strip(), priority, now, now, user_id))
        return cur.lastrowid


def _complaint_dict(row):
    if row is None:
        return None
    item = dict(row)
    item["tracking_id"] = f"SC{item['id']:05d}"
    return item


def _parse_id(complaint_id):
    value = str(complaint_id).strip().upper()
    if value.startswith("SC"):
        value = value[2:]
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def get_complaint(complaint_id, user_id=None, is_admin=False):
    cid = _parse_id(complaint_id)
    if cid is None:
        return None
    with get_connection() as conn:
        if is_admin:
            row = conn.execute("SELECT * FROM complaints WHERE id=?", (cid,)).fetchone()
        else:
            row = conn.execute(
                "SELECT * FROM complaints WHERE id=? AND user_id=?", (cid, user_id)
            ).fetchone()
    return _complaint_dict(row)


def get_all_complaints(user_id=None, is_admin=False):
    with get_connection() as conn:
        if is_admin:
            rows = conn.execute("SELECT * FROM complaints ORDER BY id DESC").fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM complaints WHERE user_id=? ORDER BY id DESC", (user_id,)
            ).fetchall()
    return [_complaint_dict(row) for row in rows]


def update_status(complaint_id, new_status):
    cid = _parse_id(complaint_id)
    if cid is None or new_status not in STATUSES:
        return False
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cur = conn.execute(
            "UPDATE complaints SET status=?, updated_at=? WHERE id=?",
            (new_status, now, cid)
        )
        return cur.rowcount > 0


def get_complaint_stats():
    with get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) FROM complaints").fetchone()[0]
        submitted = conn.execute(
            "SELECT COUNT(*) FROM complaints WHERE status='Submitted'"
        ).fetchone()[0]
        in_progress = conn.execute(
            "SELECT COUNT(*) FROM complaints WHERE status='In Progress'"
        ).fetchone()[0]
        resolved = conn.execute(
            "SELECT COUNT(*) FROM complaints WHERE status='Resolved'"
        ).fetchone()[0]
        by_category = conn.execute("""
            SELECT category, COUNT(*) AS count FROM complaints
            GROUP BY category ORDER BY count DESC, category
        """).fetchall()
    return {
        "total": total, "submitted": submitted,
        "in_progress": in_progress, "resolved": resolved,
        "by_category": [dict(r) for r in by_category],
    }


if __name__ == "__main__":
    create_database()
    print(f"SocietyConnect database is ready: {DB_PATH}")

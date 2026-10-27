import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("societyconnect.db")

email = input("Enter the registered email to promote to admin: ")
confirmation = input(
    "Type PROMOTE to grant admin access: "
)

if confirmation != "PROMOTE":
    print("Cancelled.")
    raise SystemExit

with sqlite3.connect(DB_PATH) as conn:

    cursor = conn.execute(
        """
        UPDATE users
        SET role = 'admin'
        WHERE email = ? COLLATE NOCASE
        """,
        (email.strip(),)
    )

    if cursor.rowcount == 1:
        print("Admin role assigned successfully.")
    else:
        print("No account found with that email.")
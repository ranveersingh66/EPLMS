"""
seed.py
-------
Inserts 10 dummy employees into the database for development/testing.
Run once after initialising the database:
    python seed.py
"""

from database import get_connection, init_db

EMPLOYEES = [
    ("Aarav Sharma",    "Engineering",      75000.00, "2023-01-15"),
    ("Priya Patel",     "Human Resources",  55000.00, "2022-06-01"),
    ("Rahul Verma",     "Finance",          68000.00, "2021-03-22"),
    ("Sneha Iyer",      "Engineering",      82000.00, "2023-07-10"),
    ("Vikram Nair",     "Marketing",        60000.00, "2022-11-05"),
    ("Anjali Mehta",    "Operations",       52000.00, "2020-09-14"),
    ("Rohan Gupta",     "Engineering",      79000.00, "2024-02-28"),
    ("Deepika Reddy",   "Finance",          63000.00, "2021-12-01"),
    ("Karan Malhotra",  "Marketing",        57000.00, "2023-04-18"),
    ("Meera Joshi",     "Human Resources",  50000.00, "2022-08-30"),
]

def seed():
    init_db()          # ensure tables exist
    conn = get_connection()

    existing = conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
    if existing >= 10:
        print(f"Database already has {existing} employee(s). Skipping seed.")
        conn.close()
        return

    conn.executemany(
        "INSERT INTO employees (name, department, base_salary, joined_date) "
        "VALUES (?, ?, ?, ?)",
        EMPLOYEES,
    )
    conn.commit()
    print(f"Inserted {len(EMPLOYEES)} dummy employees.")
    conn.close()


if __name__ == "__main__":
    seed()


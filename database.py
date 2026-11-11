"""
database.py
-----------
Handles creation of the SQLite database and its tables for the
Employee Payroll and Leave Management System.

Run this file directly to (re)create payroll.db:
    python database.py
"""

import sqlite3

DB_NAME = "payroll.db"


def get_connection():
    """Return a new SQLite connection with foreign keys enabled."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn


def init_db():
    """Create all tables if they do not already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # ---------- employees ----------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            base_salary REAL NOT NULL,
            joined_date TEXT NOT NULL
        )
    """)

    # ---------- leave_requests ----------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leave_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id INTEGER NOT NULL,
            leave_type TEXT NOT NULL,       -- Sick, Casual, Unpaid
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            days INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',  -- Pending, Approved, Rejected
            FOREIGN KEY (emp_id) REFERENCES employees (id)
        )
    """)

    # ---------- payrolls ----------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payrolls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id INTEGER NOT NULL,
            month_year TEXT NOT NULL,       -- e.g. "2026-11"
            basic_pay REAL NOT NULL,
            unpaid_days INTEGER NOT NULL,
            leave_deduction REAL NOT NULL,
            net_salary REAL NOT NULL,
            FOREIGN KEY (emp_id) REFERENCES employees (id)
        )
    """)

    conn.commit()
    conn.close()
    print(f"Database '{DB_NAME}' initialized successfully.")


if __name__ == "__main__":
    init_db()

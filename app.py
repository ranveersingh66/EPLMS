"""
app.py
------
Flask application for the Employee Payroll and Leave Management System.

Routes:
    GET  /                        -> dashboard
    POST /add-employee            -> register a new employee
    POST /edit-employee/<id>      -> update an existing employee's details
    POST /request-leave           -> log a leave request
    POST /process-leave/<id>      -> approve/reject a pending leave request
    POST /generate-payroll        -> calculate & store monthly payroll for an employee

Run with:
    python app.py
"""

from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, flash

from database import get_connection, init_db

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-in-production"  # needed for flash messages


# ----------------------------------------------------------------------
# Template filters
# ----------------------------------------------------------------------

@app.template_filter("emp_id")
def emp_id_filter(value):
    """Format an integer employee ID as a zero-padded 3-digit string (e.g. 1 → '001')."""
    return f"{int(value):03d}"


# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------

def calculate_days(start_date_str, end_date_str):
    """Return the inclusive number of days between two YYYY-MM-DD strings."""
    start = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    return (end - start).days + 1


def get_employee(conn, emp_id):
    return conn.execute(
        "SELECT * FROM employees WHERE id = ?", (emp_id,)
    ).fetchone()


# ----------------------------------------------------------------------
# Dashboard
# ----------------------------------------------------------------------

@app.route("/")
def index():
    conn = get_connection()

    employees = conn.execute(
        "SELECT * FROM employees ORDER BY id DESC"
    ).fetchall()

    leave_requests = conn.execute("""
        SELECT leave_requests.*, employees.name AS emp_name
        FROM leave_requests
        JOIN employees ON leave_requests.emp_id = employees.id
        ORDER BY leave_requests.id DESC
    """).fetchall()

    payrolls = conn.execute("""
        SELECT payrolls.*, employees.name AS emp_name
        FROM payrolls
        JOIN employees ON payrolls.emp_id = employees.id
        ORDER BY payrolls.id DESC
        LIMIT 10
    """).fetchall()

    total_employees = len(employees)
    pending_leaves = sum(1 for lr in leave_requests if lr["status"] == "Pending")

    conn.close()

    return render_template(
        "index.html",
        employees=employees,
        leave_requests=leave_requests,
        payrolls=payrolls,
        total_employees=total_employees,
        pending_leaves=pending_leaves,
        today=date.today().isoformat(),
    )


# ----------------------------------------------------------------------
# Employees
# ----------------------------------------------------------------------

@app.route("/add-employee", methods=["POST"])
def add_employee():
    name = request.form.get("name", "").strip()
    department = request.form.get("department", "").strip()
    base_salary = request.form.get("base_salary", "").strip()
    joined_date = request.form.get("joined_date", "").strip()

    if not (name and department and base_salary and joined_date):
        flash("Please fill in all employee fields.", "error")
        return redirect(url_for("index"))

    try:
        base_salary = float(base_salary)
    except ValueError:
        flash("Base salary must be a number.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    conn.execute(
        "INSERT INTO employees (name, department, base_salary, joined_date) "
        "VALUES (?, ?, ?, ?)",
        (name, department, base_salary, joined_date),
    )
    conn.commit()
    conn.close()

    flash(f"Employee '{name}' added successfully.", "success")
    return redirect(url_for("index"))


@app.route("/edit-employee/<int:emp_id>", methods=["POST"])
def edit_employee(emp_id):
    name        = request.form.get("name",        "").strip()
    department  = request.form.get("department",  "").strip()
    base_salary = request.form.get("base_salary", "").strip()
    joined_date = request.form.get("joined_date", "").strip()

    if not (name and department and base_salary and joined_date):
        flash("Please fill in all fields before saving.", "error")
        return redirect(url_for("index"))

    try:
        base_salary = float(base_salary)
    except ValueError:
        flash("Base salary must be a number.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    employee = get_employee(conn, emp_id)
    if employee is None:
        conn.close()
        flash("Employee not found.", "error")
        return redirect(url_for("index"))

    conn.execute(
        "UPDATE employees SET name = ?, department = ?, base_salary = ?, joined_date = ? "
        "WHERE id = ?",
        (name, department, base_salary, joined_date, emp_id),
    )
    conn.commit()
    conn.close()

    flash(f"Employee #{emp_id:03d} updated successfully.", "success")
    return redirect(url_for("index"))


# ----------------------------------------------------------------------
# Leave requests
# ----------------------------------------------------------------------

@app.route("/request-leave", methods=["POST"])
def request_leave():
    emp_id = request.form.get("emp_id", "").strip()
    leave_type = request.form.get("leave_type", "").strip()
    start_date = request.form.get("start_date", "").strip()
    end_date = request.form.get("end_date", "").strip()

    if not (emp_id and leave_type and start_date and end_date):
        flash("Please fill in all leave request fields.", "error")
        return redirect(url_for("index"))

    try:
        days = calculate_days(start_date, end_date)
        if days <= 0:
            raise ValueError
    except ValueError:
        flash("End date must be on or after the start date.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    employee = get_employee(conn, emp_id)
    if employee is None:
        conn.close()
        flash("Employee not found.", "error")
        return redirect(url_for("index"))

    conn.execute(
        "INSERT INTO leave_requests (emp_id, leave_type, start_date, end_date, days, status) "
        "VALUES (?, ?, ?, ?, ?, 'Pending')",
        (emp_id, leave_type, start_date, end_date, days),
    )
    conn.commit()
    conn.close()

    flash("Leave request submitted.", "success")
    return redirect(url_for("index"))


@app.route("/process-leave/<int:leave_id>", methods=["POST"])
def process_leave(leave_id):
    action = request.form.get("action", "")  # "approve" or "reject"
    new_status = "Approved" if action == "approve" else "Rejected"

    conn = get_connection()
    leave = conn.execute(
        "SELECT * FROM leave_requests WHERE id = ?", (leave_id,)
    ).fetchone()

    if leave is None:
        conn.close()
        flash("Leave request not found.", "error")
        return redirect(url_for("index"))

    conn.execute(
        "UPDATE leave_requests SET status = ? WHERE id = ?",
        (new_status, leave_id),
    )
    conn.commit()
    conn.close()

    flash(f"Leave request #{leave_id} marked as {new_status}.", "success")
    return redirect(url_for("index"))


# ----------------------------------------------------------------------
# Payroll
# ----------------------------------------------------------------------

@app.route("/generate-payroll", methods=["POST"])
def generate_payroll():
    emp_id = request.form.get("emp_id", "").strip()
    month_year = request.form.get("month_year", "").strip()  # e.g. "2026-11"

    if not (emp_id and month_year):
        flash("Please choose an employee and a month.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    employee = get_employee(conn, emp_id)
    if employee is None:
        conn.close()
        flash("Employee not found.", "error")
        return redirect(url_for("index"))

    base_salary = employee["base_salary"]
    daily_rate = base_salary / 30

    # Sum approved Unpaid leave days that fall within the selected month.
    # start_date is stored as "YYYY-MM-DD", so matching the "YYYY-MM" prefix
    # keeps the SQL simple and avoids date-arithmetic functions.
    row = conn.execute("""
        SELECT COALESCE(SUM(days), 0) AS unpaid_total
        FROM leave_requests
        WHERE emp_id = ?
          AND leave_type = 'Unpaid'
          AND status = 'Approved'
          AND substr(start_date, 1, 7) = ?
    """, (emp_id, month_year)).fetchone()

    unpaid_days = row["unpaid_total"]
    leave_deduction = round(daily_rate * unpaid_days, 2)
    net_salary = round(base_salary - leave_deduction, 2)

    conn.execute("""
        INSERT INTO payrolls (emp_id, month_year, basic_pay, unpaid_days, leave_deduction, net_salary)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (emp_id, month_year, base_salary, unpaid_days, leave_deduction, net_salary))
    conn.commit()
    conn.close()

    flash(
        f"Payroll generated for {employee['name']} ({month_year}): "
        f"Net Salary = {net_salary}",
        "success",
    )
    return redirect(url_for("index"))


# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------

if __name__ == "__main__":
    init_db()  # make sure tables exist before the app starts
    app.run(debug=True)

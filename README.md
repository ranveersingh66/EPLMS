# Employee Payroll & Leave Management System

A lightweight web application built with **Flask** and **SQLite** to manage employee records, leave requests, and monthly payroll — with a clean, no-framework dashboard UI.

---

## Features

- **Employee Management** — Add, edit, and view employees with zero-padded IDs (001, 002, …)
- **Leave Requests** — Submit Sick, Casual, or Unpaid leave; approve or reject from the dashboard
- **Payroll Generation** — Auto-calculates net salary after deducting approved unpaid leave days
- **Summary Dashboard** — At-a-glance cards for total employees, pending leaves, and recent payslips
- **Edit Modal** — Inline modal to update any employee's name, department, salary, or join date

---

## Tech Stack

| Layer     | Technology          |
|-----------|---------------------|
| Backend   | Python 3, Flask     |
| Database  | SQLite (via `sqlite3`) |
| Frontend  | HTML, CSS (custom, no framework) |
| Templating | Jinja2             |

---

## Project Structure

```
EPLMS/
├── app.py          # Flask routes and application logic
├── database.py     # DB connection and table initialisation
├── seed.py         # Inserts 10 dummy employees for development
├── payroll.db      # SQLite database (auto-created on first run)
├── static/
│   └── style.css   # All custom styles
└── templates/
    └── index.html  # Single-page dashboard (tabs + modal)
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/EPLMS.git
cd EPLMS
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install flask
```

### 4. Run the app

```bash
python app.py
```

The app initialises the database automatically on first launch. Open your browser and go to:

```
http://127.0.0.1:5000
```

### 5. (Optional) Load dummy data

```bash
python seed.py
```

Inserts 10 sample employees. Safe to run multiple times — skips if 10+ employees already exist.

---

## Usage

| Tab | What you can do |
|-----|-----------------|
| **Employees** | Add a new employee · Click ✏️ Edit on any row to update details |
| **Leave** | Submit a leave request for any employee · Approve or Reject pending requests |
| **Payroll** | Select an employee and a month to generate a payslip · Net salary = Base salary − (daily rate × approved unpaid days) |

---

## Payroll Formula

```
Daily Rate      = Base Salary ÷ 30
Leave Deduction = Daily Rate × Approved Unpaid Leave Days (in that month)
Net Salary      = Base Salary − Leave Deduction
```

---




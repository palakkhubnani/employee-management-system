from flask import Flask, request, jsonify, render_template
import sqlite3
import re

app = Flask(__name__)
DATABASE = "employees.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            position TEXT NOT NULL,
            salary REAL NOT NULL,
            contact TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def validate_employee(data):
    required = [
        "employee_id",
        "name",
        "department",
        "position",
        "salary",
        "contact",
        "email"
    ]

    for field in required:
        if field not in data or str(data[field]).strip() == "":
            return f"{field.replace('_', ' ').title()} is required."

    try:
        salary = float(data["salary"])
    except (ValueError, TypeError):
        return "Salary must be a number."

    if salary < 0:
        return "Salary cannot be negative."

    if not re.fullmatch(r"\d{10}", str(data["contact"]).strip()):
        return "Contact number must contain exactly 10 digits."

    if not re.fullmatch(
        r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
        str(data["email"]).strip()
    ):
        return "Please enter a valid email address."

    return None


@app.route("/")
def home():
    return render_template("index.html")


# GET - view/search employees
@app.route("/api/employees", methods=["GET"])
def get_employees():
    search = request.args.get("search", "").strip()

    conn = get_db_connection()

    if search:
        employees = conn.execute("""
            SELECT * FROM employees
            WHERE name LIKE ?
               OR employee_id LIKE ?
               OR department LIKE ?
            ORDER BY id DESC
        """, (
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        )).fetchall()
    else:
        employees = conn.execute(
            "SELECT * FROM employees ORDER BY id DESC"
        ).fetchall()

    conn.close()

    return jsonify([dict(employee) for employee in employees])


# POST - add employee
@app.route("/api/employees", methods=["POST"])
def add_employee():
    data = request.get_json(silent=True) or {}

    error = validate_employee(data)

    if error:
        return jsonify({"error": error}), 400

    conn = get_db_connection()

    try:
        conn.execute("""
            INSERT INTO employees
            (employee_id, name, department, position, salary, contact, email)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data["employee_id"].strip(),
            data["name"].strip(),
            data["department"].strip(),
            data["position"].strip(),
            float(data["salary"]),
            data["contact"].strip(),
            data["email"].strip()
        ))

        conn.commit()

    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({
            "error": "Employee ID already exists."
        }), 409

    conn.close()

    return jsonify({
        "message": "Employee added successfully."
    }), 201


# PUT - update employee
@app.route("/api/employees/<int:employee_id>", methods=["PUT"])
def update_employee(employee_id):
    data = request.get_json(silent=True) or {}

    error = validate_employee(data)

    if error:
        return jsonify({"error": error}), 400

    conn = get_db_connection()

    existing = conn.execute(
        "SELECT * FROM employees WHERE id = ?",
        (employee_id,)
    ).fetchone()

    if existing is None:
        conn.close()
        return jsonify({
            "error": "Employee not found."
        }), 404

    try:
        conn.execute("""
            UPDATE employees
            SET employee_id = ?,
                name = ?,
                department = ?,
                position = ?,
                salary = ?,
                contact = ?,
                email = ?
            WHERE id = ?
        """, (
            data["employee_id"].strip(),
            data["name"].strip(),
            data["department"].strip(),
            data["position"].strip(),
            float(data["salary"]),
            data["contact"].strip(),
            data["email"].strip(),
            employee_id
        ))

        conn.commit()

    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({
            "error": "Employee ID already exists."
        }), 409

    conn.close()

    return jsonify({
        "message": "Employee updated successfully."
    })


# DELETE - delete employee
@app.route("/api/employees/<int:employee_id>", methods=["DELETE"])
def delete_employee(employee_id):
    conn = get_db_connection()

    cursor = conn.execute(
        "DELETE FROM employees WHERE id = ?",
        (employee_id,)
    )

    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        return jsonify({
            "error": "Employee not found."
        }), 404

    return jsonify({
        "message": "Employee deleted successfully."
    })


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
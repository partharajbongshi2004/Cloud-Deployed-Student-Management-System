import sqlite3
from typing import List, Tuple, Optional, Dict, Any

DB_NAME = "students.db"


def get_connection() -> sqlite3.Connection:
    """Create and return a thread-safe SQLite database connection."""
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize the database and create the students table if it does not exist."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT UNIQUE NOT NULL,
                    full_name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    department TEXT NOT NULL,
                    semester INTEGER NOT NULL,
                    gpa REAL NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()
    except sqlite3.Error as e:
        raise RuntimeError(f"Database initialization error: {e}")


def add_student(
    student_id: str,
    full_name: str,
    email: str,
    department: str,
    semester: int,
    gpa: float,
    status: str = "Active",
) -> Tuple[bool, str]:
    """Insert a new student record into the database."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO students (student_id, full_name, email, department, semester, gpa, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (student_id.strip(), full_name.strip(), email.strip().lower(), department, semester, gpa, status),
            )
            conn.commit()
        return True, "Student added successfully!"
    except sqlite3.IntegrityError as e:
        if "student_id" in str(e):
            return False, "A student with this Student ID already exists."
        if "email" in str(e):
            return False, "A student with this Email already exists."
        return False, "Integrity error: Duplicate or invalid data."
    except sqlite3.Error as e:
        return False, f"Database error: {e}"


def get_all_students(
    search_query: str = "", department_filter: str = "All", status_filter: str = "All"
) -> List[Dict[str, Any]]:
    """Retrieve students with optional search and filter parameters."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM students WHERE 1=1"
            params: List[Any] = []

            if search_query.strip():
                query += " AND (full_name LIKE ? OR student_id LIKE ? OR email LIKE ?)"
                like_term = f"%{search_query.strip()}%"
                params.extend([like_term, like_term, like_term])

            if department_filter != "All":
                query += " AND department = ?"
                params.append(department_filter)

            if status_filter != "All":
                query += " AND status = ?"
                params.append(status_filter)

            query += " ORDER BY created_at DESC"
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except sqlite3.Error as e:
        raise RuntimeError(f"Error fetching student records: {e}")


def get_student_by_id(record_id: int) -> Optional[Dict[str, Any]]:
    """Fetch a single student record by primary key ID."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students WHERE id = ?", (record_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    except sqlite3.Error as e:
        raise RuntimeError(f"Error fetching student: {e}")


def update_student(
    record_id: int,
    student_id: str,
    full_name: str,
    email: str,
    department: str,
    semester: int,
    gpa: float,
    status: str,
) -> Tuple[bool, str]:
    """Update an existing student record."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE students
                SET student_id = ?, full_name = ?, email = ?, department = ?, semester = ?, gpa = ?, status = ?
                WHERE id = ?
                """,
                (
                    student_id.strip(),
                    full_name.strip(),
                    email.strip().lower(),
                    department,
                    semester,
                    gpa,
                    status,
                    record_id,
                ),
            )
            if cursor.rowcount == 0:
                return False, "Student record not found."
            conn.commit()
        return True, "Student record updated successfully!"
    except sqlite3.IntegrityError:
        return False, "Student ID or Email already belongs to another student."
    except sqlite3.Error as e:
        return False, f"Database error: {e}"


def delete_student(record_id: int) -> Tuple[bool, str]:
    """Delete a student record by primary key ID."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM students WHERE id = ?", (record_id,))
            if cursor.rowcount == 0:
                return False, "Student record not found."
            conn.commit()
        return True, "Student record deleted successfully!"
    except sqlite3.Error as e:
        return False, f"Database error: {e}"

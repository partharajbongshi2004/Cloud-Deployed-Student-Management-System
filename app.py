import re
import pandas as pd
import streamlit as st
from database import (
    init_db,
    add_student,
    get_all_students,
    update_student,
    delete_student,
)

# 1. Page Configuration (Must be the first Streamlit command)
st.set_page_config(
    page_title="Student Management System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Initialize SQLite Database Safely
try:
    init_db()
except Exception as e:
    st.error(f"Failed to initialize database: {e}")
    st.stop()

# Constants
DEPARTMENTS = [
    "Computer Science",
    "Electrical Engineering",
    "Mechanical Engineering",
    "Business Administration",
    "Data Science",
    "Civil Engineering",
]
STATUS_OPTIONS = ["Active", "Graduated", "On Leave", "Suspended"]


def validate_inputs(student_id: str, full_name: str, email: str, gpa: float) -> tuple[bool, str]:
    """Validate user inputs before database operations."""
    if not student_id.strip():
        return False, "Student ID cannot be empty."
    if not full_name.strip() or len(full_name.strip()) < 2:
        return False, "Please enter a valid full name (at least 2 characters)."
    if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email.strip()):
        return False, "Please enter a valid email address."
    if not (0.0 <= gpa <= 4.0):
        return False, "GPA must be between 0.00 and 4.00."
    return True, ""


def main():
    # Sidebar Navigation
    st.sidebar.title("🎓 Navigation")
    menu = st.sidebar.radio(
        "Select Action",
        ["View", "Add", "Update", "Delete"],
        index=0,
    )
    st.sidebar.divider()
    st.sidebar.caption("Student Management System • Cloud Ready")

    # Main Header
    st.title("🎓 Student Management System")

    # Fetch all records once for metrics and dropdowns
    try:
        all_students = get_all_students()
    except Exception as e:
        st.error(f"Error loading student records: {e}")
        all_students = []

    df_all = pd.DataFrame(all_students)

    # Top KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    total_students = len(df_all)
    active_students = len(df_all[df_all["status"] == "Active"]) if not df_all.empty else 0
    avg_gpa = round(df_all["gpa"].mean(), 2) if not df_all.empty else 0.00
    total_depts = df_all["department"].nunique() if not df_all.empty else 0

    col1.metric("Total Students", total_students)
    col2.metric("Active Students", active_students)
    col3.metric("Average GPA", f"{avg_gpa:.2f}")
    col4.metric("Departments", total_depts)
    st.divider()

    # =========================================================
    # 1. VIEW STUDENTS
    # =========================================================
    if menu == "View":
        st.subheader("📊 Student Directory")

        f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
        with f_col1:
            search_query = st.text_input(
                "Search",
                placeholder="Search by Name, Student ID, or Email...",
                label_visibility="collapsed",
            )
        with f_col2:
            dept_filter = st.selectbox(
                "Department",
                ["All"] + DEPARTMENTS,
                label_visibility="collapsed",
            )
        with f_col3:
            status_filter = st.selectbox(
                "Status",
                ["All"] + STATUS_OPTIONS,
                label_visibility="collapsed",
            )

        filtered_students = get_all_students(search_query, dept_filter, status_filter)

        if filtered_students:
            df_filtered = pd.DataFrame(filtered_students)
            display_cols = ["student_id", "full_name", "email", "department", "semester", "gpa", "status"]

            st.dataframe(
                df_filtered[display_cols],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "student_id": st.column_config.TextColumn("Student ID"),
                    "full_name": st.column_config.TextColumn("Full Name"),
                    "email": st.column_config.TextColumn("Email Address"),
                    "department": st.column_config.TextColumn("Department"),
                    "semester": st.column_config.NumberColumn("Semester", format="%d"),
                    "gpa": st.column_config.NumberColumn("GPA", format="%.2f"),
                    "status": st.column_config.TextColumn("Status"),
                },
            )

            csv_data = df_filtered[display_cols].to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Export to CSV",
                data=csv_data,
                file_name="students_directory.csv",
                mime="text/csv",
            )
        else:
            st.info("No student records found. Use the **Add** option in the sidebar to create one.")

    # =========================================================
    # 2. ADD STUDENT
    # =========================================================
    elif menu == "Add":
        st.subheader("➕ Register New Student")

        with st.form("add_student_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                student_id = st.text_input("Student ID *", placeholder="e.g., STU-2026-001")
                full_name = st.text_input("Full Name *", placeholder="e.g., Jane Doe")
                email = st.text_input("Email Address *", placeholder="e.g., jane.doe@university.edu")
            with c2:
                department = st.selectbox("Department *", DEPARTMENTS)
                semester = st.number_input("Semester *", min_value=1, max_value=12, value=1, step=1)
                gpa = st.number_input("GPA (0.00 - 4.00) *", min_value=0.0, max_value=4.0, value=3.50, step=0.01)

            status = st.selectbox("Enrollment Status", STATUS_OPTIONS, index=0)
            submitted = st.form_submit_button("Save Student", type="primary")

            if submitted:
                is_valid, error_msg = validate_inputs(student_id, full_name, email, gpa)
                if not is_valid:
                    st.error(error_msg)
                else:
                    success, message = add_student(
                        student_id=student_id,
                        full_name=full_name,
                        email=email,
                        department=department,
                        semester=int(semester),
                        gpa=float(gpa),
                        status=status,
                    )
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

    # =========================================================
    # 3. UPDATE STUDENT
    # =========================================================
    elif menu == "Update":
        st.subheader("✏️ Update Student Record")

        if not all_students:
            st.info("No student records available to update.")
        else:
            student_map = {
                f"{s['student_id']} - {s['full_name']}": s for s in all_students
            }
            selected_label = st.selectbox("Select Student to Edit", list(student_map.keys()))
            selected_student = student_map[selected_label]

            with st.form("update_student_form"):
                c1, c2 = st.columns(2)
                with c1:
                    edit_student_id = st.text_input("Student ID *", value=selected_student["student_id"])
                    edit_full_name = st.text_input("Full Name *", value=selected_student["full_name"])
                    edit_email = st.text_input("Email Address *", value=selected_student["email"])
                with c2:
                    dept_idx = (
                        DEPARTMENTS.index(selected_student["department"])
                        if selected_student["department"] in DEPARTMENTS
                        else 0
                    )
                    edit_department = st.selectbox("Department *", DEPARTMENTS, index=dept_idx)
                    edit_semester = st.number_input(
                        "Semester *",
                        min_value=1,
                        max_value=12,
                        value=int(selected_student["semester"]),
                        step=1,
                    )
                    edit_gpa = st.number_input(
                        "GPA (0.00 - 4.00) *",
                        min_value=0.0,
                        max_value=4.0,
                        value=float(selected_student["gpa"]),
                        step=0.01,
                    )

                status_idx = (
                    STATUS_OPTIONS.index(selected_student["status"])
                    if selected_student["status"] in STATUS_OPTIONS
                    else 0
                )
                edit_status = st.selectbox("Enrollment Status", STATUS_OPTIONS, index=status_idx)
                updated = st.form_submit_button("Update Student", type="primary")

                if updated:
                    is_valid, error_msg = validate_inputs(
                        edit_student_id, edit_full_name, edit_email, edit_gpa
                    )
                    if not is_valid:
                        st.error(error_msg)
                    else:
                        success, message = update_student(
                            record_id=selected_student["id"],
                            student_id=edit_student_id,
                            full_name=edit_full_name,
                            email=edit_email,
                            department=edit_department,
                            semester=int(edit_semester),
                            gpa=float(edit_gpa),
                            status=edit_status,
                        )
                        if success:
                            st.success(message)

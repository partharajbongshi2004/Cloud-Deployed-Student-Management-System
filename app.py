import re
import pandas as pd
import streamlit as st

# 1. Page Configuration (Must be the very first Streamlit command)
st.set_page_config(
    page_title="Student Management System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

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


def init_session_state() -> None:
    """Initialize st.session_state with sample student records on first load."""
    if "students" not in st.session_state:
        st.session_state.students = [
            {
                "student_id": "STU-2026-001",
                "full_name": "Ayesha Rahman",
                "email": "ayesha.rahman@university.edu",
                "department": "Computer Science",
                "semester": 4,
                "gpa": 3.85,
                "status": "Active",
            },
            {
                "student_id": "STU-2026-002",
                "full_name": "Lucas Silva",
                "email": "lucas.silva@university.edu",
                "department": "Data Science",
                "semester": 6,
                "gpa": 3.62,
                "status": "Active",
            },
            {
                "student_id": "STU-2026-003",
                "full_name": "Nadia Islam",
                "email": "nadia.islam@university.edu",
                "department": "Electrical Engineering",
                "semester": 8,
                "gpa": 3.91,
                "status": "Graduated",
            },
        ]


def validate_student(
    student_id: str,
    full_name: str,
    email: str,
    gpa: float,
    original_id: str | None = None,
) -> tuple[bool, str]:
    """Validate form inputs and check for duplicate Student IDs or Emails."""
    clean_id = student_id.strip()
    clean_name = full_name.strip()
    clean_email = email.strip().lower()

    if not clean_id:
        return False, "Student ID cannot be empty."
    if len(clean_name) < 2:
        return False, "Full Name must be at least 2 characters long."
    if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", clean_email):
        return False, "Please enter a valid email address."
    if not (0.0 <= gpa <= 4.0):
        return False, "GPA must be between 0.00 and 4.00."

    for s in st.session_state.students:
        if original_id is not None and s["student_id"] == original_id:
            continue
        if s["student_id"].lower() == clean_id.lower():
            return False, f"Student ID '{clean_id}' already exists."
        if s["email"].lower() == clean_email:
            return False, f"Email '{clean_email}' is already registered."

    return True, ""


def main() -> None:
    init_session_state()

    # Sidebar Navigation
    st.sidebar.title("🎓 Navigation")
    menu = st.sidebar.radio(
        "Select Action",
        ["View Students", "Add Student", "Update Student", "Delete Student"],
        index=0,
    )
    st.sidebar.divider()
    st.sidebar.info("Data is stored in active session memory.")

    # Main Header
    st.title("🎓 Student Management System")

    # Convert session state to DataFrame for KPIs
    df_all = pd.DataFrame(st.session_state.students)

    # Top KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    total_students = len(df_all)
    active_students = int((df_all["status"] == "Active").sum()) if not df_all.empty else 0
    avg_gpa = float(df_all["gpa"].mean()) if not df_all.empty else 0.00
    total_depts = int(df_all["department"].nunique()) if not df_all.empty else 0

    col1.metric("Total Students", total_students)
    col2.metric("Active Students", active_students)
    col3.metric("Average GPA", f"{avg_gpa:.2f}")
    col4.metric("Departments", total_depts)
    st.divider()

    # =========================================================
    # 1. VIEW STUDENTS
    # =========================================================
    if menu == "View Students":
        st.subheader("📊 Student Directory")

        if df_all.empty:
            st.info("No student records found. Select **Add Student** from the sidebar to begin.")
            return

        # Search and Filter Controls
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

        # Filter DataFrame
        df_filtered = df_all.copy()
        if search_query.strip():
            q = search_query.strip().lower()
            df_filtered = df_filtered[
                df_filtered["student_id"].str.lower().str.contains(q, na=False)
                | df_filtered["full_name"].str.lower().str.contains(q, na=False)
                | df_filtered["email"].str.lower().str.contains(q, na=False)
            ]
        if dept_filter != "All":
            df_filtered = df_filtered[df_filtered["department"] == dept_filter]
        if status_filter != "All":
            df_filtered = df_filtered[df_filtered["status"] == status_filter]

        if df_filtered.empty:
            st.warning("No matching student records found.")
        else:
            st.dataframe(
                df_filtered,
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

            csv_bytes = df_filtered.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download CSV",
                data=csv_bytes,
                file_name="student_directory.csv",
                mime="text/csv",
            )

    # =========================================================
    # 2. ADD STUDENT
    # =========================================================
    elif menu == "Add Student":
        st.subheader("➕ Add New Student")

        with st.form("add_student_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                student_id = st.text_input("Student ID *", placeholder="e.g., STU-2026-004")
                full_name = st.text_input("Full Name *", placeholder="e.g., Tanvir Ahmed")
                email = st.text_input("Email Address *", placeholder="e.g., tanvir@university.edu")
            with c2:
                department = st.selectbox("Department *", DEPARTMENTS)
                semester = st.number_input("Semester *", min_value=1, max_value=12, value=1, step=1)
                gpa = st.number_input("GPA (0.00 - 4.00) *", min_value=0.0, max_value=4.0, value=3.50, step=0.01)

            status = st.selectbox("Enrollment Status", STATUS_OPTIONS, index=0)
            submitted = st.form_submit_button("Save Student", type="primary")

            if submitted:
                is_valid, err_msg = validate_student(student_id, full_name, email, float(gpa))
                if not is_valid:
                    st.error(err_msg)
                else:
                    st.session_state.students.append(
                        {
                            "student_id": student_id.strip(),
                            "full_name": full_name.strip(),
                            "email": email.strip().lower(),
                            "department": department,
                            "semester": int(semester),
                            "gpa": round(float(gpa), 2),
                            "status": status,
                        }
                    )
                    st.success(f"Student '{full_name.strip()}' added successfully!")
                    st.rerun()

if __name__ == "__main__": main()
      

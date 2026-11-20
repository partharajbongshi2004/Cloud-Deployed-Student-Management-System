# 🎓 Student Management System

A clean, modern, cloud-ready Student Management System built with **Python**, **Streamlit**, and **SQLite**. Designed for effortless deployment on **Streamlit Community Cloud**.

## ✨ Features
- **Full CRUD Operations**: Create, Read, Update, and Delete student records with real-time database updates.
- **Interactive Dashboard**: Live KPI metrics tracking total students, active enrollments, average GPA, and active departments.
- **Smart Search & Filtering**: Filter records dynamically by student name, ID, email, department, or enrollment status.
- **Input Validation & Integrity**: Enforces unique Student IDs and emails, valid email formatting, and GPA bounds (`0.00` – `4.00`).
- **Data Export**: One-click CSV export for filtered student directories.

## 📂 Project Structure
```text
├── app.py              # Main Streamlit dashboard and UI logic
├── database.py         # SQLite connection and CRUD operations
├── requirements.txt    # Python dependencies for Streamlit Cloud
└── README.md           # Project documentation
```

## 🚀 Local Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com
   cd student-management-system
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   streamlit run app.py
   ```

## ☁️ Deploying on Streamlit Community Cloud

1. Push `app.py`, `database.py`, `requirements.txt`, and `README.md` to a public or private GitHub repository.
2. Go to [share.streamlit.io](https://streamlit.io) and sign in with GitHub.
3. Click **New app**, select your repository, branch (`main`), and set the main file path to `app.py`.
4. Click **Deploy!**

> **Note on SQLite Persistence:** Streamlit Community Cloud uses an ephemeral filesystem. Data stored in `students.db` persists while the app container is active, but will reset if the app reboots or redeploys. For permanent cloud persistence, connect `database.py` to a hosted database like PostgreSQL (Supabase/Neon) or Turso.

import streamlit as st
import pandas as pd
from datetime import date
import pymysql


def get_connection():
    try:
        return pymysql.connect(
            host="localhost",
            user="root",
            password="root123",   # change this if your MySQL password is different
            database="attendance_db"
        )
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None


def mark_attendance(roll_no, name, status):
    today = date.today()
    conn = get_connection()

    if conn is None:
        return

    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO attendance (roll_no, name, date, status)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                status = VALUES(status)
        """, (roll_no.strip(), name.strip(), today, status))

        conn.commit()
        st.success("Attendance saved successfully.")
    except Exception as e:
        st.error(f"Error while saving attendance: {e}")
    finally:
        conn.close()


def view_today_attendance():
    today = date.today()
    conn = get_connection()

    if conn is None:
        return

    cursor = conn.cursor()

    try:
        cursor.execute("SELECT roll_no, name, date, status FROM attendance WHERE date = %s", (today,))
        data = cursor.fetchall()

        df = pd.DataFrame(data, columns=["Roll No", "Name", "Date", "Status"])

        if df.empty:
            st.info("No attendance records for today.")
        else:
            st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Error while fetching today's attendance: {e}")
    finally:
        conn.close()


def generate_full_report():
    conn = get_connection()

    if conn is None:
        return

    cursor = conn.cursor()

    try:
        cursor.execute("SELECT roll_no, name, date, status FROM attendance")
        data = cursor.fetchall()

        df = pd.DataFrame(data, columns=["Roll No", "Name", "Date", "Status"])

        if df.empty:
            st.info("No attendance data available.")
            return

        report = df.groupby(["Roll No", "Name", "Status"]).size().unstack(fill_value=0)
        st.dataframe(report, use_container_width=True)
    except Exception as e:
        st.error(f"Error while generating report: {e}")
    finally:
        conn.close()


def export_to_excel():
    conn = get_connection()

    if conn is None:
        return

    cursor = conn.cursor()

    try:
        cursor.execute("SELECT roll_no, name, date, status FROM attendance")
        data = cursor.fetchall()

        df = pd.DataFrame(data, columns=["Roll No", "Name", "Date", "Status"])

        if df.empty:
            st.warning("No data to export.")
            return

        file_name = "attendance_report.xlsx"
        df.to_excel(file_name, index=False)
        st.success(f"Exported successfully as {file_name}")
    except Exception as e:
        st.error(f"Error while exporting: {e}")
    finally:
        conn.close()


def delete_student_record(roll_no):
    conn = get_connection()

    if conn is None:
        return

    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM attendance WHERE roll_no = %s", (roll_no.strip(),))
        conn.commit()
        st.success(f"All records for Roll No {roll_no} deleted.")
    except Exception as e:
        st.error(f"Error while deleting student record: {e}")
    finally:
        conn.close()


def search_student(roll_no):
    conn = get_connection()

    if conn is None:
        return

    cursor = conn.cursor()

    try:
        cursor.execute("SELECT roll_no, name, date, status FROM attendance WHERE roll_no = %s", (roll_no.strip(),))
        data = cursor.fetchall()

        df = pd.DataFrame(data, columns=["Roll No", "Name", "Date", "Status"])

        if df.empty:
            st.info("No records found.")
        else:
            st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Error while searching student: {e}")
    finally:
        conn.close()


def reset_attendance():
    conn = get_connection()

    if conn is None:
        return

    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM attendance")
        conn.commit()
        st.success("Attendance database reset successfully.")
    except Exception as e:
        st.error(f"Error while resetting attendance: {e}")
    finally:
        conn.close()


st.set_page_config(page_title="Attendance Tracker", layout="wide")
st.title("🎓 Attendance Management System")

menu = st.sidebar.selectbox(
    "Menu",
    [
        "Mark Attendance",
        "View Today's Attendance",
        "Generate Full Report",
        "Export to Excel",
        "Search Student",
        "Delete Student",
        "Reset Attendance"
    ]
)

if menu == "Mark Attendance":
    st.header("Mark Attendance")

    roll_no = st.text_input("Roll Number")
    name = st.text_input("Student Name")
    status = st.selectbox("Status", ["Present", "Absent"])

    if st.button("Submit Attendance"):
        if roll_no.strip() and name.strip():
            mark_attendance(roll_no, name, status)
        else:
            st.warning("Roll number and name are required.")

elif menu == "View Today's Attendance":
    st.header("Today's Attendance")
    view_today_attendance()

elif menu == "Generate Full Report":
    st.header("Full Attendance Report")
    generate_full_report()

elif menu == "Export to Excel":
    st.header("Export Attendance")
    export_to_excel()

elif menu == "Search Student":
    st.header("Search Student Attendance")
    roll_no = st.text_input("Enter Roll Number")
    if st.button("Search"):
        if roll_no.strip():
            search_student(roll_no)
        else:
            st.warning("Please enter a roll number.")

elif menu == "Delete Student":
    st.header("Delete Student Records")
    roll_no = st.text_input("Enter Roll Number to Delete")
    if st.button("Delete"):
        if roll_no.strip():
            delete_student_record(roll_no)
        else:
            st.warning("Please enter a roll number.")

elif menu == "Reset Attendance":
    st.header("Reset Attendance Database")
    st.warning("This will delete all attendance records.")
    if st.button("Reset All Data"):
        reset_attendance()

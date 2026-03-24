import streamlit as st
import pandas as pd
from datetime import date
import pymysql


def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="root123",  
        database="attendance_db"
    )


def mark_attendance(roll_no, name, status):
    today = date.today()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO attendance (roll_no, name, date, status)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    status = VALUES(status)
    """, (roll_no.strip(), name.strip(), today, status))

    conn.commit()
    conn.close()


def view_today_attendance():
    today = date.today()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM attendance WHERE date = %s", (today,))
    data = cursor.fetchall()

    conn.close()

    df = pd.DataFrame(data, columns=["Roll No", "Name", "Date", "Status"])

    if df.empty:
        st.info("No attendance records for today.")
    else:
        st.dataframe(df)


def generate_full_report():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM attendance")
    data = cursor.fetchall()

    conn.close()

    df = pd.DataFrame(data, columns=["Roll No", "Name", "Date", "Status"])

    if df.empty:
        st.info("No attendance data available.")
        return

    report = (
        df.groupby(["Roll No", "Name", "Status"])
        .size()
        .unstack(fill_value=0)
    )

    st.dataframe(report)


def export_to_excel():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM attendance")
    data = cursor.fetchall()

    conn.close()

    df = pd.DataFrame(data, columns=["Roll No", "Name", "Date", "Status"])

    if df.empty:
        st.warning("No data to export.")
        return

    df.to_excel("attendance_report.xlsx", index=False)
    st.success("Exported as attendance_report.xlsx")


def delete_student_record(roll_no):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM attendance WHERE roll_no = %s", (roll_no.strip(),))
    conn.commit()
    conn.close()

    st.success(f"All records for Roll No {roll_no} deleted.")


def search_student(roll_no):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM attendance WHERE roll_no = %s", (roll_no.strip(),))
    data = cursor.fetchall()

    conn.close()

    df = pd.DataFrame(data, columns=["Roll No", "Name", "Date", "Status"])

    if df.empty:
        st.info("No records found.")
    else:
        st.dataframe(df)


def reset_attendance():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM attendance")
    conn.commit()
    conn.close()

    st.success("Attendance database reset successfully.")


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
        if roll_no and name:
            mark_attendance(roll_no, name, status)
            st.success("Attendance saved successfully (no duplicates possible).")
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
        search_student(roll_no)


elif menu == "Delete Student":
    st.header("Delete Student Records")
    roll_no = st.text_input("Enter Roll Number to Delete")
    if st.button("Delete"):
        delete_student_record(roll_no)


elif menu == "Reset Attendance":
    st.header("Reset Attendance Database")
    if st.button("Reset All Data"):
        reset_attendance()

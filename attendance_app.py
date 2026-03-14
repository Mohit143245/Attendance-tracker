import streamlit as st
import pandas as pd
import csv
import os
from datetime import date

FILE_NAME = "attendance.csv"

# ==========================================
# Utility functions
# ==========================================
def load_data():
    if os.path.exists(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
    else:
        df = pd.DataFrame(columns=["Roll No", "Name", "Date", "Status"])
    return df


def save_data(df):
    df.to_csv(FILE_NAME, index=False)


# ==========================================
# CORE: HARD DUPLICATE-PROOF MARK ATTENDANCE
# ==========================================
def mark_attendance(roll_no, name, status):
    today = date.today().strftime("%Y-%m-%d")
    df = load_data()

    # Normalize data
    df["Roll No"] = df["Roll No"].astype(str).str.strip()
    df["Date"] = df["Date"].astype(str).str.strip()

    roll_no = str(roll_no).strip()
    name = name.strip()

    # HARD DELETE existing record for same Roll No + Date
    df = df[~((df["Roll No"] == roll_no) & (df["Date"] == today))]

    # Insert fresh record
    new_row = pd.DataFrame([{
        "Roll No": roll_no,
        "Name": name,
        "Date": today,
        "Status": status
    }])

    df = pd.concat([df, new_row], ignore_index=True)
    save_data(df)


# ==========================================
# Other features
# ==========================================
def view_today_attendance():
    df = load_data()
    today = date.today().strftime("%Y-%m-%d")
    today_df = df[df["Date"] == today]

    if today_df.empty:
        st.info("No attendance records for today.")
    else:
        st.dataframe(today_df)


def generate_full_report():
    df = load_data()
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
    df = load_data()
    if df.empty:
        st.warning("No data to export.")
        return

    df.to_excel("attendance_report.xlsx", index=False)
    st.success("Exported as attendance_report.xlsx")


def delete_student_record(roll_no):
    df = load_data()
    roll_no = str(roll_no).strip()
    df = df[df["Roll No"].astype(str) != roll_no]
    save_data(df)
    st.success(f"All records for Roll No {roll_no} deleted.")


def search_student(roll_no):
    df = load_data()
    roll_no = str(roll_no).strip()
    result = df[df["Roll No"].astype(str) == roll_no]

    if result.empty:
        st.info("No records found.")
    else:
        st.dataframe(result)


def reset_attendance():
    df = pd.DataFrame(columns=["Roll No", "Name", "Date", "Status"])
    save_data(df)
    st.success("Attendance file reset successfully.")


# ==========================================
# Streamlit UI
# ==========================================
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

# ==========================================
# Menu Actions
# ==========================================
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
    st.header("Reset Attendance File")
    if st.button("Reset All Data"):
        reset_attendance()

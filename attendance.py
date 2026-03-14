import csv
from datetime import date
import pandas as pd
from datetime import date
import speech_recognition as sr 
import os

# ===================================================
# Function 1: Mark Attendance
# ===================================================
def mark_attendance():
    name = input("Enter student name: ")
    status = input("Enter status (Present/Absent): ").capitalize()
    today = date.today().strftime("%Y-%m-%d")

    with open("attendance.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        if file.tell() == 0:  
            writer.writerow(["Name", "Date", "Status"])
        writer.writerow([name, today, status])

    print(f" Attendance marked for {name}: {status}")

# ===================================================
# Function 2: View Today’s Attendance
# ===================================================
def view_attendance():
    today = date.today().strftime("%Y-%m-%d")
    print(f"\n Attendance for {today}:\n")

    try:
        with open("attendance.csv", mode="r") as file:
            reader = csv.reader(file)
            next(reader)  
            found = False
            for row in reader:
                if row[1] == today:
                    print(f"{row[0]} → {row[2]}")
                    found = True
            if not found:
                print("No attendance records found for today.")
    except FileNotFoundError:
        print(" No attendance file found!")


# ===================================================
# Function 3: Generate Full Report (Present/Absent count)
# ===================================================
def generate_report():
    report = {}

    try:
        with open("attendance.csv", mode="r") as file:
            reader = csv.reader(file)
            next(reader)  
            for row in reader:
                name, _, status = row
                if name not in report:
                    report[name] = {"Present": 0, "Absent": 0}
                report[name][status] += 1

        print("\n Full Attendance Report:")
        for name, counts in report.items():
            print(f"{name} → Present: {counts['Present']} | Absent: {counts['Absent']}")
    except FileNotFoundError:
        print(" No attendance file found!")


# ===================================================
# Function 4: Export Report to Excel (via pandas)
# ===================================================
def export_report():
    try:
        df = pd.read_csv("attendance.csv")
        df.to_excel("attendance_report.xlsx", index=False)
        print(" Attendance report exported successfully as 'attendance_report.xlsx'")
    except FileNotFoundError:
        print(" No attendance file found!")


# ===================================================
# Function 5: Reset Attendance Report (Clear file)
# ===================================================
def reset_attendance():
    with open("attendance.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Date", "Status"])
    print(" Attendance report has been reset!")
    # ===================================================
# Function 6: Mark attendace by voice
# ===================================================        
def take_voice_input(prompt_text):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print(prompt_text)
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        print(" You said:", text)
        return text
    except sr.UnknownValueError:
        print(" Sorry, I could not understand. Please try again.")
        return None
    except sr.RequestError:
        print(" Speech recognition service unavailable.")
        return None

def mark_attendance_voice():
    name = take_voice_input("Say the student's name:")
    if not name:
        return

    status = take_voice_input("Say Present or Absent:")
    if not status:
        return

    status = status.capitalize()
    from datetime import date
    import csv

    today = date.today().strftime("%Y-%m-%d")

    with open("attendance.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([name, today, status])

    print(f" Attendance marked for {name} as {status} on {today}.")

# ===================================================
# Function 7: delete Specific Student Record
# ===================================================    
def delete_student_record():
    name_to_delete = input("Enter the student's name to delete their record: ").strip().lower()

    if not os.path.exists("attendance.csv"):
        print(" No attendance records found.\n")
        return

    
    with open("attendance.csv", "r") as file:
        reader = csv.reader(file)
        rows = list(reader)

    new_rows = [row for row in rows if len(row) > 0 and row[0].strip().lower() != name_to_delete]

    with open("attendance.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(new_rows)

    print(f" All attendance records for '{name_to_delete.title()}' have been deleted from CSV.")

    
    try:
        df_excel = pd.read_excel("attendance_report.xlsx")
        df_excel = df_excel[df_excel['Name'].str.lower() != name_to_delete]
        df_excel.to_excel("attendance_report.xlsx", index=False)
        print(f" Record for '{name_to_delete.title()}' deleted from Excel as well.")
    except FileNotFoundError:
        print(" Excel report not found — only CSV updated.")
    
# ===================================================
# Function 8: Search Specific Student Record
# ===================================================
def search_student_record():
    name_to_search = input("Enter the student's name to search: ").strip().lower()
    
    
    if not os.path.exists("attendance.csv"):
        print(" No attendance file found!")
        return

    found_records = []

    try:
        with open("attendance.csv", mode="r") as file:
            reader = csv.reader(file)
            header = next(reader)  
            
            for row in reader:
                
                if len(row) >= 3 and row[0].strip().lower() == name_to_search:
                    found_records.append(row)
        
        print(f"\n Attendance History for {name_to_search.title()}:")
        
        if found_records:
            
            print("-" * 30)
            print(f"{header[1]:<10} {header[2]}") 
            print("-" * 30)
            for record in found_records:
                
                print(f"{record[1]:<10} {record[2]}")
            print("-" * 30)
        else:
            print(f" No attendance records found for '{name_to_search.title()}'.")
            
    except Exception as e:
        print(f" An error occurred while reading the file: {e}")

# ===================================================
# Main Menu System
# ===================================================
while True:
    print("\n===== Attendance Tracker =====")
    print("1. Mark Attendance")
    print("2. View Today’s Attendance")
    print("3. Generate Full Report")
    print("4. Export Report to Excel")
    print("5. Reset Attendance Report")
    print("6. Mark Attendance by Voice")
    print("7. Delete Specific Student Record")
    print("8. Search Specific Student Record")
    print("9. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        mark_attendance()
    elif choice == "2":
        view_attendance()
    elif choice == "3":
        generate_report()
    elif choice == "4":
        export_report()
    elif choice == "5":
        reset_attendance()
    elif choice == "6":
        mark_attendance_voice()
    elif choice == "7":
         delete_student_record()  
    elif choice == "8":
         search_student_record()       
    elif choice == "9":
        print(" Exiting... Bye!")
        break
    else:
        print(" Invalid choice, try again!")

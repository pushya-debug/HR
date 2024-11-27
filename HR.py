import streamlit as st
from datetime import date
import pandas as pd
import matplotlib.pyplot as plt
import logging
import os

# Initialize logging
logging.basicConfig(
    filename="hr_app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize Snowflake session using Streamlit connection
cnx = st.connection("snowflake")  # Replace 'snowflake' with your connection name in Streamlit
session = cnx.session()

# Constants
DATABASE_NAME = "HR_PERFORMANCE_DB"
SCHEMA_NAME = "HR_TRACKING_SCHEMA"

# Authentication (simplified for demo purposes)
USERS = {
    "admin_user": {"password": "admin123", "role": "admin"},
    "regular_user": {"password": "user123", "role": "user"}
}

# Authentication Form
st.sidebar.title("Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

# Use Streamlit session state to manage login state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None

if 'username' not in st.session_state:
    st.session_state['username'] = None

if st.sidebar.button("Login"):
    if username in USERS and USERS[username]["password"] == password:
        st.session_state['logged_in'] = True
        st.session_state['user_role'] = USERS[username]["role"]
        st.session_state['username'] = username
        st.sidebar.success(f"Welcome, {username}!")
    else:
        st.session_state['logged_in'] = False
        st.session_state['user_role'] = None
        st.session_state['username'] = None
        st.sidebar.error("Invalid username or password.")

# Logout option
if st.session_state['logged_in'] and st.sidebar.button("Logout"):
    st.session_state['logged_in'] = False
    st.session_state['user_role'] = None
    st.session_state['username'] = None
    st.sidebar.info("You have been logged out.")
    st.experimental_rerun()

# Check if the user is logged in
if not st.session_state['logged_in']:
    st.sidebar.info("Please log in to continue.")
    st.stop()

# Role-Based Access Control
USER_ROLES = {"admin": ["add", "edit", "delete", "view", "analytics"], "user": ["view", "analytics"]}

# App Title
st.title("HR Performance Tracking App")
st.sidebar.title("Navigation")

# Sidebar Navigation
sections = [
    "Employee Overview", "Education Records", "Family Details", 
    "Task Management", "Attendance", "Recognition", "Training", 
    "Real-Time Analytics"
]

# Admin-only access
if "add" in USER_ROLES[st.session_state['user_role']]:
    sections += [
        "Add Employee", "Add Task", "Add Attendance", "Add Recognition", "Add Training"
]

options = st.sidebar.radio("Select a section:", sections)

# Utility functions
def fetch_table_data(query):
    """Fetch data using a custom query."""
    try:
        logging.info(f"[{st.session_state['username']}] Executing query: {query}")
        return session.sql(query).to_pandas()
    except Exception as e:
        logging.error(f"[{st.session_state['username']}] Error executing query: {query}, Error: {e}")
        st.error(f"Error executing query: {e}")
        return None

def log_audit_action(action_type, description, details):
    """Log user actions into the audit trail."""
    try:
        query = f"""
            INSERT INTO {DATABASE_NAME}.{SCHEMA_NAME}.AUDIT_LOG 
            (USERNAME, ROLE, ACTION_TYPE, DESCRIPTION, DETAILS, TIMESTAMP)
            VALUES ('{st.session_state['username']}', '{st.session_state['user_role']}', '{action_type}', '{description}', '{details}', CURRENT_TIMESTAMP)
        """
        logging.info(f"[{st.session_state['username']}] Logging audit action: {query}")
        session.sql(query).collect()
    except Exception as e:
        logging.error(f"[{st.session_state['username']}] Failed to log audit action: {e}")

# Add Employee - Admin only
if options == "Add Employee" and st.session_state['user_role'] == "admin":
    st.header("Add New Employee")

    # Editable form fields for Employee details
    name = st.text_input("Employee Name")
    email = st.text_input("Employee Email")
    department = st.text_input("Department")
    designation = st.text_input("Designation")
    salary = st.number_input("Salary", min_value=0)
    joining_date = st.date_input("Joining Date")
    
    if st.button("Submit"):
        # Query to insert employee
        query = f"""
        INSERT INTO {DATABASE_NAME}.{SCHEMA_NAME}.EMPLOYEES (NAME, EMAIL, DEPARTMENT, DESIGNATION, SALARY, JOINING_DATE)
        VALUES ('{name}', '{email}', '{department}', '{designation}', {salary}, '{joining_date}')
        """
        session.sql(query).collect()
        log_audit_action("Add Employee", f"Added employee {name}", f"Name: {name}, Email: {email}")
        st.success(f"Employee {name} added successfully.")

# Add Education - Accessible by all users
if options == "Add Education":
    st.header("Add Education Record")
    employee_name = st.text_input("Employee Name")
    degree = st.text_input("Degree")
    institution = st.text_input("Institution")
    graduation_year = st.number_input("Graduation Year", min_value=1900, max_value=9999)
    
    if st.button("Submit"):
        # Query to insert education record
        query = f"""
        INSERT INTO {DATABASE_NAME}.{SCHEMA_NAME}.EDUCATION (EMPLOYEE_ID, DEGREE, INSTITUTION, GRADUATION_YEAR)
        SELECT EMPLOYEE_ID, '{degree}', '{institution}', {graduation_year} 
        FROM {DATABASE_NAME}.{SCHEMA_NAME}.EMPLOYEES WHERE NAME = '{employee_name}'
        """
        session.sql(query).collect()
        log_audit_action("Add Education", f"Added education record for {employee_name}", f"Degree: {degree}, Institution: {institution}")
        st.success(f"Education record for {employee_name} added successfully.")

# Task Management - Admin can add tasks, users can update status
if options == "Task Management":
    if st.session_state['user_role'] == "admin":
        st.header("Add New Task")
        task_description = st.text_area("Task Description")
        employee_name = st.text_input("Assigned To")
        deadline = st.date_input("Deadline")
        status = st.selectbox("Task Status", ["Not Started", "In Progress", "Completed"])
        priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        
        if st.button("Submit"):
            # Query to insert task
            query = f"""
            INSERT INTO {DATABASE_NAME}.{SCHEMA_NAME}.TASKS (EMPLOYEE_ID, TASK_DESCRIPTION, DEADLINE, STATUS, PRIORITY)
            SELECT EMPLOYEE_ID, '{task_description}', '{deadline}', '{status}', '{priority}'
            FROM {DATABASE_NAME}.{SCHEMA_NAME}.EMPLOYEES WHERE NAME = '{employee_name}'
            """
            session.sql(query).collect()
            log_audit_action("Add Task", f"Added task for {employee_name}", f"Task: {task_description}")
            st.success(f"Task for {employee_name} added successfully.")
    
    else:
        st.header("Update Task Status")
        task_id = st.number_input("Task ID")
        new_status = st.selectbox("Update Task Status", ["Not Started", "In Progress", "Completed"])
        
        if st.button("Update"):
            # Query to update task status
            query = f"""
            UPDATE {DATABASE_NAME}.{SCHEMA_NAME}.TASKS
            SET STATUS = '{new_status}'
            WHERE TASK_ID = {task_id}
            """
            session.sql(query).collect()
            log_audit_action("Update Task", f"Updated task {task_id}", f"New Status: {new_status}")
            st.success(f"Task {task_id} status updated successfully.")

# Time and Attendance - Users can manage their own timesheets
if options == "Attendance":
    st.header("Time & Attendance")
    employee_name = st.session_state['username']
    check_in = st.time_input("Check-in Time")
    check_out = st.time_input("Check-out Time")
    daily_report = st.text_area("Daily Report")

    if st.button("Submit Attendance"):
        # Insert timesheet data
        query = f"""
        INSERT INTO {DATABASE_NAME}.{SCHEMA_NAME}.ATTENDANCE (EMPLOYEE_NAME, CHECK_IN_TIME, CHECK_OUT_TIME, DAILY_REPORT)
        VALUES ('{employee_name}', '{check_in}', '{check_out}', '{daily_report}')
        """
        session.sql(query).collect()
        log_audit_action("Submit Attendance", f"Submitted attendance for {employee_name}", f"Check-in: {check_in}, Check-out: {check_out}")
        st.success(f"Attendance for {employee_name} submitted successfully.")

# Real-Time Analytics (Admin only)
if options == "Real-Time Analytics" and st.session_state['user_role'] == "admin":
    st.header("Real-Time Analytics Dashboard")
    # Attendance Trends
    attendance_data = fetch_table_data(f"SELECT * FROM {DATABASE_NAME}.{SCHEMA_NAME}.ATTENDANCE")
    if attendance_data is not None:
        st.write("Attendance Data", attendance_data)
        fig, ax = plt.subplots()
        ax.plot(attendance_data['CHECK_IN_TIME'], attendance_data['CHECK_OUT_TIME'])
        ax.set_xlabel('Check-in Time')
        ax.set_ylabel('Check-out Time')
        st.pyplot(fig)

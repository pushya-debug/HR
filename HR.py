import streamlit as st
from snowflake.snowpark.context import get_active_session
from datetime import date
import pandas as pd
import logging

# Initialize logging
logging.basicConfig(
    filename="hr_app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize Snowflake connection
session = get_active_session()

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
USER_ROLES = {"admin": ["add", "edit", "delete", "view", "analytics"], "user": ["view", "analytics", "edit"]}

# App Title
st.title("HR Performance Tracking App")
st.sidebar.title("Navigation")

# Sidebar Navigation
sections = [
    "Employee Overview", "Education Records", "Family Details", 
    "Task Management", "Attendance", "Real-Time Analytics"
]

# Admin-only access
if "add" in USER_ROLES[st.session_state['user_role']]:
    sections += [
        "Add Employee", "Add Task", "Add Attendance", "Add Recognition", "Add Salary"
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

# Admin - Add Employee
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
        query = f"""
        INSERT INTO {DATABASE_NAME}.{SCHEMA_NAME}.EMPLOYEES (NAME, EMAIL, DEPARTMENT, DESIGNATION, SALARY, JOINING_DATE)
        VALUES ('{name}', '{email}', '{department}', '{designation}', {salary}, '{joining_date}')
        """
        session.sql(query).collect()
        log_audit_action("Add Employee", f"Added employee {name}", f"Name: {name}, Email: {email}")
        st.success(f"Employee {name} added successfully.")

# Add Education - Accessible by all users
if options == "Education Records" and st.session_state['user_role'] == "user":
    st.header("Add Education Record")
    employee_name = st.text_input("Employee Name")
    degree = st.text_input("Degree")
    institution = st.text_input("Institution")
    graduation_year = st.number_input("Graduation Year", min_value=1900, max_value=9999)
    
    if st.button("Submit"):
        query = f"""
        INSERT INTO {DATABASE_NAME}.{SCHEMA_NAME}.EDUCATION (EMPLOYEE_ID, DEGREE, INSTITUTION, GRADUATION_YEAR)
        SELECT EMPLOYEE_ID, '{degree}', '{institution}', {graduation_year} 
        FROM {DATABASE_NAME}.{SCHEMA_NAME}.EMPLOYEES WHERE NAME = '{employee_name}'
        """
        session.sql(query).collect()
        log_audit_action("Add Education", f"Added education record for {employee_name}", f"Degree: {degree}, Institution: {institution}")
        st.success(f"Education record for {employee_name} added successfully.")

# Add Task - Admin only
if options == "Add Task" and st.session_state['user_role'] == "admin":
    st.header("Add New Task")
    task_description = st.text_area("Task Description")
    employee_name = st.text_input("Assigned To")
    deadline = st.date_input("Deadline")
    status = st.selectbox("Task Status", ["Not Started", "In Progress", "Completed"])
    priority = st.selectbox("Priority", ["Low", "Medium", "High"])
    
    if st.button("Submit"):
        query = f"""
        INSERT INTO {DATABASE_NAME}.{SCHEMA_NAME}.TASKS (EMPLOYEE_ID, TASK_DESCRIPTION, DEADLINE, STATUS, PRIORITY)
        SELECT EMPLOYEE_ID, '{task_description}', '{deadline}', '{status}', '{priority}'
        FROM {DATABASE_NAME}.{SCHEMA_NAME}.EMPLOYEES WHERE NAME = '{employee_name}'
        """
        session.sql(query).collect()
        log_audit_action("Add Task", f"Added task for {employee_name}", f"Task: {task_description}")
        st.success(f"Task for {employee_name} added successfully.")

# Add Attendance - Admin only
if options == "Add Attendance" and st.session_state['user_role'] == "admin":
    st.header("Add Attendance Record")
    employee_name = st.text_input("Employee Name")
    attendance_date = st.date_input("Date")
    status = st.selectbox("Attendance Status", ["Present", "Absent", "Leave"])
    
    if st.button("Submit"):
        query = f"""
        INSERT INTO {DATABASE_NAME}.{SCHEMA_NAME}.ATTENDANCE (EMPLOYEE_ID, ATTENDANCE_DATE, STATUS)
        SELECT EMPLOYEE_ID, '{attendance_date}', '{status}' 
        FROM {DATABASE_NAME}.{SCHEMA_NAME}.EMPLOYEES WHERE NAME = '{employee_name}'
        """
        session.sql(query).collect()
        log_audit_action("Add Attendance", f"Added attendance for {employee_name}", f"Date: {attendance_date}, Status: {status}")
        st.success(f"Attendance for {employee_name} on {attendance_date} added successfully.")

# Add Recognition - Admin only
if options == "Add Recognition" and st.session_state['user_role'] == "admin":
    st.header("Add Employee Recognition")
    employee_name = st.text_input("Employee Name")
    recognition_type = st.selectbox("Recognition Type", ["Employee of the Month", "Best Team Player", "Excellence in Service"])
    date_of_recognition = st.date_input("Date of Recognition")
    
    if st.button("Submit"):
        query = f"""
        INSERT INTO {DATABASE_NAME}.{SCHEMA_NAME}.RECOGNITIONS (EMPLOYEE_ID, RECOGNITION_TYPE, DATE_OF_RECOGNITION)
        SELECT EMPLOYEE_ID, '{recognition_type}', '{date_of_recognition}' 
        FROM {DATABASE_NAME}.{SCHEMA_NAME}.EMPLOYEES WHERE NAME = '{employee_name}'
        """
        session.sql(query).collect()
        log_audit_action("Add Recognition", f"Added recognition for {employee_name}", f"Type: {recognition_type}, Date: {date_of_recognition}")
        st.success(f"Recognition for {employee_name} added successfully.")

# Real-time Analytics - Available to all
if options == "Real-Time Analytics":
    st.header("Real-Time Analytics")
    # Task Completion Rates
    st.subheader("Task Completion Rates")
    task_completion_query = f"""
        SELECT STATUS, COUNT(*) AS COUNT
        FROM {DATABASE_NAME}.{SCHEMA_NAME}.TASKS
        GROUP BY STATUS
    """
    task_df = fetch_table_data(task_completion_query)
    if task_df is not None and not task_df.empty:
        st.bar_chart(task_df.set_index("STATUS"))
    else:
        st.write("No task data available.")

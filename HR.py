# File path: hr_performance_tracking_app.py

import streamlit as st
from snowflake.snowpark.context import get_active_session
from datetime import date
import pandas as pd
import matplotlib.pyplot as plt
import logging

# Initialize logging
logging.basicConfig(
    filename="hr_app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize Snowflake connection
cnx = st.connection("snowflake")
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

if st.sidebar.button("Login"):
    if username in USERS and USERS[username]["password"] == password:
        st.sidebar.success(f"Welcome, {username}!")
        st.session_state['logged_in'] = True
        st.session_state['user_role'] = USERS[username]["role"]
    else:
        st.sidebar.error("Invalid username or password.")
        st.session_state['logged_in'] = False
        st.session_state['user_role'] = None

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
if "add" in USER_ROLES[st.session_state['user_role']]:
    sections += [
        "Add Employee", "Add Education", "Add Family Details", 
        "Add Task", "Add Attendance", "Add Recognition", "Add Training"
]

options = st.sidebar.radio("Select a section:", sections)

# Utility functions
def fetch_table_data(query):
    """Fetch data using a custom query."""
    try:
        logging.info(f"[{username}] Executing query: {query}")
        return session.sql(query).to_pandas()
    except Exception as e:
        logging.error(f"[{username}] Error executing query: {query}, Error: {e}")
        st.error(f"Error executing query: {e}")
        return None

def log_audit_action(action_type, description, details):
    """Log user actions into the audit trail."""
    try:
        query = f"""
            INSERT INTO {DATABASE_NAME}.{SCHEMA_NAME}.AUDIT_LOG 
            (USERNAME, ROLE, ACTION_TYPE, DESCRIPTION, DETAILS, TIMESTAMP)
            VALUES ('{username}', '{st.session_state['user_role']}', '{action_type}', '{description}', '{details}', CURRENT_TIMESTAMP)
        """
        logging.info(f"[{username}] Logging audit action: {query}")
        session.sql(query).collect()
    except Exception as e:
        logging.error(f"[{username}] Failed to log audit action: {e}")

# Real-Time Analytics
if options == "Real-Time Analytics":
    st.header("Real-Time Analytics Dashboard")
    
    # Attendance Trends
    st.subheader("Monthly Attendance Trends")
    attendance_trend_query = f"""
        SELECT TO_CHAR(DATE, 'YYYY-MM') AS MONTH, COUNT(*) AS TOTAL_RECORDS,
               SUM(CASE WHEN STATUS = 'Present' THEN 1 ELSE 0 END) AS PRESENT_COUNT
        FROM {DATABASE_NAME}.{SCHEMA_NAME}.ATTENDANCE
        GROUP BY TO_CHAR(DATE, 'YYYY-MM')
        ORDER BY MONTH
    """
    attendance_df = fetch_table_data(attendance_trend_query)
    if attendance_df is not None and not attendance_df.empty:
        attendance_df['PRESENT_PERCENT'] = (attendance_df['PRESENT_COUNT'] / attendance_df['TOTAL_RECORDS']) * 100
        st.line_chart(attendance_df.set_index("MONTH")["PRESENT_PERCENT"])
    else:
        st.write("No attendance data available.")

    # Task Completion Rates
    st.subheader("Task Completion Rates")
    task_completion_query = f"""
        SELECT STATUS, COUNT(*) AS COUNT
        FROM {DATABASE_NAME}.{SCHEMA_NAME}.TASKS
        GROUP BY STATUS
    """
    task_df = fetch_table_data(task_completion_query)
    if task_df is not None and not task_df.empty:
        fig, ax = plt.subplots()
        ax.pie(task_df['COUNT'], labels=task_df['STATUS'], autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures the pie is drawn as a circle.
        st.pyplot(fig)
    else:
        st.write("No task data available.")

    # Department-Wise Employee Distribution
    st.subheader("Department-Wise Employee Distribution")
    department_query = f"""
        SELECT DEPARTMENT, COUNT(*) AS EMPLOYEE_COUNT
        FROM {DATABASE_NAME}.{SCHEMA_NAME}.EMPLOYEES
        GROUP BY DEPARTMENT
    """
    department_df = fetch_table_data(department_query)
    if department_df is not None and not department_df.empty:
        st.bar_chart(department_df.set_index("DEPARTMENT")["EMPLOYEE_COUNT"])
    else:
        st.write("No department data available.")

    # Log the action
    log_audit_action("View Analytics", "Viewed Real-Time Analytics Dashboard", "N/A")

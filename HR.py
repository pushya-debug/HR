import streamlit as st
from snowflake.snowpark import Session
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

# Load Snowflake connection details from Streamlit secrets
snowflake_conn_params = {
    "account": st.secrets["connections.snowflake"]["account"],
    "user": st.secrets["connections.snowflake"]["user"],
    "password": st.secrets["connections.snowflake"]["password"],
    "role": st.secrets["connections.snowflake"]["role"],
    "warehouse": st.secrets["connections.snowflake"]["warehouse"],
    "database": st.secrets["connections.snowflake"]["database"],
    "schema": st.secrets["connections.snowflake"]["schema"],
    "client_session_keep_alive": st.secrets["connections.snowflake"]["client_session_keep_alive"]
}

# Initialize Snowflake session
try:
    session = Session.builder.configs(snowflake_conn_params).create()
    logging.info("Successfully connected to Snowflake.")
except Exception as e:
    logging.error(f"Error while connecting to Snowflake: {e}")
    st.error(f"Error while connecting to Snowflake: {e}")
    st.stop()

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

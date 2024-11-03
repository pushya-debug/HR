# Import necessary packages
import streamlit as st
from snowflake.snowpark.context import get_active_session

# Connection to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# App Title
st.title("HR Performance Tracking App :balloon:")

# Sidebar Navigation
st.sidebar.title("Navigation")
options = st.sidebar.radio("Select a section:", [
    "Employee Overview", "Add Employee", "Education Records", "Add Education", 
    "Family Details", "Add Family Details", "Task Management", "Add Task", 
    "Attendance", "Add Attendance", "Recognition", "Add Recognition", 
    "Training", "Add Training", "User Management"
])

# Define the database and schema
DATABASE_NAME = "HR_PERFORMANCE_DB"
SCHEMA_NAME = "HR_TRACKING_SCHEMA"

# Fetch employees for dropdowns in other sections
employees_df = session.sql(f"SELECT * FROM {DATABASE_NAME}.{SCHEMA_NAME}.EMPLOYEES").to_pandas()

# Fetch employment types once
employment_types = session.sql(f"SELECT DISTINCT EMPLOYMENT_TYPE FROM {DATABASE_NAME}.{SCHEMA_NAME}.EMPLOYMENT_TYPE_LOOKUP").to_pandas()['EMPLOYMENT_TYPE'].tolist()

# Employee Overview Section
if options == "Employee Overview":
    st.header("Employee Overview")
    if employees_df.empty:
        st.write("No employee data available.")
    else:
        st.dataframe(employees_df)

# Add Employee Section
elif options == "Add Employee":
    st.header("Add New Employee")
    with st.form(key='add_employee'):
        name = st.text_input("Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        address = st.text_input("Address")
        department = st.text_input("Department")
        designation = st.text_input("Designation")
        manager_id = st.number_input("Manager ID", min_value=1, step=1, format="%d")
        salary = st.number_input("Salary", format="%f", step=0.01)
        joining_date = st.date_input("Joining Date")
        employment_type = st.selectbox("Employment Type", employment_types)  # Use the fetched employment types

        submit_button = st.form_submit_button(label='Add Employee')
        if submit_button:
            session.sql(f"""
                INSERT INTO {DATABASE_NAME}.{SCHEMA_NAME}.EMPLOYEES (NAME, EMAIL, PHONE, ADDRESS, DEPARTMENT, DESIGNATION, MANAGER_ID, SALARY, JOINING_DATE, EMPLOYMENT_TYPE)
                VALUES ('{name}', '{email}', '{phone}', '{address}', '{department}', '{designation}', {manager_id}, {salary}, '{joining_date}', '{employment_type}')
            """).collect()
            st.success("Employee added successfully!")

# Training Records Section
elif options == "Training":
    st.header("Training Records")
    training_df = session.sql(f"SELECT * FROM {DATABASE_NAME}.{SCHEMA_NAME}.TRAINING").to_pandas()
    
    if training_df.empty:
        st.write("No training records available.")
    else:
        st.dataframe(training_df)

# Add Training Section
elif options == "Add Training":
    st.header("Add Training Record")
    employee_id = st.selectbox("Select Employee ID for Training:", employees_df['EMPLOYEE_ID'].tolist())
    
    with st.form(key='add_training'):
        training_title = st.text_input("Training Title")
        provider = st.text_input("Provider")
        training_date = st.date_input("Training Date")
        duration = st.number_input("Duration (hours)", min_value=1, step=1)
        cost = st.number_input("Cost", min_value=0.0, step=0.01, format="%f")

        submit_button = st.form_submit_button(label='Add Training')
        if submit_button:
            session.sql(f"""
                INSERT INTO {DATABASE_NAME}.{SCHEMA_NAME}.TRAINING (EMPLOYEE_ID, TRAINING_TITLE, PROVIDER, TRAINING_DATE, DURATION, COST)
                VALUES ({employee_id}, '{training_title}', '{provider}', '{training_date}', {duration}, {cost})
            """).collect()
            st.success("Training record added successfully!")

# User Management Section
elif options == "User Management":
    st.header("User Management")
    
    # Fetch user data from database
    users_df = session.sql(f"SELECT * FROM {DATABASE_NAME}.{SCHEMA_NAME}.USERS").to_pandas()
    
    if users_df.empty:
        st.write("No users found.")
    else:
        st.dataframe(users_df)
    
    st.subheader("Add New User")
    with st.form(key='add_user'):
        username = st.text_input("Username")
        role = st.selectbox("Role", ["Admin", "Manager", "Employee"])
        email = st.text_input("Email")
        active_status = st.selectbox("Active Status", ["Active", "Inactive"])

        submit_button = st.form_submit_button(label='Add User')
        if submit_button:
            session.sql(f"""
                INSERT INTO {DATABASE_NAME}.{SCHEMA_NAME}.USERS (USERNAME, ROLE, EMAIL, ACTIVE_STATUS)
                VALUES ('{username}', '{role}', '{email}', '{active_status}')
            """).collect()
            st.success("User added successfully!")

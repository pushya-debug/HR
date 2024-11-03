# Import necessary packages
import streamlit as st
from snowflake.snowpark.functions import col
import pandas as pd

# Initialize the Streamlit app
st.title("HR Performance Tracking App :balloon:")
st.write("Manage your HR data efficiently!")

# Connection to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Fetching employee data
employees_df = session.table("HR_PERFORMANCE_DB.HR_TRACKING_SCHEMA.EMPLOYEES").select(col('EMPLOYEE_ID'), col('NAME')).to_pandas()

# Add Employee Section
st.header("Add New Employee")
name_on_order = st.text_input('Employee Name:')
st.write('The name of the new employee will be: ', name_on_order)

# Select employee from the list for operations
selected_employee = st.selectbox("Select Employee for Details", employees_df['NAME'])

# Displaying selected employee's details
if selected_employee:
    employee_details = employees_df[employees_df['NAME'] == selected_employee]
    st.write("Details for selected employee:", employee_details)

# Multi-select for job roles (or any other data retrieval, e.g. departments)
roles_df = session.table("HR_PERFORMANCE_DB.HR_TRACKING_SCHEMA.JOB_ROLES").select(col('ROLE_NAME')).to_pandas()
roles_list = st.multiselect(
    "Choose Roles for the Employee",
    roles_df['ROLE_NAME'].tolist(),
    max_selections=3
)

# Concatenating selected roles into a string
if roles_list:
    roles_string = ', '.join(roles_list)
    st.write("Selected roles for the employee:", roles_string)

    # Prepare to insert employee into the database
    if st.button("Submit New Employee"):
        insert_stmt = f"""
            INSERT INTO HR_PERFORMANCE_DB.HR_TRACKING_SCHEMA.EMPLOYEES (NAME, JOB_ROLES)
            VALUES ('{name_on_order}', '{roles_string}')
        """
        session.sql(insert_stmt).collect()
        st.success(f'Employee "{name_on_order}" added successfully!', icon="✅")

# Import necessary packages
import streamlit as st
from snowflake.snowpark.context import get_active_session

# Initialize the Snowflake session
cnx = st.connection("snowflake")
session = cnx.session()

# App Title
st.title("HR Performance Tracking App ")

# Sidebar Navigation
st.sidebar.title("Navigation")
options = st.sidebar.radio("Select a section:", [
    "Employee Overview", "Add Employee", "Education Records", "Add Education", 
    "Family Details", "Add Family Details", "Task Management", "Add Task", 
    "Attendance", "Add Attendance", "Recognition", "Add Recognition", 
    "Training", "Add Training"
])

# Define the database and schema
DATABASE_NAME = "HR_PERFORMANCE_DB"
SCHEMA_NAME = "HR_TRACKING_SCHEMA"

# Fetch employees for dropdowns in other sections
employees_df = session.sql(f"SELECT * FROM {DATABASE_NAME}.{SCHEMA_NAME}.EMPLOYEES").to_pandas()

# Employee Overview Section
if options == "Employee Overview":
    st.header("Employee Overview")
    employees_df = session.sql(f"SELECT * FROM {DATABASE_NAME}.{SCHEMA_NAME}.EMPLOYEES").to_pandas()
    
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
        employment_type = st.selectbox("Employment Type", session.sql(f"SELECT EMPLOYMENT_TYPE FROM {DATABASE_NAME}.{SCHEMA_NAME}.EMPLOYMENT_TYPE_LOOKUP").to_pandas()['EMPLOYMENT_TYPE'].tolist())

        submit_button = st.form_submit_button(label='Add Employee')
        if submit_button:
            session.sql(f"""
                INSERT INTO {DATABASE_NAME}.{SCHEMA_NAME}.EMPLOYEES (NAME, EMAIL, PHONE, ADDRESS, DEPARTMENT, DESIGNATION, MANAGER_ID, SALARY, JOINING_DATE, EMPLOYMENT_TYPE)
                VALUES ('{name}', '{email}', '{phone}', '{address}', '{department}', '{designation}', {manager_id}, {salary}, '{joining_date}', '{employment_type}')
            """).collect()
            st.success("Employee added successfully!")

# Education Records Section
elif options == "Education Records":
    st.header("Education Records")
    employee_id = st.selectbox("Select Employee ID:", employees_df['EMPLOYEE_ID'].tolist())
    
    # Fetch education records for the selected employee
    education_df = session.sql(f"SELECT * FROM {DATABASE_NAME}.{SCHEMA_NAME}.EDUCATION WHERE EMPLOYEE_ID = {employee_id}").to_pandas()
    
    if education_df.empty:
        st.write("No education records available for this employee.")
    else:
        st.dataframe(education_df)

# Add Education Section
elif options == "Add Education":
    st.header("Add Education Record")
    employee_id = st.selectbox("Select Employee ID for Education:", employees_df['EMPLOYEE_ID'].tolist())
    
    with st.form(key='add_education'):
        degree = st.text_input("Degree")
        institution = st.text_input("Institution")
        graduation_year = st.number_input("Graduation Year", min_value=1900, max_value=2100, step=1)
        certifications = st.text_area("Certifications")

        submit_button = st.form_submit_button(label='Add Education')
        if submit_button:
            session.sql(f"""
                INSERT INTO {DATABASE_NAME}.{SCHEMA_NAME}.EDUCATION (EMPLOYEE_ID, DEGREE, INSTITUTION, GRADUATION_YEAR, CERTIFICATIONS)
                VALUES ({employee_id}, '{degree}', '{institution}', {graduation_year}, '{certifications}')
            """).collect()
            st.success("Education record added successfully!")

# Family Details Section
elif options == "Family Details":
    st.header("Family Details")
    employee_id = st.selectbox("Select Employee ID for Family Details:", employees_df['EMPLOYEE_ID'].tolist())
    
    # Fetch family details for the selected employee
    family_details_df = session.sql(f"SELECT * FROM {DATABASE_NAME}.{SCHEMA_NAME}.FAMILY_DETAILS WHERE EMPLOYEE_ID = {employee_id}").to_pandas()
    
    if family_details_df.empty:
        st.write("No family details available for this employee.")
    else:
        st.dataframe(family_details_df)

# Add Family Details Section
elif options == "Add Family Details":
    st.header("Add Family Member")
    employee_id = st.selectbox("Select Employee ID for Family Member:", employees_df['EMPLOYEE_ID'].tolist())
    
    with st.form(key='add_family'):
        family_member_name = st.text_input("Family Member Name")
        relationship = st.text_input("Relationship")
        contact_info = st.text_input("Contact Info")
        emergency_contact = st.checkbox("Emergency Contact")

        submit_button = st.form_submit_button(label='Add Family Member')
        if submit_button:
            session.sql(f"""
                INSERT INTO {DATABASE_NAME}.{SCHEMA_NAME}.FAMILY_DETAILS (EMPLOYEE_ID, FAMILY_MEMBER_NAME, RELATIONSHIP, CONTACT_INFO, EMERGENCY_CONTACT)
                VALUES ({employee_id}, '{family_member_name}', '{relationship}', '{contact_info}', {emergency_contact})
            """).collect()
            st.success("Family member added successfully!")

# Task Management Section
elif options == "Task Management":
    st.header("Task Management")
    employee_id = st.selectbox("Select Employee ID for Task Management:", employees_df['EMPLOYEE_ID'].tolist())
    
    # Fetch tasks for the selected employee
    tasks_df = session.sql(f"SELECT * FROM {DATABASE_NAME}.{SCHEMA_NAME}.TASKS WHERE EMPLOYEE_ID = {employee_id}").to_pandas()
    
    if tasks_df.empty:
        st.write("No tasks assigned to this employee.")
    else:
        st.dataframe(tasks_df)

# Add Task Section
elif options == "Add Task":
    st.header("Add Task")
    employee_id = st.selectbox("Select Employee ID for Task:", employees_df['EMPLOYEE_ID'].tolist())
    
    with st.form(key='add_task'):
        task_description = st.text_area("Task Description")
        deadline = st.date_input("Deadline")
        task_status = st.selectbox("Select Task Status", session.sql(f"SELECT STATUS FROM {DATABASE_NAME}.{SCHEMA_NAME}.TASK_STATUS_LOOKUP").to_pandas()['STATUS'].tolist())
        task_priority = st.selectbox("Select Task Priority", session.sql(f"SELECT PRIORITY FROM {DATABASE_NAME}.{SCHEMA_NAME}.PRIORITY_LOOKUP").to_pandas()['PRIORITY'].tolist())

        submit_button = st.form_submit_button(label='Add Task')
        if submit_button:
            session.sql(f"""
                INSERT INTO {DATABASE_NAME}.{SCHEMA_NAME}.TASKS (EMPLOYEE_ID, TASK_DESCRIPTION, ASSIGNED_DATE, DEADLINE, STATUS, PRIORITY)
                VALUES ({employee_id}, '{task_description}', CURRENT_DATE, '{deadline}', '{task_status}', '{task_priority}')
            """).collect()
            st.success("Task added successfully!")

# Attendance Section
elif options == "Attendance":
    st.header("Attendance Records")
    attendance_df = session.sql(f"SELECT * FROM {DATABASE_NAME}.{SCHEMA_NAME}.ATTENDANCE").to_pandas()
    
    if attendance_df.empty:
        st.write("No attendance records available.")
    else:
        st.dataframe(attendance_df)

# Add Attendance Section
elif options == "Add Attendance":
    st.header("Add Attendance Record")
    employee_id = st.selectbox("Select Employee ID for Attendance:", employees_df['EMPLOYEE_ID'].tolist())
    
    with st.form(key='add_attendance'):
        date = st.date_input("Date")
        check_in = st.time_input("Check In")
        check_out = st.time_input("Check Out")
        status = st.selectbox("Select Attendance Status", session.sql(f"SELECT STATUS FROM {DATABASE_NAME}.{SCHEMA_NAME}.ATTENDANCE_STATUS_LOOKUP").to_pandas()['STATUS'].tolist())

        submit_button = st.form_submit_button(label='Add Attendance')
        if submit_button:
            session.sql(f"""
                INSERT INTO {DATABASE_NAME}.{SCHEMA_NAME}.ATTENDANCE (EMPLOYEE_ID, DATE, CHECK_IN, CHECK_OUT, STATUS)
                VALUES ({employee_id}, '{date}', '{check_in}', '{check_out}', '{status}')
            """).collect()
            st.success("Attendance record added successfully!")

# Recognition Section
elif options == "Recognition":
    st.header("Employee Recognition")
    recognition_df = session.sql(f"SELECT * FROM {DATABASE_NAME}.{SCHEMA_NAME}.RECOGNITION").to_pandas()
    
    if recognition_df.empty:
        st.write("No recognition records available.")
    else:
        st.dataframe(recognition_df)

# Add Recognition Section
elif options == "Add Recognition":
    st.header("Add Recognition")
    employee_id = st.selectbox("Select Employee ID for Recognition:", employees_df['EMPLOYEE_ID'].tolist())
    
    with st.form(key='add_recognition'):
        description = st.text_area("Description")
        award_name = st.text_input("Award Name")

        submit_button = st.form_submit_button(label='Add Recognition')
        if submit_button:
            session.sql(f"""
                INSERT INTO {DATABASE_NAME}.{SCHEMA_NAME}.RECOGNITION (EMPLOYEE_ID, DESCRIPTION, AWARD_NAME, DATE)
                VALUES ({employee_id}, '{description}', '{award_name}', CURRENT_DATE)
            """).collect()
            st.success("Recognition added successfully!")

# Training Section
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
        training_name = st.text_input("Training Name")
        description = st.text_area("Description")
        completion_date = st.date_input("Completion Date")

        submit_button = st.form_submit_button(label='Add Training')
        if submit_button:
            session.sql(f"""
                INSERT INTO {DATABASE_NAME}.{SCHEMA_NAME}.TRAINING (EMPLOYEE_ID, TRAINING_NAME, DESCRIPTION, COMPLETION_DATE)
                VALUES ({employee_id}, '{training_name}', '{description}', '{completion_date}')
            """).collect()
            st.success("Training record added successfully!")

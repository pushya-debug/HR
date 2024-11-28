import streamlit as st
from streamlit_login_auth_ui.widgets import __login__
import pandas as pd
import matplotlib.pyplot as plt

# Custom login UI from streamlit-login-auth-ui
__login__obj = __login__(auth_token="courier_auth_token", 
                        company_name="Shims",
                        width=200, height=250, 
                        logout_button_name='Logout', hide_menu_bool=False, 
                        hide_footer_bool=False, 
                        lottie_url='https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json')

LOGGED_IN = __login__obj.build_login_ui()

if LOGGED_IN:
    # Your main app starts here after login
    st.title("HR Performance Tracking App")
    
    # Navigation Sidebar
    st.sidebar.title("Navigation")
    sections = ["Employee Overview", "Education Records", "Family Details", "Task Management", 
                "Attendance", "Recognition", "Training", "Real-Time Analytics"]
    
    # Role-based options
    if st.session_state['user_role'] == "admin":
        sections += ["Add Employee", "Add Task", "Add Attendance", "Add Recognition", "Add Training"]
    
    # Sidebar navigation menu
    selected_section = st.sidebar.radio("Select a section:", sections)

    # Fetch data function (placeholder for real implementation)
    def fetch_data(query):
        # Example query function to get data from Snowflake, replace with your actual query logic.
        # Returning a sample dataframe
        return pd.DataFrame({
            'Employee': ['John Doe', 'Jane Smith'],
            'Check-in': ['08:00 AM', '09:00 AM'],
            'Check-out': ['05:00 PM', '06:00 PM'],
            'Status': ['Completed', 'In Progress']
        })
    
    # Admin Section - Add Employee
    if selected_section == "Add Employee" and st.session_state['user_role'] == "admin":
        st.header("Add New Employee")
        name = st.text_input("Employee Name")
        email = st.text_input("Employee Email")
        department = st.text_input("Department")
        designation = st.text_input("Designation")
        salary = st.number_input("Salary", min_value=0)
        joining_date = st.date_input("Joining Date")
        if st.button("Submit"):
            # Insert employee record (your actual query will go here)
            st.success(f"Employee {name} added successfully.")

    # User Section - Add Education
    elif selected_section == "Education Records":
        st.header("Add Education Record")
        employee_name = st.text_input("Employee Name")
        degree = st.text_input("Degree")
        institution = st.text_input("Institution")
        graduation_year = st.number_input("Graduation Year", min_value=1900, max_value=9999)
        if st.button("Submit"):
            # Insert education record (your actual query will go here)
            st.success(f"Education record for {employee_name} added successfully.")
    
    # Task Management - Admin Add Task
    elif selected_section == "Task Management":
        if st.session_state['user_role'] == "admin":
            st.header("Add New Task")
            task_description = st.text_area("Task Description")
            employee_name = st.text_input("Assigned To")
            deadline = st.date_input("Deadline")
            status = st.selectbox("Task Status", ["Not Started", "In Progress", "Completed"])
            priority = st.selectbox("Priority", ["Low", "Medium", "High"])
            if st.button("Submit"):
                st.success(f"Task for {employee_name} added successfully.")
        else:
            st.header("Update Task Status")
            task_id = st.number_input("Task ID")
            new_status = st.selectbox("Update Task Status", ["Not Started", "In Progress", "Completed"])
            if st.button("Update"):
                st.success(f"Task {task_id} status updated to {new_status}.")

    # Attendance - For All Users (Users can log their own attendance)
    elif selected_section == "Attendance":
        st.header("Time & Attendance")
        employee_name = st.session_state['username']
        check_in = st.time_input("Check-in Time")
        check_out = st.time_input("Check-out Time")
        daily_report = st.text_area("Daily Report")
        if st.button("Submit Attendance"):
            # Submit timesheet (your actual query will go here)
            st.success(f"Attendance for {employee_name} submitted successfully.")

    # Real-Time Analytics (Admin Only)
    elif selected_section == "Real-Time Analytics" and st.session_state['user_role'] == "admin":
        st.header("Real-Time Analytics Dashboard")
        # Example plot for performance analytics
        performance_data = fetch_data("SELECT * FROM PERFORMANCE_TABLE")
        if performance_data is not None:
            st.write("Performance Data", performance_data)
            fig, ax = plt.subplots()
            ax.plot(performance_data['Check-in'], performance_data['Check-out'])
            ax.set_xlabel('Check-in Time')
            ax.set_ylabel('Check-out Time')
            st.pyplot(fig)

    # Other sections - Recognition, Training, etc.
    elif selected_section == "Recognition" or selected_section == "Training":
        st.header(f"Add {selected_section}")
        title = st.text_input(f"Enter {selected_section} Title")
        description = st.text_area(f"Enter {selected_section} Details")
        if st.button(f"Submit {selected_section}"):
            st.success(f"{selected_section} added successfully.")

    # Footer/Log out
    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False
        st.session_state['user_role'] = None
        st.session_state['username'] = None
        st.sidebar.info("You have been logged out.")
        st.experimental_rerun()

else:
    st.info("Please log in to continue.")

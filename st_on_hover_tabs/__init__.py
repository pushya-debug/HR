import os
import streamlit as st
import streamlit.components.v1 as components

_RELEASE = True

# Define the build directory for the frontend
if _RELEASE:
    # Path to the build directory in your GitHub repository (assumed to be part of the repo)
    build_dir = "frontend/build"  # This should be relative to the root of your repo

    # Check if the build directory exists (good practice to avoid issues in case of misconfiguration)
    if not os.path.exists(build_dir):
        st.error(f"Build directory not found: {build_dir}")
        st.stop()

    _on_hover_tabs = components.declare_component(
        "on_hover_tabs",
        path=build_dir  # This path points to the `frontend/build` directory in the repo
    )
else:
    _on_hover_tabs = components.declare_component(
        "on_hover_tabs",
        url="http://localhost:3001"  # URL for local development server
    )

# Function to create on-hover tabs
def on_hover_tabs(tabName, iconName, styles=None, default_choice=1, key=None):
    component_value = _on_hover_tabs(
        tabName=tabName,
        iconName=iconName,
        styles=styles,
        key=key,
        default=tabName[default_choice]
    )
    return component_value

# Load custom CSS if in development mode
if not _RELEASE:
    st.subheader("Component that creates tabs corresponding with on-hover sidebar")
    st.markdown('<style>' + open('./style.css').read() + '</style>', unsafe_allow_html=True)  # Load the on-hover sidebar CSS

    # Sidebar tabs with on-hover functionality
    with st.sidebar:
        tabs = on_hover_tabs(
            tabName=['Employee Overview', 'Education Records', 'Family Details', 'Task Management', 
                     'Attendance', 'Recognition', 'Training', 'Real-Time Analytics'],
            iconName=['user', 'school', 'family', 'tasks', 'calendar', 'star', 'star', 'chart-line'], 
            key="1"
        )  # Create tabs for on-hover navigation bar

    # Handle each tab selection and render corresponding content
    if tabs == 'Employee Overview':
        st.title("Employee Overview")
        st.write(f'Name of option is {tabs}')
    
    elif tabs == 'Education Records':
        st.title("Education Records")
        st.write(f'Name of option is {tabs}')
    
    elif tabs == 'Family Details':
        st.title("Family Details")
        st.write(f'Name of option is {tabs}')
    
    elif tabs == 'Task Management':
        st.title("Task Management")
        st.write(f'Name of option is {tabs}')
    
    elif tabs == 'Attendance':
        st.title("Attendance")
        st.write(f'Name of option is {tabs}')
    
    elif tabs == 'Recognition':
        st.title("Recognition")
        st.write(f'Name of option is {tabs}')
    
    elif tabs == 'Training':
        st.title("Training")
        st.write(f'Name of option is {tabs}')
    
    elif tabs == 'Real-Time Analytics':
        st.title("Real-Time Analytics")
        st.write(f'Name of option is {tabs}')

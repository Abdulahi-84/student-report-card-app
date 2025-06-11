import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta, date
from PIL import Image
from fpdf import FPDF
import numpy as np

# --- Configuration and Data Paths ---
DATA_DIR = "student_data"
STUDENTS_FILE = os.path.join(DATA_DIR, "students.json")
RESULTS_FILE = os.path.join(DATA_DIR, "results.json")
STUDENT_PROFILES_FILE = os.path.join(DATA_DIR, "student_profiles.json") # New file for profiles

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# --- GLOBAL SETTINGS ---
TEACHER_USERNAME = "Abdul"
TEACHER_PASSWORD_HASH = "e10adc39499ba59abbe56e057f20f883e" # MD5 hash of "123456"

# Pre-defined student list with IDs and passwords (for initial app run)
INITIAL_STUDENTS = [
    {"id": 1, "username": "Adams", "password": "123456"},
    {"id": 2, "username": "Bala", "password": "123456"},
    {"id": 3, "username": "Ngozi", "password": "123456"},
]

# Pre-defined options for Session and Term dropdowns
SESSIONS = [f"{year}/{year+1}" for year in range(2023, datetime.now().year + 2)] # Generate current and future sessions
TERMS = ["First Term", "Second Term", "Third Term"]


# --- Helper Functions for Data Persistence ---
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.strftime('%Y-%m-%d')
        if isinstance(obj, pd.Timestamp):
            return obj.strftime('%Y-%m-%d')
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def load_data(file_path, initial_data=None):
    """Loads data from a JSON file. Returns initial_data if file doesn't exist or is empty."""
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        if initial_data is not None:
            if file_path == STUDENTS_FILE:
                st.info("Initializing student accounts.")
            return list(initial_data)
        return []
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            # Special handling for students_data to ensure initial students are always present
            if file_path == STUDENTS_FILE and initial_data is not None:
                existing_usernames = {s['username'] for s in data}
                for student in initial_data:
                    if student['username'] not in existing_usernames:
                        data.append(student)
                        st.info(f"Adding initial student '{student['username']}' to existing accounts.")
                data.sort(key=lambda x: x.get('id', 0))
            return data
    except json.JSONDecodeError as e:
        st.error(f"Error decoding JSON from {file_path}: {e}. The file might be corrupted. Attempting to reset.")
        if initial_data is not None:
            return list(initial_data)
        return []
    except Exception as e:
        st.error(f"An unexpected error occurred while loading {file_path}: {e}")
        if initial_data is not None:
            return list(initial_data)
        return []


def save_data(data, file_path):
    """Saves data to a JSON file using the custom encoder."""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4, cls=CustomJSONEncoder)
    except Exception as e:
        st.error(f"Error saving data to {file_path}: {e}")


# --- Session State Initialization ---
def initialize_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.username = None

    st.session_state.students_data = load_data(STUDENTS_FILE, INITIAL_STUDENTS)
    if 'results_data' not in st.session_state:
        st.session_state.results_data = load_data(RESULTS_FILE)
    if 'student_profiles_data' not in st.session_state:
        st.session_state.student_profiles_data = load_data(STUDENT_PROFILES_FILE)


# --- Authentication ---
def authenticate_user(username, password):
    if username == TEACHER_USERNAME and password == "123456":
        st.session_state.logged_in = True
        st.session_state.user_role = 'teacher'
        st.session_state.username = username
        st.success("Teacher login successful!")
        st.rerun()
    else:
        found_student = next((s for s in st.session_state.students_data if s['username'] == username and s['password'] == password), None)
        if found_student:
            st.session_state.logged_in = True
            st.session_state.user_role = 'student'
            st.session_state.username = username
            st.session_state.student_id = found_student.get('id')
            st.success(f"Welcome, {username}!")
            st.rerun()
        else:
            st.error("Invalid Username or Password.")

def logout():
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.username = None
    st.session_state.student_id = None
    st.info("Logged out successfully.")
    st.rerun()

# --- Custom CSS Styling ---
def apply_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Roboto', sans-serif;
        color: #333333;
    }

    .block-container {
        padding-top: 2.5rem;
        padding-right: 3rem;
        padding-left: 3rem;
        padding-bottom: 2.5rem;
        background-color: #FFFFFF;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }

    h1 {
        color: #0E3B6F;
        font-weight: 700;
        font-size: 2.8em;
        margin-bottom: 0.6em;
        padding-bottom: 0.2em;
        border-bottom: 2px solid #E0E0E0;
    }

    h2 {
        color: #1A518B;
        font-weight: 600;
        font-size: 2em;
        margin-top: 1.5em;
        margin-bottom: 1em;
    }

    h3 {
        color: #2E6FA8;
        font-weight: 500;
        font-size: 1.5em;
        margin-top: 1em;
        margin-bottom: 0.8em;
    }

    /* Sidebar styling */
    .st-emotion-cache-vk3305, /* Sidebar background */
    .st-emotion-cache-10q7q2w { /* Another possible sidebar target */
        background-color: #1D4E5F; /* Dark blue/teal for sidebar */
        color: #F8F8F8; /* Light off-white for sidebar text */
        border-radius: 10px;
        box-shadow: 2px 0 10px rgba(0,0,0,0.1);
    }
    .st-emotion-cache-10q7q2w .st-emotion-cache-nahz7x,
    .st-emotion-cache-10q7q2w h2,
    .st-emotion-cache-10q7q2w h3,
    .st-emotion-cache-10q7q2w .st-emotion-cache-14d8g5s,
    .st-emotion-cache-10q7q2w .st-emotion-cache-1t2y8b6 {
        color: #F8F8F8 !important;
    }

    /* Button styling */
    .st-emotion-cache-x78le4 button,
    .st-emotion-cache-nahz7x button {
        background-color: #2E6FA8;
        color: white;
        border-radius: 0.5rem;
        padding: 0.7rem 1.4rem;
        font-size: 1.05rem;
        font-weight: 500;
        border: none;
        transition: background-color 0.3s, transform 0.2s, box-shadow 0.2s;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }
    .st-emotion-cache-x78le4 button:hover,
    .st-emotion-cache-nahz7x button:hover {
        background-color: #1A518B;
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    }
    /* Specific sidebar button styling */
    .st-emotion-cache-10q7q2w .st-emotion-cache-x78le4 button,
    .st-emotion-cache-10q7q2w .st-emotion-cache-nahz7x button {
        background-color: #2E6FA8;
        color: white;
    }
    .st-emotion-cache-10q7q2w .st-emotion-cache-x78le4 button:hover,
    .st-emotion-cache-10q7q2w .st-emotion-cache-nahz7x button:hover {
        background-color: #1A518B;
    }

    /* Selectbox styling */
    .st-emotion-cache-1c7y2kd, .st-emotion-cache-o378hi { /* Selectbox and Multiselect containers */
        border: 1px solid #CCCCCC;
        border-radius: 0.4rem;
        background-color: #F8F8F8; /* Light background for inputs */
        color: #333333;
    }
    .st-emotion-cache-1c7y2kd > div > label, /* Label for selectbox */
    .st-emotion-cache-o3378hi > div > label {
        color: #333333;
    }
    .st-emotion-cache-1c7y2kd .st-emotion-cache-nahz7x { /* Selectbox text */
        color: #333333;
    }
    .st-emotion-cache-jtmznh { /* Dropdown menu */
        background-color: #FFFFFF;
        border: 1px solid #CCCCCC;
        border-radius: 0.4rem;
    }
    .st-emotion-cache-jtmznh li { /* Individual options */
        color: #333333;
    }
    .st-emotion-cache-jtmznh li:hover {
        background-color: #E0F2F7;
    }
    .st-emotion-cache-nahz7x .st-emotion-cache-1c11n07 { /* Multiselect selected tags */
        background-color: #E0F2F7;
        color: #1A518B;
        border-radius: 0.3rem;
        padding: 0.2em 0.5em;
        margin: 0.2em;
    }
    .st-emotion-cache-o378hi .st-emotion-cache-nahz7x { /* Multiselect placeholder text */
        color: #666666;
    }

    /* Input fields, text areas */
    .st-emotion-cache-1ftv5x input,
    .st-emotion-cache-1ftv5x textarea {
        background-color: #F8F8F8 !important; /* Ensure input background is light */
        color: #333333 !important;
        border: 1px solid #CCCCCC;
        border-radius: 0.4rem;
        padding: 0.5rem;
    }
    .st-emotion-cache-1ftv5x div[contenteditable="true"] { /* Text area content */
        background-color: #F8F8F8 !important;
        color: #333333 !important;
    }


    /* Info and Warning boxes */
    .st-emotion-cache-1fzhx90 { /* Info box */
        background-color: #e0f2f7; /* Light blue */
        border-left: 5px solid #00aaff;
        padding: 1em;
        border-radius: 0.3em;
        color: #004d66;
    }
    .st-emotion-cache-1629p8f { /* Warning box */
        background-color: #fff3cd; /* Light yellow */
        border-left: 5px solid #ffc107;
        padding: 1em;
        border-radius: 0.3em;
        color: #856404;
    }
    
    /* Metrics styling */
    .st-emotion-cache-1dlfddc { /* Metric value */
        color: #0e3b6f;
        font-weight: 700;
    }
    .st-emotion-cache-1s3t0z4 { /* Metric label */
        color: #555555;
    }

    /* Dataframe styling */
    .st-emotion-cache-fg4pbf {
        border: 1px solid #e6e6e6;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)


# --- Report Card Logic (Adapted from SR0-4.18.py) ---
def calculate_grades(df_scores):
    """
    Calculates final scores, grades, and remarks for a DataFrame of subjects.
    Assumes df_scores has 'CA1', 'CA2', 'Exam' columns.
    Returns the DataFrame with 'Final', 'Grade', 'Remark' columns added.
    """
    if df_scores.empty:
        return df_scores

    # Ensure numeric types, coercing errors
    df_scores['CA1'] = pd.to_numeric(df_scores['CA1'], errors='coerce').fillna(0)
    df_scores['CA2'] = pd.to_numeric(df_scores['CA2'], errors='coerce').fillna(0)
    df_scores['Exam'] = pd.to_numeric(df_scores['Exam'], errors='coerce').fillna(0)

    df_scores['Final'] = df_scores['CA1'] + df_scores['CA2'] + df_scores['Exam']

    def get_grade_remark(score):
        if score >= 75:
            return "A", "Excellent"
        elif score >= 60:
            return "B", "Very Good"
        elif score >= 50:
            return "C", "Credit"
        else:
            return "F", "Failed"

    df_scores[['Grade', 'Remark']] = df_scores['Final'].apply(lambda x: pd.Series(get_grade_remark(x)))
    return df_scores

def ordinal(n):
    """Converts a number to its ordinal string (e.g., 1st, 2nd, 3rd)."""
    return "%d%s" % (n, "tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])

# --- Teacher Portal ---
def teacher_portal():
    st.title("👨‍🏫 Teacher Portal")
    st.subheader("Manage Student Results and Profiles")

    st.sidebar.markdown("---")
    st.sidebar.button("Logout", on_click=logout)

    st.write("Welcome, Teacher! Here you can upload and manage student results and their profiles.")

    # Create tabs for better organization
    tab_results, tab_profiles, tab_accounts = st.tabs(["📊 Manage Results", "🧑‍🎓 Student Profiles", "🔑 Student Accounts"])

    with tab_results:
        st.subheader("Upload Student Results (Excel File)")
        st.info("Expected Excel format: Student Name in cell B2. Subject data starts from Row 9, Column A. Columns needed: 'Subject', 'CA 1' (or 'CA1'), 'CA 2' (or 'CA2'), and 'Exam'.")

        uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])

        if uploaded_file is not None:
            try:
                # Read student name from B2
                student_info_df = pd.read_excel(uploaded_file, header=None, nrows=2, usecols="B", engine='openpyxl')
                student_name = student_info_df.iloc[1, 0]

                if not student_name:
                    st.error("Could not find student name in cell B2 of the Excel file.")
                    return

                # Clean up student name: remove leading/trailing spaces and newlines
                student_name = str(student_name).strip()

                st.write(f"Detected Student Name: **{student_name}**")

                # Read subject data starting from row 9 (skiprows=8)
                # Use 'header=0' to ensure the first row after skiprows is treated as the header
                df = pd.read_excel(uploaded_file, skiprows=8, header=0, engine='openpyxl')

                # --- Robust Column Name Normalization and Validation ---
                df.columns = [col.strip() for col in df.columns]
                normalized_cols = {col.lower().replace(' ', ''): col for col in df.columns}

                required_mappings = {
                    'subject': 'Subject',
                    'ca1': 'CA1',
                    'ca2': 'CA2',
                    'exam': 'Exam'
                }
                
                found_columns = {}
                missing_expected_columns = []

                for normalized_expected, final_name in required_mappings.items():
                    if normalized_expected in normalized_cols:
                        found_columns[normalized_cols[normalized_expected]] = final_name
                    else:
                        missing_expected_columns.append(final_name)
                
                if missing_expected_columns:
                    st.error(f"Error: The uploaded Excel file is missing one or more required columns. Please ensure you have columns like 'Subject', 'CA 1' (or 'CA1'), 'CA 2' (or 'CA2'), and 'Exam'. Missing: {missing_expected_columns}")
                    return

                # Rename columns to their standardized form
                df.rename(columns=found_columns, inplace=True)
                
                # Select only the required columns for processing, in the correct order
                df = df[list(required_mappings.values())]

                # Fill empty values (NaNs) with 0 for calculations
                df.fillna(0, inplace=True)

                # Calculate grades and remarks
                processed_df = calculate_grades(df.copy())

                st.success(f"Successfully processed data for {student_name}.")
                st.dataframe(processed_df, hide_index=True)

                if st.button(f"Save Results for {student_name}"):
                    student_results = processed_df.to_dict(orient='records')
                    
                    existing_student_index = -1
                    for i, entry in enumerate(st.session_state.results_data):
                        if entry.get('student_name') == student_name:
                            existing_student_index = i
                            break

                    if existing_student_index != -1:
                        st.session_state.results_data[existing_student_index]['results'] = student_results
                        st.session_state.results_data[existing_student_index]['total_score'] = processed_df['Final'].sum()
                        st.success(f"Updated results for {student_name}!")
                    else:
                        new_result_entry = {
                            "student_name": student_name,
                            "total_score": processed_df['Final'].sum(),
                            "results": student_results
                        }
                        st.session_state.results_data.append(new_result_entry)
                        st.success(f"Saved new results for {student_name}!")

                    # --- Automatic Student Account and Profile Creation/Update ---
                    # 1. Ensure student account exists
                    if not any(s['username'].lower() == student_name.lower() for s in st.session_state.students_data):
                        max_id = 0
                        if st.session_state.students_data:
                            max_id = max([s.get('id', 0) for s in st.session_state.students_data])
                        
                        new_student_id = max_id + 1
                        
                        st.session_state.students_data.append({
                            "id": new_student_id,
                            "username": student_name,
                            "password": "123456" # Default password
                        })
                        save_data(st.session_state.students_data, STUDENTS_FILE)
                        st.info(f"Added {student_name} to student accounts with default password '123456'.")

                    # 2. Ensure student profile exists (or create basic one)
                    if not any(p['student_name'].lower() == student_name.lower() for p in st.session_state.student_profiles_data):
                        st.session_state.student_profiles_data.append({
                            "student_name": student_name,
                            "age": "", "reg_number": "", "parent_name": "",
                            "parent_phone": "", "parent_address": "",
                            "session": "", "term": ""
                        })
                        st.warning(f"A basic profile for {student_name} was created. Please go to the 'Student Profiles' tab to fill in more details.")
                        save_data(st.session_state.student_profiles_data, STUDENT_PROFILES_FILE)

                    save_data(st.session_state.results_data, RESULTS_FILE)
                    st.rerun() # Rerun to update the displayed data and tabs

            except Exception as e:
                st.error(f"Error processing Excel file: {e}")
                st.warning("Please ensure the Excel file format matches the expected structure.")
                st.exception(e)

    with tab_profiles:
        st.subheader("Manage Student Profiles")

        student_names_in_profiles = [""] + [p['student_name'] for p in st.session_state.student_profiles_data]
        selected_student_for_profile = st.selectbox("Select Student to Edit/View Profile", student_names_in_profiles, key="select_profile_student")

        current_profile = None
        if selected_student_for_profile:
            current_profile = next((p for p in st.session_state.student_profiles_data if p['student_name'] == selected_student_for_profile), None)

        with st.form("student_profile_form", clear_on_submit=False):
            st.markdown("### Student Profile Details")
            
            # Pre-fill if editing an existing profile
            default_name = current_profile['student_name'] if current_profile else ""
            default_age = current_profile['age'] if current_profile else 0 # Changed default to 0 for number_input
            default_reg_number = current_profile['reg_number'] if current_profile else ""
            default_parent_name = current_profile['parent_name'] if current_profile else ""
            default_parent_phone = current_profile['parent_phone'] if current_profile else ""
            default_parent_address = current_profile['parent_address'] if current_profile else ""
            
            # Set default index for selectboxes carefully
            default_session_index = SESSIONS.index(current_profile['session']) if current_profile and current_profile['session'] in SESSIONS else 0
            default_term_index = TERMS.index(current_profile['term']) if current_profile and current_profile['term'] in TERMS else 0
            
            # If no student is selected, ensure the first item is selected by default for new entry
            if not selected_student_for_profile:
                default_name = ""
                default_age = 0
                default_reg_number = ""
                default_parent_name = ""
                default_parent_phone = ""
                default_parent_address = ""
                default_session_index = 0
                default_term_index = 0


            # Input fields
            student_name_input = st.text_input("Student Name (Must match name in results file)", value=default_name, disabled=bool(selected_student_for_profile), key="profile_student_name")
            age_input = st.number_input("Age", min_value=0, max_value=100, value=default_age, key="profile_age")
            reg_number_input = st.text_input("Registration Number", value=default_reg_number, key="profile_reg_number")
            parent_name_input = st.text_input("Parent/Guardian Name", value=default_parent_name, key="profile_parent_name")
            parent_phone_input = st.text_input("Parent/Guardian Phone Number", value=default_parent_phone, key="profile_parent_phone")
            parent_address_input = st.text_area("Parent/Guardian Address", value=default_parent_address, key="profile_parent_address")
            session_select = st.selectbox("Academic Session", options=SESSIONS, index=default_session_index, key="profile_session")
            term_select = st.selectbox("Academic Term", options=TERMS, index=default_term_index, key="profile_term")

            col1, col2 = st.columns(2)
            with col1:
                submit_profile_button = st.form_submit_button("Save Profile")
            with col2:
                # Only show delete button if a profile is selected
                if selected_student_for_profile and current_profile:
                    delete_profile_button_clicked = st.form_submit_button("Delete Profile", help="Removes this profile (does NOT delete student account or results).")
                else:
                    delete_profile_button_clicked = False # Ensure it's false if button isn't shown


            if submit_profile_button:
                if not student_name_input.strip():
                    st.error("Student Name cannot be empty.")
                else:
                    new_profile_data = {
                        "student_name": student_name_input.strip(),
                        "age": age_input,
                        "reg_number": reg_number_input.strip(),
                        "parent_name": parent_name_input.strip(),
                        "parent_phone": parent_phone_input.strip(),
                        "parent_address": parent_address_input.strip(),
                        "session": session_select,
                        "term": term_select
                    }

                    profile_exists_index = -1
                    for i, p in enumerate(st.session_state.student_profiles_data):
                        if p['student_name'].lower() == student_name_input.strip().lower():
                            profile_exists_index = i
                            break
                    
                    if selected_student_for_profile and current_profile: # Editing existing
                        if profile_exists_index != -1:
                            st.session_state.student_profiles_data[profile_exists_index] = new_profile_data
                            st.success(f"Profile for {student_name_input} updated successfully!")
                        else: # Should not happen if `selected_student_for_profile` is set
                             st.error("Error: Could not find the selected profile to update. Please refresh.")
                    else: # Adding new profile (via this form, not auto-creation)
                        if profile_exists_index == -1: # Ensure it doesn't exist
                            st.session_state.student_profiles_data.append(new_profile_data)
                            st.success(f"New profile for {student_name_input} added successfully!")
                            # Also ensure a basic account exists if not already
                            if not any(s['username'].lower() == student_name_input.lower() for s in st.session_state.students_data):
                                max_id = 0
                                if st.session_state.students_data:
                                    max_id = max([s.get('id', 0) for s in st.session_state.students_data])
                                new_student_id = max_id + 1
                                st.session_state.students_data.append({
                                    "id": new_student_id,
                                    "username": student_name_input.strip(),
                                    "password": "123456"
                                })
                                save_data(st.session_state.students_data, STUDENTS_FILE)
                                st.info(f"Added {student_name_input} to student accounts with default password '123456'.")
                        else:
                            st.warning(f"A profile for {student_name_input} already exists. Please select it from the dropdown to edit.")
                    
                    save_data(st.session_state.student_profiles_data, STUDENT_PROFILES_FILE)
                    st.rerun()
            
            if delete_profile_button_clicked: # Check if the delete button was clicked
                # Confirmation for deletion
                confirm_delete = st.empty()
                if confirm_delete.button(f"Click again to CONFIRM Delete {selected_student_for_profile}'s Profile", key="confirm_delete_profile"):
                    st.session_state.student_profiles_data = [p for p in st.session_state.student_profiles_data if p['student_name'] != selected_student_for_profile]
                    save_data(st.session_state.student_profiles_data, STUDENT_PROFILES_FILE)
                    st.success(f"Profile for {selected_student_for_profile} deleted successfully.")
                    st.rerun()
                else:
                    st.warning(f"Are you sure you want to delete {selected_student_for_profile}'s profile? This action cannot be undone.")


        st.markdown("---")
        st.subheader("All Student Profiles")
        if st.session_state.student_profiles_data:
            profiles_df = pd.DataFrame(st.session_state.student_profiles_data)
            st.dataframe(profiles_df, hide_index=True, use_container_width=True)
        else:
            st.info("No student profiles added yet.")

    with tab_accounts:
        st.subheader("Registered Student Accounts")
        if st.session_state.students_data:
            students_df = pd.DataFrame(st.session_state.students_data)
            st.dataframe(students_df, hide_index=True)

            st.info("You can add/remove student login accounts here directly.")
            
            with st.form("add_student_form", clear_on_submit=True):
                st.subheader("Add New Student Login Account")
                new_student_username = st.text_input("New Student Username", key="new_login_username").strip()
                new_student_password = st.text_input("New Student Password", value="123456", key="new_login_password")
                add_student_button = st.form_submit_button("Add Student Login Account")

                if add_student_button:
                    if new_student_username and new_student_password:
                        if any(s['username'].lower() == new_student_username.lower() for s in st.session_state.students_data):
                            st.error("Student with this username already exists.")
                        else:
                            max_id = 0
                            if st.session_state.students_data:
                                max_id = max([s.get('id', 0) for s in st.session_state.students_data])
                            new_student_id = max_id + 1

                            st.session_state.students_data.append({
                                "id": new_student_id,
                                "username": new_student_username,
                                "password": new_student_password
                            })
                            save_data(st.session_state.students_data, STUDENTS_FILE)
                            st.success(f"Student login account '{new_student_username}' added successfully!")
                            # Also create a basic profile for them
                            if not any(p['student_name'].lower() == new_student_username.lower() for p in st.session_state.student_profiles_data):
                                st.session_state.student_profiles_data.append({
                                    "student_name": new_student_username,
                                    "age": "", "reg_number": "", "parent_name": "",
                                    "parent_phone": "", "parent_address": "",
                                    "session": "", "term": ""
                                })
                                save_data(st.session_state.student_profiles_data, STUDENT_PROFILES_FILE)
                                st.info(f"A basic profile was also created for {new_student_username}. Please fill in details in the 'Student Profiles' tab.")

                            st.rerun()
                    else:
                        st.error("Please provide both username and password for the new student login account.")
            
            with st.form("remove_student_form", clear_on_submit=True):
                st.subheader("Remove Student Login Account")
                current_student_usernames = [s['username'] for s in st.session_state.students_data if s['username'] != TEACHER_USERNAME] # Cannot remove teacher
                student_to_remove = st.selectbox("Select Student Login Account to Remove", options=[""] + current_student_usernames, key="remove_login_student")
                remove_student_button = st.form_submit_button("Remove Selected Login Account")

                if remove_student_button and student_to_remove:
                    # Remove from students_data (login accounts)
                    st.session_state.students_data = [s for s in st.session_state.students_data if s['username'] != student_to_remove]
                    save_data(st.session_state.students_data, STUDENTS_FILE)

                    # Also remove their results and profiles to keep data clean
                    st.session_state.results_data = [r for r in st.session_state.results_data if r['student_name'] != student_to_remove]
                    save_data(st.session_state.results_data, RESULTS_FILE)

                    st.session_state.student_profiles_data = [p for p in st.session_state.student_profiles_data if p['student_name'] != student_to_remove]
                    save_data(st.session_state.student_profiles_data, STUDENT_PROFILES_FILE)

                    st.success(f"Student '{student_to_remove}' login account, results, and profile removed successfully!")
                    st.rerun()
                elif remove_student_button:
                    st.error("Please select a student login account to remove.")
        else:
            st.info("No student accounts registered yet. They will be added when you upload results for them, or you can add them manually above.")


# --- Student Portal ---
def student_portal():
    student_name = st.session_state.username
    st.title(f"Hello, {student_name}! 👋")
    st.subheader("Your Report Card & Profile")

    st.sidebar.markdown("---")
    st.sidebar.button("Logout", on_click=logout)

    student_record = next((r for r in st.session_state.results_data if r['student_name'] == student_name), None)
    student_profile = next((p for p in st.session_state.student_profiles_data if p['student_name'] == student_name), None)

    col_profile, col_results = st.columns([1, 2])

    with col_profile:
        st.markdown("### Your Profile Details")
        if student_profile:
            st.write(f"**Name:** {student_profile.get('student_name', 'N/A')}")
            st.write(f"**Age:** {student_profile.get('age', 'N/A')}")
            st.write(f"**Registration No.:** {student_profile.get('reg_number', 'N/A')}")
            st.write(f"**Academic Session:** {student_profile.get('session', 'N/A')}")
            st.write(f"**Academic Term:** {student_profile.get('term', 'N/A')}")
            st.write(f"**Parent/Guardian:** {student_profile.get('parent_name', 'N/A')}")
            st.write(f"**Parent Phone:** {student_profile.get('parent_phone', 'N/A')}")
            st.write(f"**Parent Address:** {student_profile.get('parent_address', 'N/A')}")
            
            image_placeholder = st.empty()
            
            # Use relative path for deployment
            script_dir = os.path.dirname(__file__)
            photo_path = os.path.join(script_dir, "assets", f"{student_name} Image.png")
            
            if os.path.exists(photo_path):
                try:
                    image_placeholder.image(photo_path, caption=f"{student_name}'s Photo", width=150)
                except Exception as e:
                    image_placeholder.warning(f"Could not load photo: {e}")
            else:
                image_placeholder.info(f"No photo found for {student_name} in the 'assets' folder.")
        else:
            st.info("Your profile details are not yet available. Please ask your teacher to update them.")

    with col_results:
        st.markdown("### Your Results")
        if student_record:
            results_df = pd.DataFrame(student_record['results'])
            total_score_student = results_df['Final'].sum()

            all_student_totals = {r['student_name']: r['total_score'] for r in st.session_state.results_data if 'total_score' in r and isinstance(r['total_score'], (int, float))}
            
            sorted_students = sorted(all_student_totals.items(), key=lambda x: x[1], reverse=True)
            
            rank = "N/A"
            for i, (name, score) in enumerate(sorted_students):
                if name == student_name:
                    rank = ordinal(i + 1)
                    break
            
            st.write(f"**Total Score:** {total_score_student}")
            st.write(f"**Rank:** {rank} Position")

            st.dataframe(results_df, hide_index=True, use_container_width=True)

            st.subheader("Download Report Card")
            pdf_output = generate_report_card_pdf(student_name, results_df, total_score_student, rank, student_profile)
            
            st.download_button(
                label="Download as PDF",
                data=bytes(pdf_output.output(dest='S')),
                file_name=f"{student_name}_Report_Card.pdf",
                mime="application/pdf"
            )
        else:
            st.info("No report card data available for you yet. Please check back later.")


# --- PDF Generation (Adapted from SR0-4.18.py) ---
class PDF(FPDF):
    def header(self):
        # Use a path relative to the script's directory for deployment
        script_dir = os.path.dirname(__file__)
        logo_path = os.path.join(script_dir, "assets", "ICY.png")
        if os.path.exists(logo_path):
            try:
                self.image(logo_path, x=10, y=8, w=25)
            except Exception as e:
                print(f"Warning: Could not load logo image for PDF: {e}") # For debugging in console
        
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "IGBOBI COLLEGE YABA", ln=True, align="C")
        self.set_font("Arial", "", 12)
        self.cell(0, 10, "Igobobi College Road, Fadeyi, Lagos", ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

def generate_report_card_pdf(student_name, results_df, total_score, rank, student_profile=None):
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    # Get the directory of the current script for relative paths
    script_dir = os.path.dirname(__file__) 

    # Student Photo Path
    photo_path = os.path.join(script_dir, "assets", f"{student_name} Image.png")
    if os.path.exists(photo_path):
        try:
            pdf.image(photo_path, x=170, y=8, w=25)
        except Exception as e:
            # print(f"Warning: Could not embed student photo in PDF: {e}") # For debugging in console
            pass # Suppress warning in PDF generation if image fails

    pdf.set_font("Arial", "B", 12)
    pdf.cell(40, 10, f"Student Name: {student_name}", ln=True)
    
    # Add profile details to PDF
    pdf.set_font("Arial", "", 11)
    if student_profile:
        pdf.cell(0, 7, f"Age: {student_profile.get('age', 'N/A')}", ln=True)
        pdf.cell(0, 7, f"Registration No.: {student_profile.get('reg_number', 'N/A')}", ln=True)
        pdf.cell(0, 7, f"Academic Session: {student_profile.get('session', 'N/A')}", ln=True)
        pdf.cell(0, 7, f"Academic Term: {student_profile.get('term', 'N/A')}", ln=True)
        pdf.cell(0, 7, f"Parent/Guardian: {student_profile.get('parent_name', 'N/A')}", ln=True)
        pdf.cell(0, 7, f"Parent Phone: {student_profile.get('parent_phone', 'N/A')}", ln=True)
        pdf.cell(0, 7, f"Parent Address: {student_profile.get('parent_address', 'N/A')}", ln=True)
    else:
        pdf.cell(0, 7, "Profile Details: Not available", ln=True)
        
    pdf.ln(3) # Small line break

    pdf.set_font("Arial", "B", 11)
    pdf.cell(40, 10, f"Total Score: {total_score}", ln=True)
    pdf.cell(40, 10, f"Rank: {rank} Position", ln=True)
    pdf.ln(5)

    headers = results_df.columns.tolist()
    
    # Calculate column widths more dynamically, with a minimum size
    col_widths = []
    for header in headers:
        text_width = pdf.get_string_width(str(header))
        col_widths.append(max(20, text_width + 10)) # Minimum 20 units, plus padding

    # Adjust if total width exceeds page width
    total_table_width = sum(col_widths)
    page_usable_width = pdf.w - pdf.l_margin - pdf.r_margin # Page width minus left/right margins
    if total_table_width > page_usable_width:
        scale_factor = page_usable_width / total_table_width
        col_widths = [w * scale_factor for w in col_widths]


    pdf.set_font("Arial", "B", 10)
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, str(header), border=1, align="C")
    pdf.ln()

    pdf.set_font("Arial", "", 10)
    for _, row in results_df.iterrows():
        for i, val in enumerate(row.tolist()):
            # Handle long text in cells if necessary, or just let fpdf truncate/wrap
            pdf.cell(col_widths[i], 10, str(val), border=1, align="C")
        pdf.ln()
    
    # --- Digital Signatures ---
    pdf.ln(15) # Add some space after the table

    signature_y_pos = pdf.get_y() # Get current Y position

    # Define signature image paths using relative path
    class_teacher_sig_path = os.path.join(script_dir, "assets", "class_teacher_signature.png")
    hod_sig_path = os.path.join(script_dir, "assets", "hod_signature.png")
    principal_sig_path = os.path.join(script_dir, "assets", "principal_signature.png")

    # Signature image dimensions (adjust as needed)
    sig_img_width = 30
    sig_img_height = 15

    # Signature text spacing
    sig_text_ln = 5 # Line height for text below signature

    # Calculate x positions for three signatures to be evenly spaced
    # Assuming standard A4 (210mm wide), and margins of 10mm on each side (total 190mm usable width)
    # This places them roughly centered and spread out
    x1 = 20 # Left signature
    x2 = pdf.w / 2 - (sig_img_width / 2) # Center signature
    x3 = pdf.w - sig_img_width - 20 # Right signature

    # Class Teacher Signature
    pdf.set_x(x1)
    if os.path.exists(class_teacher_sig_path):
        try:
            pdf.image(class_teacher_sig_path, x=x1, y=signature_y_pos, w=sig_img_width, h=sig_img_height)
        except Exception as e:
            print(f"Warning: Could not embed Class Teacher signature: {e}")
    pdf.set_y(signature_y_pos + sig_img_height + 2) # Move y down for text
    pdf.set_x(x1)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(sig_img_width, sig_text_ln, "Class Teacher", 0, 0, 'C') # Text below signature


    # HOD Signature
    pdf.set_y(signature_y_pos) # Reset y for next signature
    pdf.set_x(x2)
    if os.path.exists(hod_sig_path):
        try:
            pdf.image(hod_sig_path, x=x2, y=signature_y_pos, w=sig_img_width, h=sig_img_height)
        except Exception as e:
            print(f"Warning: Could not embed HOD signature: {e}")
    pdf.set_y(signature_y_pos + sig_img_height + 2)
    pdf.set_x(x2)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(sig_img_width, sig_text_ln, "HOD", 0, 0, 'C')


    # Principal Signature
    pdf.set_y(signature_y_pos) # Reset y for next signature
    pdf.set_x(x3)
    if os.path.exists(principal_sig_path):
        try:
            pdf.image(principal_sig_path, x=x3, y=signature_y_pos, w=sig_img_width, h=sig_img_height)
        except Exception as e:
            print(f"Warning: Could not embed Principal signature: {e}")
    pdf.set_y(signature_y_pos + sig_img_height + 2)
    pdf.set_x(x3)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(sig_img_width, sig_text_ln, "Principal", 0, 1, 'C') # ln=1 to move to next line after last signature

    
    return pdf


# --- Main Application Logic ---
def main():
    st.set_page_config(
        page_title="Student Report Card Portal",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    apply_custom_css()
    initialize_session_state()

    if not st.session_state.logged_in:
        st.sidebar.title("Login")
        with st.sidebar.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")

            if login_button:
                authenticate_user(username, password)
        st.info("Please login to access the portal.")
    elif st.session_state.user_role == 'teacher':
        teacher_portal()
    elif st.session_state.user_role == 'student':
        student_portal()

if __name__ == "__main__":
    main()

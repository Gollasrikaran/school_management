import streamlit as st
from database import create_users_table, add_user, create_school_tables, load_data, create_connection
from auth import login_form
from branch_admin import branch_admin_dashboard
from teacher_dashboard import teacher_dashboard
import pandas as pd


# Initialize database if it doesn't exist
create_users_table()
create_school_tables()
     # Initialize school database tables

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'role' not in st.session_state:
    st.session_state.role = None

def home_page():
    st.title(f"Welcome, {st.session_state.username}!")
    st.write(f"Your role is: {st.session_state.role}")
    st.write("This is the protected home page.")


def superadmin_dashboard():
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page", ["Schools", "Branches", "Teachers", "Classes"])

    if page == "Schools":
        st.header("Manage Schools")
        # Add School Form
        with st.form("add_school_form"):
            school_name = st.text_input("School Name")
            address = st.text_input("Address")
            branch_name = st.text_input("Branch Name")
            submitted = st.form_submit_button("Add School")

            if submitted and school_name and branch_name:
                conn = create_connection("school.db")
                try:
                    with conn:
                        conn.execute("""
                            INSERT INTO Schools (name, address, branch_name)
                            VALUES (?, ?, ?)
                        """, (school_name, address, branch_name))
                    st.success("School and Branch information added successfully!")
                except Exception as e:
                    st.error(f"Error adding school: {e}")

        # Update School ID
        with st.form("update_school_id_form"):
            current_branch_name = st.text_input("Branch Name to Update ID")
            new_id = st.text_input("New ID")
            update_submitted = st.form_submit_button("Update School ID")

            if update_submitted and current_branch_name and new_id:
                conn = create_connection("school.db")
                try:
                    with conn:
                        conn.execute("""
                            UPDATE Schools
                            SET id = ?
                            WHERE branch_name = ?
                        """, (new_id, current_branch_name))
                        st.success("School ID updated successfully!")
                except Exception as e:
                    st.error(f"Error updating school ID: {e}")

        # Update School Address
        with st.form("update_school_address_form"):
            current_branch_name = st.text_input("Branch Name to Update Address")
            new_address = st.text_input("New Address")
            update_address_submitted = st.form_submit_button("Update School Address")

            if update_address_submitted and current_branch_name and new_address:
                conn = create_connection("school.db")
                try:
                    with conn:
                        conn.execute("""
                            UPDATE Schools
                            SET address = ?
                            WHERE branch_name = ?
                        """, (new_address, current_branch_name))
                        st.success("School address updated successfully!")
                except Exception as e:
                    st.error(f"Error updating school address: {e}")

        # Delete School by Branch Name
        with st.form("delete_school_form"):
            branch_name_to_delete = st.text_input("Branch Name to Delete")
            delete_submitted = st.form_submit_button("Delete School by Branch Name")

            if delete_submitted and branch_name_to_delete:
                conn = create_connection("school.db")
                try:
                    with conn:
                        conn.execute("DELETE FROM Schools WHERE branch_name = ?", (branch_name_to_delete,))
                    st.success(f"School with Branch Name '{branch_name_to_delete}' deleted successfully!")
                except Exception as e:
                    st.error(f"Error deleting school: {e}")

        # Display existing schools
        schools_df = load_data("SELECT * FROM Schools")
        if not schools_df.empty:
            st.subheader("Existing Schools")
            st.dataframe(schools_df)

    elif page == "Branches":
        st.header("Manage Branches")

        branches_df = load_data("SELECT id, name, address, branch_name FROM Schools")
        if not branches_df.empty:
            st.subheader("Existing Branches")
            st.dataframe(branches_df)

            # Update Branch Name
            with st.form("update_branch_form"):
                branch_id = st.selectbox("Select School to Update Branch", options=branches_df['id'].tolist(),
                                        format_func=lambda x: branches_df[branches_df['id'] == x]['name'].iloc[0])
                new_branch_name = st.text_input("New Branch Name")
                submitted = st.form_submit_button("Update Branch Name")

                if submitted and new_branch_name:
                    conn = create_connection("school.db")
                    try:
                        with conn:
                            conn.execute("""
                                UPDATE Schools
                                SET branch_name = ?
                                WHERE id = ?
                            """, (new_branch_name, branch_id))
                        st.success("Branch name updated successfully!")
                    except Exception as e:
                        st.error(f"Error updating branch name: {e}")

            # Delete Branch
            with st.form("delete_branch_form"):
                branch_name_to_delete = st.text_input("Branch Name to Delete")
                delete_submitted = st.form_submit_button("Delete Branch by Branch Name")

                if delete_submitted and branch_name_to_delete:
                    conn = create_connection("school.db")
                    try:
                        with conn:
                            conn.execute("DELETE FROM Schools WHERE branch_name = ?", (branch_name_to_delete,))
                        st.success(f"Branch with Branch Name '{branch_name_to_delete}' deleted successfully!")
                    except Exception as e:
                        st.error(f"Error deleting branch: {e}")
        else:
            st.warning("No schools available. Please add schools first.")

    elif page == "Teachers":
        st.header("Manage Teachers")

        # Add Teacher Form
        with st.form("add_teacher_form"):
            teacher_name = st.text_input("Teacher Name")
            school_name = st.text_input("School Name")
            branch_name = st.text_input("Branch Name")
            subject = st.text_input("Subject")
            submitted = st.form_submit_button("Add Teacher")

            if submitted and teacher_name and school_name and branch_name and subject:
                conn = create_connection("school.db")
                try:
                    with conn:
                        conn.execute("""
                            INSERT INTO Teachers (teacher_name, school_name, branch_name, subject)
                            VALUES (?, ?, ?, ?)
                        """, (teacher_name, school_name, branch_name, subject))
                    st.success(f"Teacher '{teacher_name}' added successfully!")
                except Exception as e:
                    st.error(f"Error adding teacher: {e}")

        # Delete Teacher by Name
        with st.form("delete_teacher_form"):
            teacher_name_to_delete = st.text_input("Teacher Name to Delete")
            delete_teacher_submitted = st.form_submit_button("Delete Teacher")

            if delete_teacher_submitted and teacher_name_to_delete:
                conn = create_connection("school.db")
                try:
                    with conn:
                        conn.execute("DELETE FROM Teachers WHERE teacher_name = ?", (teacher_name_to_delete,))
                    st.success(f"Teacher '{teacher_name_to_delete}' deleted successfully!")
                except Exception as e:
                    st.error(f"Error deleting teacher: {e}")

        # Display existing teachers
        teachers_df = load_data("SELECT * FROM Teachers")
        if not teachers_df.empty:
            st.subheader("Existing Teachers")
            st.dataframe(teachers_df)
        else:
            st.warning("No teachers available. Please add teachers.")

    elif page == "Classes":
        st.header("Manage Classes")

        # Load existing branches for dropdown
        branches_df = load_data("SELECT id, branch_name FROM Schools")
        branch_options = branches_df['branch_name'].tolist()

        # Form for adding classes
        with st.form("add_class_form"):
            school_name = st.text_input("School Name")
            branch_name = st.selectbox("Branch Name", options=branch_options)  # Dropdown for branch
            class_no = st.number_input("Class Number", min_value=1, max_value=12, step=1)
            section = st.text_input("Section")
            no_of_students = st.number_input("Number of Students", min_value=0, step=1)
            submitted = st.form_submit_button("Add Class")

            if submitted and school_name and branch_name and class_no and section and no_of_students:
                conn = create_connection("school.db")
                try:
                    with conn:
                        # Fetch the branch_id based on school_name and branch_name
                        cursor = conn.cursor()
                        cursor.execute("SELECT id FROM Schools WHERE name = ? AND branch_name = ?",
                                    (school_name, branch_name))
                        result = cursor.fetchone()
                        if result:
                            branch_id = result[0]
                            # Check if class already exists
                            cursor.execute("SELECT * FROM Classes WHERE branch_id = ? AND class = ? AND section = ?",
                                            (branch_id, class_no, section))
                            existing_class = cursor.fetchone()
                            if existing_class:
                                st.error(f"Class {class_no}-{section} already exists for branch '{branch_name}'.")
                            else:
                                conn.execute("""
                                    INSERT INTO Classes (branch_id, class, section, no_of_students)
                                    VALUES (?, ?, ?, ?)
                                """, (branch_id, class_no, section, no_of_students))
                                st.success(f"Class {class_no}-{section} added for branch '{branch_name}' successfully!")
                        else:
                            st.error("School or branch not found. Please check the school and branch names.")
                except Exception as e:
                    st.error(f"Error adding class: {e}")

        # Form to update class
        classes_df = load_data("SELECT id, class, section, branch_id, no_of_students FROM Classes")
        with st.form("update_class_form"):
            if not classes_df.empty:
                class_id = st.selectbox("Select class to update", options=classes_df['id'].tolist(),
                                        format_func=lambda x: f"Class {classes_df[classes_df['id'] == x]['class'].iloc[0]}-{classes_df[classes_df['id'] == x]['section'].iloc[0]}")
                new_class_no = st.number_input("New Class Number", min_value=1, max_value=12, step=1)
                new_section = st.text_input("New Section")
                new_no_of_students = st.number_input("Number of Students", min_value=0, step=1)
                update_submitted = st.form_submit_button("Update Class")

                if update_submitted and new_class_no and new_section and new_no_of_students:
                    conn = create_connection("school.db")
                    try:
                        with conn:
                            conn.execute("""
                                UPDATE Classes
                                SET class = ?, section = ?, no_of_students = ?
                                WHERE id = ?
                            """, (new_class_no, new_section, new_no_of_students, class_id))
                            st.success(f"Class updated to {new_class_no}-{new_section} successfully!")
                    except Exception as e:
                        st.error(f"Error updating class: {e}")
            else:
                st.warning("No classes available. Please add classes first.")

        # Form to delete class
        with st.form("delete_class_form"):
            if not classes_df.empty:
                class_no_to_delete = st.number_input("Class Number to Delete", min_value=1, max_value=12, step=1)
                section_to_delete = st.text_input("Section to Delete")
                delete_submitted = st.form_submit_button("Delete Class")

                if delete_submitted and class_no_to_delete and section_to_delete:
                    conn = create_connection("school.db")
                    try:
                        with conn:
                            # Delete class based on class and section
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM Classes WHERE class = ? AND section = ?",
                                            (class_no_to_delete, section_to_delete))
                            if cursor.rowcount > 0 :
                                st.success(f"Class {class_no_to_delete}-{section_to_delete} deleted successfully!")
                            else:
                                st.error(f"Class {class_no_to_delete}-{section_to_delete} not found, please check the class and section")
                    except Exception as e:
                        st.error(f"Error deleting class: {e}")
            else:
                st.warning("No classes available. Please add classes first.")

        # Display Existing Classes
        classes_df = load_data("SELECT c.id, s.name as school_name, s.branch_name, c.class, c.section, c.no_of_students FROM Classes c JOIN Schools s ON c.branch_id = s.id")
        if not classes_df.empty:
            st.subheader("Existing Classes")
            st.dataframe(classes_df)
        else:
            st.warning("No classes available. Please add classes.")


def main():
    st.title("Login App")
    if not st.session_state.logged_in:
        login_form()
    else:
        # Logout button in the sidebar
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.role = None
        
        if st.session_state.role == "superadmin":
             superadmin_dashboard()
        elif st.session_state.role == "branchadmin":
            branch_name = st.sidebar.radio("Select Branch", ["Malakpet", "Dilshuknagar"])
            branch_admin_dashboard(branch_name)
        elif st.session_state.role == "teacher":
            teacher_dashboard()
        else:
            home_page()
    # --- Add new user section (for dev) ---
    st.sidebar.title("Dev Add User")
    with st.sidebar.form("add_user"):
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        new_role = st.selectbox("Select Role", ["superadmin", "branchadmin", "teacher"])
        add_user_button = st.form_submit_button("Add New User")

    if add_user_button:
         add_user(new_username, new_password, new_role)

if __name__ == "__main__":
    # Add users with provided credentials (for demo)
    add_user("admin@his.com", "admin", "superadmin")
    add_user("akt", "akt", "branchadmin")
    add_user("tkt", "tkt", "teacher")
    # Add dummy branch for demo
    conn = create_connection("school.db")
    with conn:
        conn.execute("INSERT INTO Schools (name, address, branch_name) VALUES (?, ?, ?)", ("Dummy School 1", "Dummy Address 1", "Malakpet"))
        conn.execute("INSERT INTO Schools (name, address, branch_name) VALUES (?, ?, ?)", ("Dummy School 2", "Dummy Address 2", "Dilshuknagar"))

    main()

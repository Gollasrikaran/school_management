import streamlit as st
from database import load_data, create_connection
import pandas as pd

def branch_admin_dashboard(branch_name):
    st.title("Branch Admin Dashboard")

    # Get the current user role from session
    user_role = st.session_state.role

    if user_role != "branchadmin":
        st.error("You do not have access to this page.")
        return

    if not branch_name:
        st.warning("Select a branch.")
        return

    st.header(f"Manage {branch_name} Branch Data")

    # --- Manage Teachers ---
    st.subheader("Manage Teachers")
    with st.form("add_teacher_form"):
      teacher_name = st.text_input("Teacher Name")
      school_name = st.text_input("School Name")
      subject = st.text_input("Subject")
      submitted = st.form_submit_button("Add Teacher")

      if submitted and teacher_name and school_name and subject:
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
                    conn.execute("DELETE FROM Teachers WHERE teacher_name = ? AND branch_name = ?", (teacher_name_to_delete, branch_name))
                st.success(f"Teacher '{teacher_name_to_delete}' deleted successfully!")
            except Exception as e:
                st.error(f"Error deleting teacher: {e}")

    # --- Manage Classes ---
    st.subheader("Manage Classes")

    # Form for adding classes
    with st.form("add_class_form"):
        school_name = st.text_input("School Name")
        class_no = st.number_input("Class Number", min_value=1, max_value=12, step=1)
        section = st.text_input("Section")
        no_of_students = st.number_input("Number of Students", min_value=0, step=1)
        submitted = st.form_submit_button("Add Class")

        if submitted and school_name and class_no and section and no_of_students:
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
    classes_df = load_data(f"SELECT id, class, section, branch_id, no_of_students FROM Classes WHERE branch_id IN (SELECT id FROM Schools WHERE branch_name = '{branch_name}')")
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
                        cursor.execute("DELETE FROM Classes WHERE class = ? AND section = ? AND branch_id IN (SELECT id FROM Schools WHERE branch_name = ?)",
                                        (class_no_to_delete, section_to_delete, branch_name))
                        if cursor.rowcount > 0 :
                            st.success(f"Class {class_no_to_delete}-{section_to_delete} deleted successfully!")
                        else:
                            st.error(f"Class {class_no_to_delete}-{section_to_delete} not found, please check the class and section")
                except Exception as e:
                    st.error(f"Error deleting class: {e}")
        else:
            st.warning("No classes available. Please add classes first.")
    
     # --- Manage Students ---
    st.subheader("Manage Students")

    # Form to add new students
    with st.form("add_student_form"):
        student_name = st.text_input("Student Name")
        class_no = st.number_input("Class Number", min_value=1, max_value=12, step=1)
        section = st.text_input("Section")
        submitted = st.form_submit_button("Add Student")

        if submitted and student_name and class_no and section:
            conn = create_connection("school.db")
            try:
                with conn:
                    # Fetch the branch_id
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM Schools WHERE branch_name = ?", (branch_name,))
                    result = cursor.fetchone()
                    if result:
                         branch_id = result[0]
                         conn.execute("""
                             INSERT INTO Students (student_name, class, section, branch_id)
                             VALUES (?, ?, ?, ?)
                         """, (student_name, class_no, section, branch_id))
                         st.success(f"Student '{student_name}' added to class {class_no}-{section} successfully!")
                    else:
                        st.error("Branch not found. Please check the branch name.")
            except Exception as e:
                st.error(f"Error adding student: {e}")

    # Form to delete students
    with st.form("delete_student_form"):
      student_name_to_delete = st.text_input("Student Name to Delete")
      class_no_to_delete = st.number_input("Class Number to Delete", min_value=1, max_value=12, step=1)
      section_to_delete = st.text_input("Section to Delete")
      delete_student_submitted = st.form_submit_button("Delete Student")
      if delete_student_submitted and student_name_to_delete and class_no_to_delete and section_to_delete:
           conn = create_connection("school.db")
           try:
                with conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM Students WHERE student_name = ? AND class = ? AND section = ? AND branch_id IN (SELECT id FROM Schools WHERE branch_name = ?)",
                                        (student_name_to_delete, class_no_to_delete, section_to_delete, branch_name))
                    if cursor.rowcount > 0 :
                         st.success(f"Student '{student_name_to_delete}' from class {class_no_to_delete}-{section_to_delete} deleted successfully!")
                    else:
                         st.error(f"Student '{student_name_to_delete}' from class {class_no_to_delete}-{section_to_delete} not found, please check the student name ,class and section")
           except Exception as e:
                    st.error(f"Error deleting student: {e}")

    # --- Display Students ---
    st.subheader("Existing Students")
    students_query = f"SELECT * FROM Students WHERE branch_id IN (SELECT id FROM Schools WHERE branch_name = '{branch_name}')"
    students_df = load_data(students_query)
    if not students_df.empty:
        st.dataframe(students_df)
    else:
        st.write("No students data available for this branch.")
    
    # --- Manage Subjects ---
    st.subheader("Manage Subjects")

    # Form to add new subjects
    with st.form("add_subject_form"):
        subject_name = st.text_input("Subject Name")
        submitted = st.form_submit_button("Add Subject")
        if submitted and subject_name:
           conn = create_connection("school.db")
           try:
                with conn:
                    conn.execute("INSERT INTO subject_names (subject_name, branch_name) VALUES (?, ?)", (subject_name, branch_name))
                    st.success(f"Subject '{subject_name}' added successfully!")
           except Exception as e:
                st.error(f"Error adding subject: {e}")

    # Form to delete a subject
    with st.form("delete_subject_form"):
        subject_name_to_delete = st.text_input("Subject Name to Delete")
        delete_submitted = st.form_submit_button("Delete Subject")

        if delete_submitted and subject_name_to_delete:
            conn = create_connection("school.db")
            try:
                with conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM subject_names WHERE subject_name = ? AND branch_name = ?", (subject_name_to_delete, branch_name))
                    if cursor.rowcount > 0 :
                         st.success(f"Subject '{subject_name_to_delete}' deleted successfully!")
                    else:
                         st.error(f"Subject '{subject_name_to_delete}' not found")
            except Exception as e:
                st.error(f"Error deleting subject: {e}")

    # Display existing subjects
    subjects_df = load_data(f"SELECT * FROM subject_names WHERE branch_name = '{branch_name}'")
    if not subjects_df.empty:
        st.subheader("Existing Subjects")
        st.dataframe(subjects_df)
    else:
        st.write("No subjects available.")
    
    # --- Manage Chapters ---
    st.subheader("Manage Chapters")

    # Subject selection dropdown
    subjects = load_data(f"SELECT subject_name FROM subject_names WHERE branch_name = '{branch_name}'")
    if not subjects.empty:
        selected_subject = st.selectbox("Select Subject", options=subjects['subject_name'].tolist(), key="subject_select_chapters")

        # Form to add chapters
        with st.form("add_chapter_form"):
            chapter_name = st.text_input("Chapter Name")
            submitted = st.form_submit_button("Add Chapter")

            if submitted and chapter_name:
                conn = create_connection("school.db")
                try:
                    with conn:
                        conn.execute("""
                            INSERT INTO chapters_name (chapter_name, subject_name, branch_name)
                            VALUES (?, ?, ?)
                        """, (chapter_name, selected_subject, branch_name))
                        st.success(f"Chapter '{chapter_name}' added to '{selected_subject}' successfully!")
                except Exception as e:
                    st.error(f"Error adding chapter: {e}")


        # Form to delete chapters
        with st.form("delete_chapter_form"):
             chapter_name_to_delete = st.text_input("Chapter Name to Delete")
             delete_chapter_submitted = st.form_submit_button("Delete Chapter")
             if delete_chapter_submitted and chapter_name_to_delete:
                conn = create_connection("school.db")
                try:
                    with conn:
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM chapters_name WHERE chapter_name = ? AND subject_name = ? AND branch_name = ?", (chapter_name_to_delete, selected_subject, branch_name))
                        if cursor.rowcount > 0:
                            st.success(f"Chapter '{chapter_name_to_delete}' deleted from '{selected_subject}' successfully!")
                        else:
                            st.error(f"Chapter '{chapter_name_to_delete}' not found for the subject '{selected_subject}'")
                except Exception as e:
                      st.error(f"Error deleting chapter: {e}")

        # Display existing chapters
        chapters_df = load_data(f"SELECT * FROM chapters_name WHERE subject_name = '{selected_subject}' AND branch_name = '{branch_name}'")
        if not chapters_df.empty:
            st.subheader(f"Existing Chapters for {selected_subject}")
            st.dataframe(chapters_df)
        else:
            st.write(f"No chapters available for {selected_subject}.")
    else:
        st.warning("No subjects available. Please add subjects first.")
    
    # --- Manage Topics ---
    st.subheader("Manage Topics")

    # Subject selection dropdown
    subjects = load_data(f"SELECT subject_name FROM subject_names WHERE branch_name = '{branch_name}'")
    if not subjects.empty:
        selected_subject = st.selectbox("Select Subject", options=subjects['subject_name'].tolist(), key="subject_select_topics")

        # Chapter selection dropdown
        chapters = load_data(f"SELECT chapter_name FROM chapters_name WHERE subject_name = '{selected_subject}' AND branch_name = '{branch_name}'")
        if not chapters.empty:
            selected_chapter = st.selectbox("Select Chapter", options=chapters['chapter_name'].tolist(), key="chapter_select_topics")
            
            # Form to add topics
            with st.form("add_topic_form"):
                 topic_name = st.text_input("Topic Name")
                 submitted = st.form_submit_button("Add Topic")

                 if submitted and topic_name:
                     conn = create_connection("school.db")
                     try:
                        with conn:
                            conn.execute("""
                                INSERT INTO topics_name (topic_name, chapter_name, subject_name, branch_name)
                                VALUES (?, ?, ?, ?)
                            """, (topic_name, selected_chapter, selected_subject, branch_name))
                            st.success(f"Topic '{topic_name}' added to '{selected_chapter}' successfully!")
                     except Exception as e:
                        st.error(f"Error adding topic: {e}")

            # Form to delete topics
            with st.form("delete_topic_form"):
                 topic_name_to_delete = st.text_input("Topic Name to Delete")
                 delete_topic_submitted = st.form_submit_button("Delete Topic")
                 if delete_topic_submitted and topic_name_to_delete:
                    conn = create_connection("school.db")
                    try:
                        with conn:
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM topics_name WHERE topic_name = ? AND chapter_name = ? AND subject_name = ? AND branch_name = ?", (topic_name_to_delete, selected_chapter, selected_subject, branch_name))
                            if cursor.rowcount > 0:
                                st.success(f"Topic '{topic_name_to_delete}' deleted from '{selected_chapter}' successfully!")
                            else:
                                st.error(f"Topic '{topic_name_to_delete}' not found for the chapter '{selected_chapter}'")
                    except Exception as e:
                          st.error(f"Error deleting topic: {e}")

            # Display existing topics
            topics_df = load_data(f"SELECT * FROM topics_name WHERE chapter_name = '{selected_chapter}' AND subject_name = '{selected_subject}' AND branch_name = '{branch_name}'")
            if not topics_df.empty:
                st.subheader(f"Existing Topics for {selected_chapter}")
                st.dataframe(topics_df)
            else:
                 st.write(f"No topics available for {selected_chapter}.")


        else:
            st.warning(f"No chapters available for the subject '{selected_subject}'.")

    else:
        st.warning("No subjects available. Please add subjects first.")



    # Fetch Data for selected branch
    if branch_name:
        schools_query = f"SELECT * FROM Schools WHERE branch_name = '{branch_name}'"
        teachers_query = f"SELECT * FROM Teachers WHERE branch_name = '{branch_name}'"
        classes_query = f"""
                    SELECT c.id, s.name as school_name, s.branch_name, c.class, c.section, c.no_of_students 
                    FROM Classes c 
                    JOIN Schools s ON c.branch_id = s.id 
                    WHERE s.branch_name = '{branch_name}'
        """
        students_query = f"SELECT * FROM Students WHERE branch_id IN (SELECT id FROM Schools WHERE branch_name = '{branch_name}')"
        subjects_query = f"SELECT * FROM subject_names WHERE branch_name = '{branch_name}'"
        chapters_query = f"SELECT * FROM chapters_name WHERE branch_name = '{branch_name}'"
        topics_query = f"SELECT * FROM topics_name WHERE branch_name = '{branch_name}'"

        schools_df = load_data(schools_query)
        teachers_df = load_data(teachers_query)
        classes_df = load_data(classes_query)
        students_df = load_data(students_query)
        subjects_df = load_data(subjects_query)
        chapters_df = load_data(chapters_query)
        topics_df = load_data(topics_query)

        # Display Data
        st.header(f"Overview for {branch_name}")

        if not schools_df.empty:
            st.subheader("School Information")
            st.dataframe(schools_df)
        else:
            st.warning("No school information available for this branch.")

        if not teachers_df.empty:
            st.subheader("Teachers Information")
            st.dataframe(teachers_df)
        else:
            st.warning("No teachers available for this branch.")

        if not classes_df.empty:
           st.subheader("Classes Information")
           st.dataframe(classes_df)
        else:
            st.warning("No classes available for this branch.")
        
        if not students_df.empty:
            st.subheader("Students Information")
            st.dataframe(students_df)
        else:
           st.warning("No students available for this branch")
        
        if not subjects_df.empty:
           st.subheader("Subjects Information")
           st.dataframe(subjects_df)
        else:
            st.warning("No subjects available for this branch.")
        
        if not chapters_df.empty:
            st.subheader("Chapters Information")
            st.dataframe(chapters_df)
        else:
            st.warning("No chapters available for this branch.")
        
        if not topics_df.empty:
            st.subheader("Topics Information")
            st.dataframe(topics_df)
        else:
             st.warning("No topics available for this branch")

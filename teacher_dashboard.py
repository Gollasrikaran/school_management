import streamlit as st
from database import load_data, create_connection
import pandas as pd
import plotly.express as px

def update_topic_status(topic_id, status):
    conn = create_connection("school.db")
    try:
        with conn:
            conn.execute("UPDATE topics_name SET status = ? WHERE id = ?", (status, topic_id))
    except Exception as e:
        st.error(f"Error updating status: {e}")

def teacher_dashboard():
    st.title("Teacher Dashboard")

    # Get the current user role and name from session
    user_role = st.session_state.role
    user_name = st.session_state.username

    if user_role != "teacher":
        st.error("You do not have access to this page.")
        return

    # Add branch selection
    branch_name = st.sidebar.radio("Select Branch", ["Malakpet", "Dilshuknagar"])
    
    st.write(f"Welcome, {user_name}!")
    st.write(f"Your selected branch is: {branch_name}")
    st.write("This is your teacher dashboard.")

    # Fetch data for the selected branch
    if branch_name:
        # Fetch unique class numbers
        classes_query = f"SELECT DISTINCT class FROM Students WHERE branch_id IN (SELECT id FROM Schools WHERE branch_name = '{branch_name}')"
        classes_df = load_data(classes_query)
        if not classes_df.empty:
            class_options = sorted(classes_df['class'].tolist())
            selected_class = st.selectbox("Select Class", options=class_options, key = "class_select")
            
             # Fetch unique sections for the selected class
            sections_query = f"SELECT DISTINCT section FROM Students WHERE branch_id IN (SELECT id FROM Schools WHERE branch_name = '{branch_name}') AND class = '{selected_class}'"
            sections_df = load_data(sections_query)
            if not sections_df.empty:
                section_options = sorted(sections_df['section'].tolist())
                selected_section = st.selectbox("Select Section", options=section_options, key = "section_select")
                
                # Fetch students for the selected class and section
                students_query = f"SELECT * FROM Students WHERE branch_id IN (SELECT id FROM Schools WHERE branch_name = '{branch_name}') AND class = '{selected_class}' AND section = '{selected_section}'"
                students_df = load_data(students_query)
                if not students_df.empty:
                    student_options = students_df['student_name'].tolist()
                    selected_student = st.selectbox("Select Student", options=student_options, key = "student_select")
                     # Fetch student information
                    student = students_df[students_df['student_name'] == selected_student].iloc[0]
                    st.write(f"**Student Name:** {student['student_name']}, **Class:** {student['class']}, **Section:** {student['section']}")
                     #Fetch Topics for the student
                    topics_query = f"""
                       SELECT t.id as topic_id, t.topic_name, t.status, c.chapter_name, s.subject_name
                       FROM topics_name t
                       JOIN chapters_name c ON t.chapter_name = c.chapter_name
                       JOIN subject_names s ON t.subject_name = s.subject_name
                       JOIN Students st ON st.branch_id IN (SELECT id FROM Schools WHERE branch_name = '{branch_name}')
                       WHERE t.branch_name = '{branch_name}'
                       AND t.chapter_name IN (SELECT chapter_name FROM chapters_name WHERE subject_name IN (SELECT subject_name FROM subject_names WHERE branch_name = '{branch_name}'))
                       AND st.id = '{student['id']}'
                     """
                    topics_df = load_data(topics_query)
                    if not topics_df.empty:
                        st.write("   **Topics:**")
                        for topic_index, topic in topics_df.iterrows():
                            topic_id = topic['topic_id']
                            status = topic['status']
                            student_id = student['id']
                            key = f"topic_{student_id}_{topic_id}"  # Unique key: student_id + topic id

                            # Create a unique key for the checkbox, default value to status
                            completed = st.checkbox(f"   {topic['topic_name']} (Chapter: {topic['chapter_name']}, Subject: {topic['subject_name']})", value = status == 'completed', key=key,
                               on_change = update_topic_status, args = (topic_id, 'completed' if status == 'not completed' else 'not completed'))
                            
                    else:
                        st.write("   No topics available for this student")
                     # Load data for visualizations
                    all_students_query = f"SELECT id, student_name FROM Students WHERE branch_id IN (SELECT id FROM Schools WHERE branch_name = '{branch_name}')"
                    all_students_df = load_data(all_students_query)

                    all_topics_query = f"""
                       SELECT t.id as topic_id, t.topic_name, t.status, c.chapter_name, s.subject_name, st.student_name
                       FROM topics_name t
                       JOIN chapters_name c ON t.chapter_name = c.chapter_name
                       JOIN subject_names s ON t.subject_name = s.subject_name
                       JOIN Students st ON st.branch_id IN (SELECT id FROM Schools WHERE branch_name = '{branch_name}')
                       WHERE t.branch_name = '{branch_name}'
                       AND t.chapter_name IN (SELECT chapter_name FROM chapters_name WHERE subject_name IN (SELECT subject_name FROM subject_names WHERE branch_name = '{branch_name}'))
                    """
                    all_topics_df = load_data(all_topics_query)

                    if not all_topics_df.empty:
                         #Bar Chart: Topic Status Count
                        status_counts = all_topics_df['status'].value_counts().reset_index()
                        status_counts.columns = ['Status', 'Count']
                        fig_bar = px.bar(status_counts, x='Status', y='Count', title='Topic Status Count')
                        st.plotly_chart(fig_bar)
                        
                        #Line Chart: Completion Trend
                        completion_trend = all_topics_df.groupby('student_name')['status'].apply(lambda x: (x == 'completed').sum()).reset_index()
                        completion_trend.columns = ['Student', 'Completed Topics']
                        fig_line = px.line(completion_trend, x='Student', y='Completed Topics', title = 'Topic Completion Trend')
                        st.plotly_chart(fig_line)
                            
                        # Pie Chart: Percentage of Students Completing All Topics
                        student_topic_counts = all_topics_df.groupby('student_name')['topic_name'].count().reset_index()
                        student_topic_counts.columns = ['Student', 'Total Topics']
                        completed_topic_counts = all_topics_df[all_topics_df['status'] == 'completed'].groupby('student_name')['topic_name'].count().reset_index()
                        completed_topic_counts.columns = ['Student', 'Completed Topics']
                        
                        merged_data = pd.merge(student_topic_counts, completed_topic_counts, on='Student', how='left')
                        merged_data['Completed Topics'] = merged_data['Completed Topics'].fillna(0)
                        
                        
                        merged_data['All Completed'] = merged_data.apply(lambda row : "Yes" if row['Total Topics'] > 0 and row['Total Topics'] == row['Completed Topics'] else "No", axis = 1)
                        
                        all_completed_counts = merged_data['All Completed'].value_counts().reset_index()
                        all_completed_counts.columns = ['All Completed', 'Count']
                        fig_pie = px.pie(all_completed_counts, values='Count', names='All Completed', title='Percentage of Students Completing All Topics')
                        st.plotly_chart(fig_pie)
                        
                        # Scatter Plot: Topic completion for every student
                        fig_scatter = px.scatter(all_topics_df, x = 'student_name', y = 'topic_name', color = 'status', title = 'Topic completion for every student')
                        st.plotly_chart(fig_scatter)
                        
                    else:
                         st.write("No Data to display charts.")
                else:
                   st.warning("No students available for this class and section.")
            else:
                st.warning("No sections available for this class.")
        else:
           st.warning("No classes available for this branch.")

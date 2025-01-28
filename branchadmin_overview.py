import streamlit as st
import pandas as pd
import plotly.express as px
from database import load_data

def display_branchadmin_overview(branch_name):
    st.header(f"Branch Admin Overview - {branch_name}")

    # Load data
    teachers_query = f"SELECT COUNT(*) as count FROM Teachers WHERE branch_name = '{branch_name}'"
    classes_query = f"SELECT COUNT(*) as count FROM Classes WHERE branch_id IN (SELECT id FROM Schools WHERE branch_name = '{branch_name}')"
    students_query = f"SELECT COUNT(*) as count FROM Students WHERE branch_id IN (SELECT id FROM Schools WHERE branch_name = '{branch_name}')"
    subjects_query = f"SELECT COUNT(*) as count FROM subject_names WHERE branch_name = '{branch_name}'"
    chapters_query = f"SELECT COUNT(*) as count FROM chapters_name WHERE branch_name = '{branch_name}'"
    topics_query = f"SELECT COUNT(*) as count FROM topics_name WHERE branch_name = '{branch_name}'"

    teachers_df = load_data(teachers_query)
    classes_df = load_data(classes_query)
    students_df = load_data(students_query)
    subjects_df = load_data(subjects_query)
    chapters_df = load_data(chapters_query)
    topics_df = load_data(topics_query)

    # Extract counts from dataframes
    teacher_count = teachers_df['count'].iloc[0] if not teachers_df.empty else 0
    class_count = classes_df['count'].iloc[0] if not classes_df.empty else 0
    student_count = students_df['count'].iloc[0] if not students_df.empty else 0
    subject_count = subjects_df['count'].iloc[0] if not subjects_df.empty else 0
    chapter_count = chapters_df['count'].iloc[0] if not chapters_df.empty else 0
    topic_count = topics_df['count'].iloc[0] if not topics_df.empty else 0

    # Display Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Teachers", teacher_count)
    col2.metric("Classes", class_count)
    col3.metric("Students", student_count)

    col4, col5, col6, _ = st.columns(4)
    col4.metric("Subjects", subject_count)
    col5.metric("Chapters", chapter_count)
    col6.metric("Topics", topic_count)

    # Prepare data for visualizations
    data = {
        'Category': ['Teachers', 'Classes', 'Students', 'Subjects', 'Chapters', 'Topics'],
        'Count': [teacher_count, class_count, student_count, subject_count, chapter_count, topic_count]
    }

    df = pd.DataFrame(data)

    # Create Bar Chart
    fig_bar = px.bar(df, x='Category', y='Count', title='Overview of Data Counts')
    st.plotly_chart(fig_bar)

    # Create Pie Chart
    fig_pie = px.pie(df, names='Category', values='Count', title='Data Distribution')
    st.plotly_chart(fig_pie)
    
    # Load data for additional visualizations
    teachers_data = load_data(f"SELECT teacher_name, subject FROM Teachers WHERE branch_name = '{branch_name}'")
    students_data = load_data(f"SELECT student_name, class, section FROM Students WHERE branch_id IN (SELECT id FROM Schools WHERE branch_name = '{branch_name}')")
    classes_data = load_data(f"SELECT class, section FROM Classes WHERE branch_id IN (SELECT id FROM Schools WHERE branch_name = '{branch_name}')")


     # Create Bar Chart: Teachers per subject
    if not teachers_data.empty:
         teachers_per_subject = teachers_data.groupby('subject')['teacher_name'].count().reset_index()
         teachers_per_subject.columns = ['Subject Name', 'Number of Teachers']
         fig_teachers_subject = px.bar(teachers_per_subject, x='Subject Name', y='Number of Teachers', title='Number of Teachers per Subject')
         st.plotly_chart(fig_teachers_subject)
    else:
         st.write("No Teachers data to display chart.")
    
    # Create Scatter Plot: Students by class and section
    if not students_data.empty:
         fig_students_scatter = px.scatter(students_data, x='class', y='section', title='Students by Class and Section')
         st.plotly_chart(fig_students_scatter)
    else:
        st.write("No Students data to display chart.")

    # Create Scatter Plot: Classes by Class and Section
    if not classes_data.empty:
        fig_classes_scatter = px.scatter(classes_data, x='class', y='section', title='Classes by Class and Section')
        st.plotly_chart(fig_classes_scatter)
    else:
        st.write("No Classes data to display chart")

import streamlit as st
import pandas as pd
import plotly.express as px
from database import load_data

def display_superadmin_overview():
    st.header("Superadmin Overview")

    # Load data
    schools_df = load_data("SELECT COUNT(*) as count FROM Schools")
    teachers_df = load_data("SELECT COUNT(*) as count FROM Teachers")
    classes_df = load_data("SELECT COUNT(*) as count FROM Classes")
    students_df = load_data("SELECT COUNT(*) as count FROM Students")
    subjects_df = load_data("SELECT COUNT(*) as count FROM subject_names")
    chapters_df = load_data("SELECT COUNT(*) as count FROM chapters_name")
    topics_df = load_data("SELECT COUNT(*) as count FROM topics_name")
    branches_df = load_data("SELECT COUNT(DISTINCT branch_name) as count FROM Schools")


    # Extract counts from dataframes
    school_count = schools_df['count'].iloc[0] if not schools_df.empty else 0
    teacher_count = teachers_df['count'].iloc[0] if not teachers_df.empty else 0
    class_count = classes_df['count'].iloc[0] if not classes_df.empty else 0
    student_count = students_df['count'].iloc[0] if not students_df.empty else 0
    subject_count = subjects_df['count'].iloc[0] if not subjects_df.empty else 0
    chapter_count = chapters_df['count'].iloc[0] if not chapters_df.empty else 0
    topic_count = topics_df['count'].iloc[0] if not topics_df.empty else 0
    branch_count = branches_df['count'].iloc[0] if not branches_df.empty else 0


    # Display Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Schools", school_count)
    col2.metric("Teachers", teacher_count)
    col3.metric("Classes", class_count)
    col4.metric("Students", student_count)

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Subjects", subject_count)
    col6.metric("Chapters", chapter_count)
    col7.metric("Topics", topic_count)
    col8.metric("Branches", branch_count)

    # Prepare data for visualizations
    data = {
        'Category': ['Schools', 'Teachers', 'Classes', 'Students', 'Subjects', 'Chapters', 'Topics', 'Branches'],
        'Count': [school_count, teacher_count, class_count, student_count, subject_count, chapter_count, topic_count, branch_count]
    }

    df = pd.DataFrame(data)

    # Create Bar Chart
    fig_bar = px.bar(df, x='Category', y='Count', title='Overview of Data Counts')
    st.plotly_chart(fig_bar)

    # Create Pie Chart
    fig_pie = px.pie(df, names='Category', values='Count', title='Data Distribution')
    st.plotly_chart(fig_pie)
    
    # Load data for additional visualizations
    schools_data = load_data("SELECT name, branch_name FROM Schools")
    teachers_data = load_data("SELECT teacher_name, branch_name FROM Teachers")
    classes_data = load_data("SELECT class, section FROM Classes")
    
    # Create Bar Chart: Schools per Branch
    if not schools_data.empty:
         schools_per_branch = schools_data.groupby('branch_name')['name'].count().reset_index()
         schools_per_branch.columns = ['Branch Name', 'Number of Schools']
         fig_schools_branch = px.bar(schools_per_branch, x='Branch Name', y='Number of Schools', title='Number of Schools per Branch')
         st.plotly_chart(fig_schools_branch)
    else:
         st.write("No Schools data to display chart.")
    
    # Create Bar Chart: Teachers per Branch
    if not teachers_data.empty:
         teachers_per_branch = teachers_data.groupby('branch_name')['teacher_name'].count().reset_index()
         teachers_per_branch.columns = ['Branch Name', 'Number of Teachers']
         fig_teachers_branch = px.bar(teachers_per_branch, x='Branch Name', y='Number of Teachers', title='Number of Teachers per Branch')
         st.plotly_chart(fig_teachers_branch)
    else:
        st.write("No Teachers data to display chart")
   
    # Create Scatter Plot: Classes by Class and Section
    if not classes_data.empty:
       fig_classes_scatter = px.scatter(classes_data, x='class', y='section', title='Classes by Class and Section')
       st.plotly_chart(fig_classes_scatter)
    else:
        st.write("No Classes data to display chart")

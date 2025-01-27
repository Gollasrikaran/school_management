import streamlit as st
from database import authenticate_user

def login_form():
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")
    if login_button:
        user = authenticate_user(username, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.username = user[1] # Store username in session
            st.session_state.role = user[3] # Store user role in session
            st.success("Logged in successfully")
        else:
            st.error("Login failed. Please check your credentials.")

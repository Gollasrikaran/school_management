import sqlite3
import hashlib
import streamlit as st
import pandas as pd


def create_connection(db_name):
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row  # to access columns by name
    return conn


def create_users_table():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def add_user(username, password, role):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    try:
        cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, hashed_password, role))
        conn.commit()
        st.success(f"User {username} with role {role} added successfully!")
    except sqlite3.IntegrityError:
        st.error("Username already exists.")
    finally:
        conn.close()


def authenticate_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_password))
    user = cursor.fetchone()
    conn.close()
    return user


def create_school_tables():
    conn = create_connection("school.db")
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS Schools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT,
                branch_name TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS Teachers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_name TEXT NOT NULL,
                school_name TEXT NOT NULL,
                branch_name TEXT NOT NULL,
                subject TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS Classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                branch_id INTEGER,
                class INTEGER,
                section TEXT,
                no_of_students INTEGER,
                FOREIGN KEY (branch_id) REFERENCES Schools(id)
            )
        """)
        # Add the Students table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS Students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT NOT NULL,
                class INTEGER NOT NULL,
                section TEXT NOT NULL,
                branch_id INTEGER,
                FOREIGN KEY (branch_id) REFERENCES Schools(id)
            )
        """)
        # Add the subject_names table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS subject_names (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_name TEXT UNIQUE NOT NULL,
                branch_name TEXT,
                FOREIGN KEY (branch_name) REFERENCES Schools(branch_name)
            )
        """)
        # Add the chapters_name table with subject_name as reference
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chapters_name (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chapter_name TEXT NOT NULL,
                subject_name TEXT,
                branch_name TEXT,
                FOREIGN KEY (subject_name) REFERENCES subject_names(subject_name),
                FOREIGN KEY (branch_name) REFERENCES Schools(branch_name)
            )
        """)
         # Add the topics_name table with chapter_name and subject_name as reference
        conn.execute("""
            CREATE TABLE IF NOT EXISTS topics_name (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_name TEXT NOT NULL,
                chapter_name TEXT,
                subject_name TEXT,
                status TEXT DEFAULT 'not completed',
                branch_name TEXT,
                FOREIGN KEY (chapter_name) REFERENCES chapters_name(chapter_name),
                FOREIGN KEY (subject_name) REFERENCES subject_names(subject_name),
                FOREIGN KEY (branch_name) REFERENCES Schools(branch_name)
            )
        """)


def load_data(query):
    conn = create_connection("school.db")
    try:
        with conn:
            df = pd.read_sql_query(query, conn)
            return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

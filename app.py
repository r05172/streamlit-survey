import os
import mysql.connector
import re
import streamlit as st
import pandas as pd

# Read DATABASE_URL from environment
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    st.error("DATABASE_URL not set")
    st.stop()

# Parse DATABASE_URL
match = re.match(r"mysql://(.*?):(.*?)@(.*?):(\d+)/(.*)", DATABASE_URL)
user, password, host, port, database = match.groups()

# Connect to MySQL
conn = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database,
    port=int(port)
)

# Create table if it doesn't exist
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS survey_responses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    age INT,
    feedback TEXT
)
""")
conn.commit()

st.title("Survey App")

name = st.text_input("Your Name")
age = st.number_input("Your Age", 1, 100)
feedback = st.text_area("Your Feedback")

if st.button("Submit"):
    cursor.execute("INSERT INTO survey_responses (name, age, feedback) VALUES (%s, %s, %s)", (name, age, feedback))
    conn.commit()
    st.success("Response submitted!")

# Optional: Show dashboard
if st.checkbox("Show Dashboard"):
    cursor.execute("SELECT * FROM survey_responses")
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=["ID", "Name", "Age", "Feedback"])
    st.dataframe(df)

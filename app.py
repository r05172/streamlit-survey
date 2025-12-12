import os
import streamlit as st
import mysql.connector
from mysql.connector import Error

st.set_page_config(page_title="Survey App", layout="centered")

# --- DB connection ---
def get_conn():
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if not DATABASE_URL:
        st.error("DATABASE_URL not set.")
        st.stop()

    # Parse the URL if needed (or use directly)
    # Example: mysql://user:pass@host:port/dbname
    import re
    match = re.match(r"mysql://(.*?):(.*?)@(.*?):(\d+)/(.*)", DATABASE_URL)
    user, password, host, port, database = match.groups()

    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=int(port)
    )
    return conn

# --- Ensure table exists ---
def ensure_table():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS survey_responses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            age INT,
            q1 VARCHAR(255),
            q2 TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

# --- Insert response ---
def insert_response(name, age, q1, q2):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO survey_responses (name, age, q1, q2) VALUES (%s, %s, %s, %s)",
        (name, age, q1, q2)
    )
    conn.commit()
    cur.close()
    conn.close()

# --- Fetch latest responses ---
def fetch_latest(n=10):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM survey_responses ORDER BY created_at DESC LIMIT %s", (n,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# --- Streamlit UI ---
ensure_table()
st.title("Simple Survey (MySQL)")
st.write("Fill the survey below:")

with st.form("survey_form"):
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=1, max_value=120, step=1, value=18)
    q1 = st.radio("How often do you use your phone during meals?", ("Always", "Sometimes", "Never"))
    q2 = st.text_area("Additional comments (optional)")
    submitted = st.form_submit_button("Submit")

if submitted:
    insert_response(name, age, q1, q2)
    st.success("Response recorded!")

st.markdown("---")
st.subheader("Latest responses")
rows = fetch_latest()
for r in rows:
    st.write(f"**{r['name']}** ({r['age']}) — {r['q1']}")
    if r['q2']:
        st.write(r['q2'])
    st.write("_submitted:", r['created_at'], "_")

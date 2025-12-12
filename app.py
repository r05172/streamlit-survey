import os, re, mysql.connector, streamlit as st, pandas as pd

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    st.error("DATABASE_URL not set")
    st.stop()

# Parse MySQL URL
match = re.match(r"mysql://(.*?):(.*?)@(.*?):(\d+)/(.*)\?ssl-mode=REQUIRED", DATABASE_URL)
user, password, host, port, database = match.groups()

conn = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database,
    port=int(port),
    ssl_verify_cert=True
)

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

# Streamlit UI
st.title("Survey App (MySQL on Aiven)")

name = st.text_input("Your Name")
age = st.number_input("Your Age", 1, 100)
feedback = st.text_area("Your Feedback")

if st.button("Submit"):
    cursor.execute(
        "INSERT INTO survey_responses (name, age, feedback) VALUES (%s, %s, %s)",
        (name, age, feedback)
    )
    conn.commit()
    st.success("Response submitted!")

# Optional Dashboard
if st.checkbox("Show Dashboard"):
    cursor.execute("SELECT * FROM survey_responses")
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=["ID", "Name", "Age", "Feedback"])
    st.dataframe(df)

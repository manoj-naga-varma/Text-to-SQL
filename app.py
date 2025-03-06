from dotenv import load_dotenv
load_dotenv()  # Load environment variables

import streamlit as st
import os
import sqlite3
import google.generativeai as genai
import pandas as pd  # For better table display


# Configure Gemini API Key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to generate SQL query from user input
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content([prompt[0], question])
    return response.text.strip()  # Strip unnecessary whitespace

# Function to retrieve query from the database
def read_sql_query(sql, db):
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]  # Get column names
        conn.close()
        return rows, columns
    except sqlite3.Error as e:
        return str(e), []  # Return error message



# Streamlit App Configuration
st.set_page_config(page_title="SQL Query Generator", layout="wide")
st.title("🧠 Gemini-Powered SQL Query Generator")

# User input area
st.subheader("📌 Enter Your Query")
question = st.text_input("Write your question here:", key="input")

submit = st.button("🚀 Generate SQL & Fetch Data")

# Expanded prompt with 30+ diverse SQL examples
prompt = ["""
You are an expert in converting English questions into SQL queries.
The SQL database is named STUDENT and contains the following columns:
- NAME (VARCHAR)
- CLASS (VARCHAR)
- SECTION (VARCHAR)
- MARKS (INT)

Your task is to generate **only** the SQL query **without any explanations**.

### **Rules:**
1️⃣ Do **not** include 
in the beginning or end of the output.  
2️⃣ Do **not** include the word **SQL** in the output.  
3️⃣ Output only the **pure SQL query**.

### **Example Queries:**  

Q: How many students are in the database?  
A: SELECT COUNT(*) FROM STUDENT;  

Q: List students who have scored more than 80 marks.  
A: SELECT NAME FROM STUDENT WHERE MARKS > 80;  

Q: Show all students whose names contain the letter 'a'.  
A: SELECT * FROM STUDENT WHERE NAME LIKE "%a%";  

Q: Retrieve the top 3 students with the highest marks.  
A: SELECT NAME, MARKS FROM STUDENT ORDER BY MARKS DESC LIMIT 3;  

Q: Find students who have the same marks.  
A: SELECT MARKS, COUNT(*) FROM STUDENT GROUP BY MARKS HAVING COUNT(*) > 1;  

Q: Retrieve students from Class 10.  
A: SELECT * FROM STUDENT WHERE CLASS = '10';  

Q: Find students in Section B.  
A: SELECT * FROM STUDENT WHERE SECTION = 'B';  

Q: Get the student with the lowest marks.  
A: SELECT NAME, MARKS FROM STUDENT ORDER BY MARKS ASC LIMIT 1;  

Q: Retrieve students who scored exactly 75 marks.  
A: SELECT * FROM STUDENT WHERE MARKS = 75;  

Q: Count students who scored below 50.  
A: SELECT COUNT(*) FROM STUDENT WHERE MARKS < 50;  

Q: Retrieve students whose names end with 'n'.  
A: SELECT * FROM STUDENT WHERE NAME LIKE "%n";  

Q: Show students ordered by their names alphabetically.  
A: SELECT * FROM STUDENT ORDER BY NAME ASC;  

Q: Find the second highest marks in the database.  
A: SELECT DISTINCT MARKS FROM STUDENT ORDER BY MARKS DESC LIMIT 1 OFFSET 1;  

Q: Show all students except those in Class 12.  
A: SELECT * FROM STUDENT WHERE CLASS <> '12';  

Q: Retrieve students with marks between 60 and 90.  
A: SELECT * FROM STUDENT WHERE MARKS BETWEEN 60 AND 90;  

Q: Get students who have names with exactly 5 letters.  
A: SELECT * FROM STUDENT WHERE LENGTH(NAME) = 5;  

Q: Find students whose names contain either 'a' or 'e'.  
A: SELECT * FROM STUDENT WHERE NAME LIKE "%a%" OR NAME LIKE "%e%";  

Q: List students along with their class and section.  
A: SELECT NAME, CLASS, SECTION FROM STUDENT;  

Q: Retrieve students who scored in the top 5%.  
A: SELECT * FROM STUDENT WHERE MARKS >= (SELECT PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY MARKS) FROM STUDENT);  

Q: Find the total number of students in each section.  
A: SELECT SECTION, COUNT(*) FROM STUDENT GROUP BY SECTION;  

Now, given the following question, generate an SQL query **without explanations, without
 at the beginning or end, and without the word SQL in the output**.
"""]

# If submit button is clicked
if submit:
    with st.spinner("Generating SQL query... 💡"):
        sql_query = get_gemini_response(question, prompt)

    # Display the generated SQL query
    st.subheader("📝 Generated SQL Query:")
    st.code(sql_query, language="sql")

    # Execute SQL query and fetch data
    with st.spinner("Fetching data from the database... 🗄️"):
        response, columns = read_sql_query(sql_query, "student.db")

    # Display the results
    st.subheader("📊 Query Results:")

    if isinstance(response, str):  # Error handling
        st.error(f"❌ SQL Error: {response}")
    elif response:
        df = pd.DataFrame(response, columns=columns)
        st.dataframe(df)  # Display results in an interactive table
    else:
        st.warning("⚠️ No data found for the given query.")

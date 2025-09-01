import sqlite3
import json

# Connect to database
conn = sqlite3.connect('mcp2.db')
cursor = conn.cursor()

# Read the JSON data
with open('student_data.json', 'r') as file:
    student_data = json.load(file)

# Insert all records
for student in student_data:
    cursor.execute("""
        INSERT INTO students (name, roll_no, age, gender, address, contact_info)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        student['name'],
        student['roll_no'],
        student['age'],
        student['gender'],
        student['address'],
        student['contact_info']
    ))

# Commit changes and close connection
conn.commit()
conn.close()

print(f"Successfully inserted {len(student_data)} records into the database!")

import mysql.connector
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'CS631Project',
    'database': 'test_db1'
}

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

@app.route('/')
def index():
    # Fetch users from the database
    cursor.execute('SELECT * FROM pet')
    pets = cursor.fetchall()
    return render_template('index.html', pets=pets)
'''
def connect_to_database():
    # Establish a connection to the MySQL server
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="CS631Project",
        database="test_db1"
    )

def display_menu():
    print("1. View records")
    print("2. Add record")
    print("3. Update record")
    print("4. Delete record")
    print("5. Exit")

def view_records(cursor):
    # Execute SQL query to retrieve and display records
    cursor.execute("SHOW FULL TABLES;")
    records = cursor.fetchall()
    for record in records:
        print(record)

def add_record(cursor):
    # Implement logic to add a record to the database
    # You can prompt the user for input and execute an INSERT query 
    pass
    # Other functions for update_record, delete_record, etc.

def main():
    # Connect to the database
    connection = connect_to_database()
    cursor = connection.cursor()

    while True:
        display_menu()
        choice = input("Enter your choice: ")

        if choice == "1":
            view_records(cursor)
        elif choice == "2":
            add_record(cursor)
        # Add other choices and corresponding function calls

        elif choice == "5":
            break
        else:
            print("Invalid choice. Please try again.")

    # Close the connection when done
    cursor.close()
    connection.close()
'''
if __name__ == "__main__":
    app.run(debug=True)

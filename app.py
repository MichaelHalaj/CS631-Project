import mysql.connector
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'CS631Project',
    'database': 'onlinecomputerstore'
}

db_connection = mysql.connector.connect(**db_config)
cursor = db_connection.cursor()

@app.route('/')
def index():
    # Fetch users from the database
    cursor.execute('SELECT * FROM customer')
    pets = cursor.fetchall()
    return render_template('index.html', pets=pets)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        cursor = db_connection.cursor()
        cursor.execute("INSERT INTO customer (FName, LName, EMail, Address, Phone) VALUES (%s, %s, %s, %s, %s)",
                       (request.form['FName'], request.form['LName'], request.form['EMail'],
                        request.form['Address'], request.form['Phone']))
        db_connection.commit()
        cursor.close()
        return redirect(url_for('index'))
    return render_template('register.html')

if __name__ == "__main__":
    app.run(debug=True)

import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'CS631Project',
    'database': 'onlinecomputerstore'
}

db_connection = mysql.connector.connect(**db_config)
cursor = db_connection.cursor()

def is_logged_in():
    if not session.get("CID"):
        return redirect(url_for("login"))

@app.route('/')
def index():
    # Fetch users from the database
    is_logged_in()
    print(session)
    cursor.execute('SELECT * FROM customer')
    customers = cursor.fetchall()
    return render_template('index.html', customers=customers)

@app.route('/home')
def home():
    if not session.get("CID"):
        return redirect("login")
    cursor.execute('SELECT * FROM customer')
    customers = cursor.fetchall()
    return render_template('index.html', customers=customers)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        cursor = db_connection.cursor()
        query = "INSERT INTO customer (FName, LName, EMail, Address, Phone) VALUES (%s, %s, %s, %s, %s)"
        values = (request.form['FName'], request.form['LName'], request.form['EMail'], request.form['Address'], request.form['Phone'])
        cursor.execute(query, values)
        db_connection.commit()
        cursor.close()
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        query = "SELECT CID FROM customer WHERE Email = %s"
        values = (request.form['EMail'], )
        cursor.execute(query, values)
        user_cid = cursor.fetchone()
        if user_cid:
            session['CID'] = user_cid[0]
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/products', methods=['GET', 'POST'])
def products():
    is_logged_in()
    cursor = db_connection.cursor(dictionary = True)
    query = """SELECT * FROM PRODUCT P 
            JOIN COMPUTER C ON P.PID = C.PID 
            JOIN LAPTOP L ON C.PID = L.PID;
            """
    cursor.execute(query)
    #products = dict(zip(cursor.column_names, cursor.fetchone()))
    products = cursor.fetchall()

    query = """SELECT * FROM PRODUCT P
                JOIN COMPUTER C ON P.PID = C.PID
                WHERE P.PTYPE = 'COMPUTER'"""
    cursor.execute(query)
    computers = cursor.fetchall()

    return render_template('products.html', products = products, computers = computers)

if __name__ == "__main__":
    app.run(debug=True)
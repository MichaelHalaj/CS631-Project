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
        print('no cid')
        return False
    return True

@app.context_processor
def inject_user():
    return dict(user = is_logged_in())

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

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        cursor = db_connection.cursor()
        query = "INSERT INTO customer (FName, LName, EMail, Address, Phone) VALUES (%s, %s, %s, %s, %s)"
        values = (request.form['FName'], request.form['LName'], request.form['EMail'], request.form['Address'], request.form['Phone'])
        cursor.execute(query, values)
        cid = cursor.lastrowid # get last auto-increment column id

        query = """
                    INSERT INTO CREDIT_CARD 
                    (CCNumber, SecNumber, OwnerName, CCType, BilAddress, ExpDate, StoredCardCID)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
        values = (request.form['CCNumber'], 
                  request.form['SecNumber'], 
                  request.form['OwnerName'],
                  request.form['CCType'],
                  request.form['BilAddress'],
                  request.form['ExpDate'] + '-01', 
                  cid)
        cursor.execute(query, values)

        query = """INSERT INTO SHIPPING_ADDRESS (CID, SAName, RecipientName, Street, SNumber, City, Zip, State, Country)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        values = (cid,
                  request.form['SAName'], 
                  request.form['RecipientName'], 
                  request.form['Street'],
                  request.form['SNumber'],
                  request.form['City'],
                  request.form['Zip'],
                  request.form['State'],
                  request.form['Country'])
        cursor.execute(query, values)
        db_connection.commit()
        cursor.close()
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    cursor = db_connection.cursor(buffered=True)
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
    if not is_logged_in():
        return redirect(url_for('login'))
    cid = session.get("CID")
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

    query = """
            SELECT P.PNAME FROM BASKET B
            JOIN APPEARS_IN A ON B.BID = A.BID
            JOIN PRODUCT P ON P.PID = A.PID
            WHERE B.CID=%s
            """
    values = (cid, )
    cursor.execute(query, values)
    basket = cursor.fetchall()
    db_connection.commit()
    return render_template('products.html', products = products, computers = computers, basket = basket)

@app.route('/add_to_basket', methods=['POST'])
def add_to_basket():
    is_logged_in()
    if request.method == 'POST':
        cursor = db_connection.cursor()
        cid = session.get("CID")
        print(cid)
        query = """
                INSERT INTO BASKET (CID)
                VALUES (%s)
                """
        values = (cid, )
        cursor.execute(query, values)

        bid = cursor.lastrowid
        query = """
                INSERT INTO APPEARS_IN (BID, PID, Quantity, PriceSold)
                VALUES (%s, %s, %s, %s)
                """
        values = (bid,
                request.form['pid'],
                0,
                0)
        cursor.execute(query, values)
        db_connection.commit()
        return redirect(url_for('products'))
    return redirect(url_for('products'))

@app.route('/confirm_edit', methods=['POST'])
def confirm_edit():
    if not is_logged_in():
        return redirect(url_for('login'))
    cid = session.get("CID")
    query = """
            UPDATE CREDIT_CARD
            SET CCNumber = %s, 
            SecNumber = %s, 
            OwnerName = %s, 
            CCType = %s,
            BilAddress = %s, 
            ExpDate =%s 
            WHERE StoredCardCID = %s
            """
    values = (request.form['CCNumber'], 
                request.form['SecNumber'], 
                request.form['OwnerName'],
                request.form['CCType'],
                request.form['BilAddress'],
                request.form['ExpDate'] + '-01', 
                cid)
    cursor.execute(query, values)

    query = """UPDATE SHIPPING_ADDRESS  
            SET SAName = %s, 
            RecipientName = %s, 
            Street = %s, 
            SNumber = %s, 
            City = %s, 
            Zip = %s, 
            State = %s, 
            Country = %s
            WHERE CID = %s
            """
    values = (request.form['SAName'], 
                request.form['RecipientName'], 
                request.form['Street'],
                request.form['SNumber'],
                request.form['City'],
                request.form['Zip'],
                request.form['State'],
                request.form['Country'],
                cid)
    cursor.execute(query, values)
    return redirect(url_for('edit'))

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if not is_logged_in():
        return redirect(url_for('login'))
    cursor = db_connection.cursor(buffered=True, dictionary = True)
    cid = session.get('CID')
    query = """
            SELECT * FROM CREDIT_CARD
            WHERE StoredCardCID = %s
            """
    values = (cid, )
    cursor.execute(query, values)
    credit_card = cursor.fetchone()

    query = """
            SELECT * FROM SHIPPING_ADDRESS
            WHERE CID = %s
            """
    values = (cid, )
    cursor.execute(query, values)
    shipping_address = cursor.fetchone()
    return render_template('edit.html', credit_card = credit_card, shipping_address = shipping_address, cid = cid)

if __name__ == "__main__":
    app.run(debug=True)

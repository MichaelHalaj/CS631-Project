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
        query = "INSERT INTO customer (FName, LName, EMail, CAddress, Phone) VALUES (%s, %s, %s, %s, %s)"
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
            SELECT * FROM PRODUCT P
            JOIN PRINTER PR ON P.PID = PR.PID
            WHERE P.PTYPE = 'PRINTER'
            """
    cursor.execute(query)
    printers = cursor.fetchall()
    bid = session.get('BID')
    if session.get('BID'):

        query = """
                SELECT P.PID, P.PNAME, B.BID, SUM(A.QUANTITY) as Quantity FROM BASKET B
                JOIN APPEARS_IN A ON B.BID = A.BID
                JOIN PRODUCT P ON P.PID = A.PID
                WHERE B.CID=%s and B.BID = %s
                GROUP BY P.PID, P.PNAME, B.BID
                """
        values = (cid, bid)
        cursor.execute(query, values)
        basket = cursor.fetchall()
        db_connection.commit()
        return render_template('products.html', products = products, computers = computers, basket = basket, printers = printers)
    return render_template('products.html', products = products, computers = computers, printers = printers)

@app.route('/order_basket', methods=['POST'])
def order_basket():
    pass

@app.route('/add_to_basket', methods=['POST'])
def add_to_basket():
    is_logged_in()
    if request.method == 'POST':
        cursor = db_connection.cursor(buffered=True, dictionary=True)

        cid = session.get("CID")


        pid = request.form['pid']
        query = """
                SELECT P.PPRICE FROM PRODUCT P 
                WHERE P.PID = %s
                """
        values = (pid, )
        cursor.execute(query, values)
        priceDict = cursor.fetchone()
        price = priceDict['PPRICE']
        if not session.get("BID"):
            query = """
                    INSERT INTO BASKET (CID)
                    VALUES (%s)
                    """
            values = (cid, )
            cursor.execute(query, values)
            bid = cursor.lastrowid
            session["BID"] = bid
        
            query = """
                    INSERT INTO APPEARS_IN (BID, PID, Quantity, PriceSold)
                    VALUES (%s, %s, %s, %s)
                    """
            values = (bid,
                    pid,
                    1,
                    price)
            cursor.execute(query, values)
            db_connection.commit()
        else:
            bid = session.get("BID")
            query = """
                    INSERT INTO APPEARS_IN (BID, PID, Quantity, PriceSold)
                    VALUES(%s, %s, 1, %s)
                    ON DUPLICATE KEY UPDATE
                    QUANTITY = QUANTITY + 1, 
                    PRICESOLD = %s * QUANTITY
                    """
            values = (bid, pid, price, price)
            cursor.execute(query, values)
            db_connection.commit()
        return redirect(url_for('products'))
    return redirect(url_for('products'))

@app.route('/remove_from_basket', methods=['POST'])
def remove_from_basket():
    is_logged_in()
    if request.method == 'POST':
        cursor = db_connection.cursor(dictionary=True)
        query = """
                DELETE
                FROM APPEARS_IN
                WHERE BID=%s AND PID=%s
                """
        values = (request.form['bid'],
                  request.form['pid'])
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

@app.route('/prepare_purchase', methods=['POST'])
def prepare_purchase():
    if not is_logged_in():
        return redirect(url_for('login'))
    cursor = db_connection.cursor(buffered=True, dictionary = True)
    cid = session.get("CID")
    query = """
            SELECT *
            FROM CREDIT_CARD
            WHERE STOREDCARDCID=%s
            """
    values = (cid, )
    cursor.execute(query, values)
    credit_cards=cursor.fetchall()

    query = """
            SELECT *
            FROM SHIPPING_ADDRESS
            WHERE CID=%s
            """
    values = (cid, )
    cursor.execute(query, values)
    addrs=cursor.fetchall()
    query = """
            SELECT B.BID 
            FROM BASKET B
            WHERE B.CID=%s
            """
    values = (cid, )
    cursor.execute(query, values)
    bid = cursor.fetchone()
    query = """
            SELECT P.PNAME, A.PRICESOLD 
            FROM BASKET B
            JOIN APPEARS_IN A ON B.BID = A.BID
            JOIN PRODUCT P ON P.PID = A.PID
            WHERE B.CID=%s
            """
    values = (cid, )
    cursor.execute(query, values)
    basket = cursor.fetchall()

    return render_template('checkout.html',credit_cards=credit_cards,addresses=addrs,basket=basket, bid=bid)

def get_transactions():
    cid = session.get("CID")
    cursor = db_connection.cursor(dictionary=True)
    query = """
            SELECT * FROM TRANSACTIONS T
            WHERE T.CID = %s
            """
    values = (cid, )
    cursor.execute(query, values)
    transactions = cursor.fetchall()
    return transactions

@app.route('/transactions', methods=['GET', 'POST'])
def transactions():
    cursor = db_connection.cursor(dictionary=True)
    transactions = get_transactions()
    cid = session.get("CID")
    if request.method == 'POST':
        query = """
                SELECT * FROM TRANSACTIONS T
                WHERE T.CID = %s AND T.TDate BETWEEN %s and %s
                """
        values = (cid, request.form['start'], request.form['end'])
        cursor.execute(query, values)
        transactions_with_dates = cursor.fetchall()
        return render_template('transactions.html', transactions = transactions, transactions_with_dates = transactions_with_dates)
    return render_template('transactions.html', transactions = transactions)

@app.route('/process_purchase', methods=['POST'])
def process_purchase():
    if not is_logged_in():
        return redirect(url_for('login'))
    cid = session.get("CID")
    bid = session['BID']
    cursor = db_connection.cursor()
    query = "INSERT IGNORE INTO transactions (BID, CCNumber, CID, SAName, TDate, TTag) VALUES (%s, %s, %s, %s, CURDATE(), 'processed')"
    values = (bid, request.form['ccno'], cid, request.form['ship_addr'], )

    cursor.execute(query, values)
    db_connection.commit()
    cursor.close()
    session['BID'] = None
    return redirect(url_for('index'))
    

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

def fetch_statistics_1_and_2():
    cursor = db_connection.cursor(dictionary = True)
    query = """
            SELECT T.CCNumber, SUM(A.PriceSold) as Total_Charged
            FROM Transactions T
            JOIN BASKET B ON T.BID = B.BID
            JOIN APPEARS_IN A on B.BID = A.BID
            GROUP BY T.CCNumber
            """
    cursor.execute(query)
    total_per_card = cursor.fetchall()

    query = """
        SELECT C.CID, C.FNAME, C.LNAME, SUM(A.PriceSold) as Total_Charged
        FROM CUSTOMER C
        JOIN BASKET B ON C.CID = B.CID
        JOIN APPEARS_IN A on B.BID = A.BID
        JOIN Transactions T on B.BID = T.BID
        GROUP BY C.CID
        ORDER BY Total_Charged DESC
        LIMIT 10
        """
    cursor.execute(query)
    best_customers = cursor.fetchall()

    return total_per_card, best_customers

@app.route('/statistics', methods=['GET', 'POST'])
def statistics():
    cursor = db_connection.cursor(dictionary = True)
    total_per_card, best_customers = fetch_statistics_1_and_2()
    if request.method == 'POST':
        id = request.form.get('question')
        if id == 'q3':
            query = """
                    SELECT P.PID, P.PNAME, SUM(A.Quantity) as Quantity_Sold FROM PRODUCT P
                    JOIN APPEARS_IN A ON P.PID = A.PID
                    JOIN BASKET B ON A.BID = B.BID
                    JOIN TRANSACTIONS T ON B.BID = T.BID
                    WHERE T.TDate BETWEEN %s AND %s
                    GROUP BY P.PID
                    ORDER BY Quantity_Sold DESC
                    """
            values = (request.form['start1'], request.form['end1'])
            cursor.execute(query, values)
            frequently_sold = cursor.fetchall()
            return render_template('statistics.html', total_per_card = total_per_card, best_customers = best_customers, frequently_sold = frequently_sold)
        elif id == 'q4':
            query = """
                    SELECT P.PID, P.PNAME, COUNT(DISTINCT T.CID) AS Customer_Count FROM PRODUCT P
                    JOIN APPEARS_IN A ON P.PID = A.PID
                    JOIN BASKET B ON A.BID = B.BID
                    JOIN TRANSACTIONS T ON B.BID = T.BID
                    WHERE T.TDate BETWEEN %s AND %s
                    GROUP BY P.PID, P.PNAME
                    ORDER BY Customer_Count DESC
                    """
            values = (request.form['start2'], request.form['end2'])
            cursor.execute(query, values)
            distinct_customers = cursor.fetchall()
            return render_template('statistics.html', total_per_card = total_per_card, best_customers = best_customers, distinct_customers = distinct_customers)
        elif id == 'q5':
            query = """
                    SELECT C.CCNUMBER, MAX(TOTALPRICESOLD) as Max_Total
                    FROM (
                        SELECT T.CCNUMBER, B.BID, SUM(A.PRICESOLD) AS TOTALPRICESOLD
                        FROM TRANSACTIONS T
                        JOIN CREDIT_CARD C ON T.CCNUMBER = C.CCNUMBER
                        JOIN BASKET B ON T.BID = B.BID
                        JOIN APPEARS_IN A ON B.BID = A.BID
                        WHERE T.TDATE BETWEEN %s and %s
                        GROUP BY T.CCNUMBER, B.BID
                    ) AS C 
                    GROUP BY C.CCNUMBER 
                    """
            values = (request.form['start3'], request.form['end3'])
            cursor.execute(query, values)
            max_total = cursor.fetchall()
            return render_template('statistics.html', total_per_card = total_per_card, best_customers = best_customers, max_total = max_total)
        elif id == 'q6':
            query = """
                    SELECT A.PID, P.PTYPE, SUM(A.PRICESOLD) / SUM(A.QUANTITY) as Average_Price_Sold FROM APPEARS_IN A
                    JOIN BASKET B ON A.BID = B.BID
                    JOIN TRANSACTIONS T ON B.BID = T.BID
                    JOIN PRODUCT P ON A.PID = P.PID
                    WHERE T.TDATE BETWEEN %s AND %s
                    GROUP BY A.PTYPE
                    """
            values = (request.form['start4'], request.form['end4'])
            cursor.execute(query, values)
            avg_selling_price = cursor.fetchall()
            return render_template('statistics.html', total_per_card = total_per_card, best_customers = best_customers, avg_selling_price = avg_selling_price)

        return render_template('statistics.html', total_per_card = total_per_card, best_customers = best_customers)
    else:
        return render_template('statistics.html', total_per_card = total_per_card, best_customers = best_customers)
    

if __name__ == "__main__":
    app.run(debug=True)

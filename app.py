from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_session import Session
import db_config  # Your db_config should return MySQL connection

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn = db_config.get_connection()
        cursor = conn.cursor(dictionary=True)

        username = request.form['username']
        password = request.form['password']

        cursor.execute("SELECT * FROM Users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['username'] = user['username']
            return redirect(url_for('reports'))
        else:
            flash('Invalid login. Try again.')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/members', methods=['GET', 'POST'])
def members():
    conn = db_config.get_connection()
    cursor = conn.cursor(dictionary=True)
    data = None
    if request.method == 'POST':
        if 'add_member' in request.form:
            cursor.execute("INSERT INTO Member (name, flat_no, phone, email, join_date) VALUES (%s, %s, %s, %s, %s)",
                           (request.form['name'], request.form['flat_no'], request.form['phone'],
                            request.form['email'], request.form['join_date']))
            conn.commit()
            flash("Member added.")
        elif 'search_member' in request.form:
            cursor.execute("SELECT * FROM Member WHERE member_id = %s", (request.form['search_id'],))
            data = cursor.fetchone()
    conn.close()
    return render_template('members.html', member=data)

@app.route('/funds', methods=['GET', 'POST'])
def funds():
    conn = db_config.get_connection()
    cursor = conn.cursor(dictionary=True)
    data = None
    if request.method == 'POST':
        if 'add_fund' in request.form:
            cursor.execute("INSERT INTO Society_Fund (fund_type, amount, last_updated, description) VALUES (%s, %s, %s, %s)",
                           (request.form['fund_type'], request.form['amount'], request.form['last_updated'], request.form['description']))
            conn.commit()
            flash("Fund added.")
        elif 'search_fund' in request.form:
            cursor.execute("SELECT * FROM Society_Fund WHERE fund_id = %s", (request.form['search_id'],))
            data = cursor.fetchone()
    conn.close()
    return render_template('funds.html', fund=data)

@app.route('/payments', methods=['GET', 'POST'])
def payments():
    conn = db_config.get_connection()
    cursor = conn.cursor(dictionary=True)
    data = None
    if request.method == 'POST':
        if 'add_payment' in request.form:
            cursor.execute("INSERT INTO Payment (member_id, payment_date, amount, mode, reference_no, fund_id) VALUES (%s, %s, %s, %s, %s, %s)",
                           (request.form['member_id'], request.form['payment_date'], request.form['amount'],
                            request.form['mode'], request.form['reference_no'], request.form['fund_id']))
            conn.commit()
            flash("Payment recorded.")
        elif 'search_payment' in request.form:
            cursor.execute("SELECT * FROM Payment WHERE payment_id = %s", (request.form['search_id'],))
            data = cursor.fetchone()
    conn.close()
    return render_template('payments.html', payment=data)

@app.route('/expenses', methods=['GET', 'POST'])
def expenses():
    conn = db_config.get_connection()
    cursor = conn.cursor(dictionary=True)
    data = None
    if request.method == 'POST':
        if 'add_expense' in request.form:
            cursor.execute("INSERT INTO Expense (fund_id, category, amount, paid_to, expense_date, description) VALUES (%s, %s, %s, %s, %s, %s)",
                           (request.form['fund_id'], request.form['category'], request.form['amount'],
                            request.form['paid_to'], request.form['expense_date'], request.form['description']))
            conn.commit()
            flash("Expense added.")
    conn.close()
    return render_template('expenses.html', expense=data)

@app.route('/maintenance', methods=['GET', 'POST'])
def maintenance():
    conn = db_config.get_connection()
    cursor = conn.cursor(dictionary=True)
    data = None
    if request.method == 'POST':
        if 'add_maintenance' in request.form:
            cursor.execute("INSERT INTO Maintenance (member_id, complaint_type, description, status, created_on) VALUES (%s, %s, %s, %s, %s)",
                           (request.form['member_id'], request.form['complaint_type'], request.form['description'],
                            request.form['status'], request.form['created_on']))
            conn.commit()
            flash("Maintenance request added.")
        elif 'search_maintenance' in request.form:
            cursor.execute("SELECT * FROM Maintenance WHERE maintenance_id = %s", (request.form['search_id'],))
            data = cursor.fetchone()
    conn.close()
    return render_template('maintenance.html', maintenance=data)

@app.route('/reports')
def reports():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = db_config.get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total_members FROM Member")
    total_members = cursor.fetchone()['total_members']

    cursor.execute("SELECT IFNULL(SUM(amount), 0) AS total_funds FROM Society_Fund")
    total_funds = cursor.fetchone()['total_funds']

    cursor.execute("SELECT IFNULL(SUM(amount), 0) AS total_payments FROM Payment")
    total_payments = cursor.fetchone()['total_payments']

    cursor.execute("SELECT IFNULL(SUM(amount), 0) AS total_expenses FROM Expense")
    total_expenses = cursor.fetchone()['total_expenses']

    cursor.execute("SELECT COUNT(*) AS open_complaints FROM Maintenance WHERE status = 'Open'")
    open_complaints = cursor.fetchone()['open_complaints']

    conn.close()

    return render_template('reports.html',
                           total_members=total_members,
                           total_funds=total_funds,
                           total_payments=total_payments,
                           total_expenses=total_expenses,
                           open_complaints=open_complaints)

@app.route('/active-members')
def active_members():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = db_config.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM active_members_view")
    members = cursor.fetchall()
    conn.close()

    return render_template('active_members.html', members=members)

@app.route('/funds/summary')
def fund_summary():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = db_config.get_connection()
    cursor = conn.cursor()
    cursor.callproc('total_funds_collected')
    for result in cursor.stored_results():
        total = result.fetchone()[0]
    conn.close()

    return render_template('fund_summary.html', total=total)

@app.route('/complaints/open')
def open_complaints():
    if 'username' not in session:
        return redirect(url_for('login'))

    member_id = request.args.get('member_id')
    count = None

    if member_id:
        conn = db_config.get_connection()
        cursor = conn.cursor()
        cursor.callproc('count_open_complaints', [member_id])
        for result in cursor.stored_results():
            count = result.fetchone()[0]
        conn.close()

    return render_template('open_complaints.html', count=count, member_id=member_id)

if __name__ == '__main__':
    app.run(debug=True)

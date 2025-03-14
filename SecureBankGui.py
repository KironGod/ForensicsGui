from flask import Flask, render_template, request, redirect, url_for, flash
from bank_operations import BankAccount, register_user

import logging
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necessary for session handling and flash messages

# Initialize the bank account
bank_account = BankAccount()

# Homepage route
@app.route('/')
def index():
    return render_template('index.html')

# Create account route
@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        age = request.form['age']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        account_type = request.form['account_type']
        account_number = request.form['account_number']
        card_number = request.form['card_number']
        credit_score = request.form['credit_score']
        email = request.form['email']
        phone_number = request.form['phone_number']
        address = request.form['address']
        try:
            register_user(username, password, age, first_name, last_name, account_type, account_number, card_number, credit_score, email, phone_number, address)
            flash("Account created successfully")
            return redirect(url_for('index'))
        except Exception as e:
            flash(str(e))
            return redirect(url_for('create_account'))
    return render_template('create_account.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            bank_account.login(username, password)
            flash("Login successful")
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(str(e))
            return redirect(url_for('login'))
    return render_template('login.html')

# Dashboard route
@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    if not bank_account.logged_in_user:
        flash("Please log in to access the dashboard")
        return redirect(url_for('login'))
    
    balance = bank_account.getBalance()
    ledger_entries = []

    try:
        response = requests.get(f'http://192.168.87.103:1020/get_ledger', params={'username': bank_account.logged_in_user})
        response.raise_for_status()
        result = response.json()
        if result['success']:
            ledger_entries = result['ledger']
    except requests.RequestException as error:
        logging.error(f"Database error: {error}")

    return render_template('dashboard.html', balance=balance, ledger=ledger_entries)

# Logout route
@app.route('/logout')
def logout():
    try:
        bank_account.logout()
        flash("Logged out successfully")
    except Exception as e:
        flash(str(e))
    return redirect(url_for('index'))

# Deposit route
@app.route('/deposit', methods=['POST'])
def deposit():
    if not bank_account.logged_in_user:
        flash("Please log in to perform this operation")
        return redirect(url_for('login'))
    try:
        amount = float(request.form['amount'])
        bank_account.deposit(amount)
        flash("Deposit successful")
    except Exception as e:
        flash(str(e))
    return redirect(url_for('dashboard'))

# Withdraw route
@app.route('/withdraw', methods=['POST'])
def withdraw():
    if not bank_account.logged_in_user:
        flash("Please log in to perform this operation")
        return redirect(url_for('login'))
    try:
        amount = float(request.form['amount'])
        bank_account.withdraw(amount)
        flash("Withdrawal successful")
    except Exception as e:
        flash(str(e))
    return redirect(url_for('dashboard'))

# Make purchase route
@app.route('/make_purchase', methods=['POST'])
def make_purchase():
    if not bank_account.logged_in_user:
        flash("Please log in to perform this operation")
        return redirect(url_for('login'))
    try:
        name = request.form['name']
        price = float(request.form['price'])
        desc = request.form['desc']
        bank_account.make_purchase(name, price, desc)
        flash("Purchase successful")
    except Exception as e:
        flash(str(e))
    return redirect(url_for('dashboard'))

# Run the Flask app
if __name__ == '__main__':
    app.run(host="192.168.87.103", port=1020, debug=True)
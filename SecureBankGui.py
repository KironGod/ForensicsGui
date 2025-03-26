import logging
from flask import Flask, render_template, request, redirect, url_for, flash
from bank_operations import BankAccount, register_user
import requests

# Explicitly configure logging to output to the terminal
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Set the logging level
stream_handler = logging.StreamHandler()  # Create a StreamHandler for terminal output
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')  # Set log format
stream_handler.setFormatter(formatter)  # Apply the formatter to the handler
logger.addHandler(stream_handler)  # Add the handler to the logger

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
        try:
            register_user(
                username=request.form['username'],
                password=request.form['password'],
                age=request.form['age'],
                first_name=request.form['first_name'],
                last_name=request.form['last_name'],
                account_type=request.form['account_type'],
                account_number=request.form['account_number'],
                card_number=request.form['card_number'],
                credit_score=request.form['credit_score'],
                email=request.form['email'],
                phone_number=request.form['phone_number'],
                address=request.form['address']
            )
            flash("Account created successfully")
            return redirect(url_for('index'))
        except Exception as e:
            logging.error(f"Error creating account: {e}")
            flash(str(e))
            return redirect(url_for('create_account'))
    return render_template('create_account.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            bank_account.login(
                username=request.form['username'],
                password=request.form['password']
            )
            logging.info(f"User {request.form['username']} logged in successfully.")
            flash("Login successful")
            return redirect(url_for('dashboard'))
        except Exception as e:
            logging.error(f"Login error: {e}")
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
        response = requests.get(
            'http://192.168.87.21:5000/get_ledger',
            params={'username': bank_account.logged_in_user}
        )
        response.raise_for_status()
        result = response.json()
        if result['success']:
            balance = result['balance']
            ledger_entries = result['ledger']
            logging.info(f"Dashboard data retrieved for user {bank_account.logged_in_user}.")
        else:
            logging.warning(f"Failed to retrieve dashboard data for user {bank_account.logged_in_user}: {result.get('message')}")
    except requests.RequestException as error:
        logging.error(f"Request error in dashboard: {error}")
        flash("Failed to retrieve account data. Please try again later.")

    return render_template('dashboard.html', balance=balance, ledger=ledger_entries)

# Logout route
@app.route('/logout')
def logout():
    try:
        bank_account.logout()
        logging.info("User logged out successfully.")
        flash("Logged out successfully")
    except Exception as e:
        logging.error(f"Logout error: {e}")
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
        logging.info(f"User {bank_account.logged_in_user} deposited ${amount}.")
        flash("Deposit successful")
    except Exception as e:
        logging.error(f"Deposit error: {e}")
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
        logging.info(f"User {bank_account.logged_in_user} withdrew ${amount}.")
        flash("Withdrawal successful")
    except Exception as e:
        logging.error(f"Withdrawal error: {e}")
        flash(str(e))
    return redirect(url_for('dashboard'))

# Make purchase route
@app.route('/make_purchase', methods=['POST'])
def make_purchase():
    if not bank_account.logged_in_user:
        flash("Please log in to perform this operation")
        return redirect(url_for('login'))
    try:
        bank_account.make_purchase(
            name=request.form['name'],
            price=float(request.form['price']),
            desc=request.form['desc']
        )
        logging.info(f"User {bank_account.logged_in_user} made a purchase: {request.form['name']} for ${request.form['price']}.")
        flash("Purchase successful")
    except Exception as e:
        logging.error(f"Purchase error: {e}")
        flash(str(e))
    return redirect(url_for('dashboard'))

# Run the Flask app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

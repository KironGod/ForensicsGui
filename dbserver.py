from flask import Flask, request, jsonify
import sqlite3
import bcrypt
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)

@app.route('/save_ledger_entry', methods=['POST'])
def save_ledger_entry():
    data = request.json
    username = data['username']
    entry = data['entry']
    balance = data['balance']

    try:
        connect = sqlite3.connect('SecureBankDB.db')
        cursor = connect.cursor()
        query = """
        UPDATE users
        SET acctLedger = COALESCE(acctLedger, '') || ?, acctBalance = ?
        WHERE username = ?
        """
        cursor.execute(query, (entry + '\n', balance, username))
        connect.commit()
        return jsonify({'success': True})
    except sqlite3.Error as error:
        logging.error(f"SQLite error in save_ledger_entry: {error}")
        return jsonify({'success': False, 'error': str(error)})
    finally:
        if connect:
            connect.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']

    try:
        connect = sqlite3.connect('SecureBankDB.db')
        cursor = connect.cursor()
        query = "SELECT password, acctBalance, COALESCE(acctLedger, '') FROM users WHERE username = ?"
        cursor.execute(query, (username,))
        result = cursor.fetchone()

        if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
            return jsonify({
                'success': True,
                'balance': result[1],
                'ledger': result[2].split('\n') if result[2] else []
            })
        else:
            return jsonify({'success': False, 'message': 'Invalid username or password'})
    except sqlite3.Error as error:
        logging.error(f"SQLite error in login: {error}")
        return jsonify({'success': False, 'error': str(error)})
    finally:
        if connect:
            connect.close()

@app.route('/register_user', methods=['POST'])
def register_user():
    data = request.json
    username = data['username']
    password = data['password']
    age = data['age']
    first_name = data['first_name']
    last_name = data['last_name']
    account_type = data['account_type']
    account_number = data['account_number']
    card_number = data['card_number']
    credit_score = data['credit_score']
    email = data['email']
    phone_number = data['phone_number']
    address = data['address']

    try:
        connect = sqlite3.connect('SecureBankDB.db')
        cursor = connect.cursor()

        # Check if the username already exists
        cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            return jsonify({'success': False, 'message': 'Username already exists'})

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        query = """
        INSERT INTO users (username, password, age, first_name, last_name, account_type, account_number, card_number, credit_score, email, phone_number, address, acctBalance, acctLedger)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, '')
        """
        cursor.execute(query, (username, hashed_password, age, first_name, last_name, account_type, account_number, card_number, credit_score, email, phone_number, address))
        connect.commit()
        return jsonify({'success': True})
    except sqlite3.Error as error:
        logging.error(f"SQLite error in register_user: {error}")
        return jsonify({'success': False, 'error': str(error)})
    finally:
        if connect:
            connect.close()

@app.route('/get_ledger', methods=['GET'])
def get_ledger():
    username = request.args.get('username')

    try:
        connect = sqlite3.connect('SecureBankDB.db')
        cursor = connect.cursor()
        query = "SELECT acctBalance, COALESCE(acctLedger, '') FROM users WHERE username = ?"
        cursor.execute(query, (username,))
        result = cursor.fetchone()

        if result:
            balance, ledger = result
            return jsonify({
                'success': True,
                'balance': balance,
                'ledger': ledger.split('\n') if ledger else []
            })
        else:
            return jsonify({'success': False, 'message': 'User not found'})
    except sqlite3.Error as error:
        logging.error(f"SQLite error in get_ledger: {error}")
        return jsonify({'success': False, 'error': str(error)})
    finally:
        if connect:
            connect.close()

if __name__ == '__main__':
    app.run(host='192.168.87.21', port=5000, debug=True)





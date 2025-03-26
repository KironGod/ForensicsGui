# bank_operations.py

import os
import logging
import requests

# Configure logging
logging.basicConfig(
    filename='securebank.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Item:
    def __init__(self, name, price, desc):
        self.name = name
        self.price = price
        self.desc = desc

class BankAccount:
    def __init__(self):
        self.balance = 0
        self.ledger = []
        self.logged_in_user = None

    def _save_ledger_entry(self, entry):
        try:
            response = requests.post(
                'http://192.168.87.21:5000/save_ledger_entry',
                json={
                    'username': self.logged_in_user,
                    'entry': entry,
                    'balance': self.balance
                }
            )
            response.raise_for_status()
            result = response.json()
            if not result.get('success'):
                logging.error(f"Failed to save ledger entry: {result.get('error')}")
                raise Exception("Failed to save ledger entry to database")
        except requests.RequestException as error:
            logging.error(f"Request error in _save_ledger_entry: {error}")
            raise Exception("Failed to connect to server for ledger entry")

    def deposit(self, amount):
        if self.logged_in_user:
            self.balance += amount
            entry = f"Deposit: +${amount}"
            self.ledger.append(entry)
            self._save_ledger_entry(entry)
            logging.info(f"User {self.logged_in_user} deposited ${amount}.")
        else:
            raise Exception("Please log in to perform this operation.")

    def withdraw(self, amount):
        if self.logged_in_user:
            if self.balance >= amount:
                self.balance -= amount
                entry = f"Withdraw: -${amount}"
                self.ledger.append(entry)
                self._save_ledger_entry(entry)
                logging.info(f"User {self.logged_in_user} withdrew ${amount}.")
            else:
                raise Exception("Insufficient balance")
        else:
            raise Exception("Please log in to perform this operation.")

    def make_purchase(self, name, price, desc):
        if self.logged_in_user:
            if self.balance >= price:
                self.balance -= price
                entry = f"Purchase: -${price}, Item: {name}, Description: {desc}"
                self.ledger.append(entry)
                self._save_ledger_entry(entry)
                logging.info(f"User {self.logged_in_user} made a purchase: {name} for ${price}.")
            else:
                raise Exception("Insufficient balance")
        else:
            raise Exception("Please log in to perform this operation.")

    def login(self, username, password):
        try:
            response = requests.post(
                'http://192.168.87.21:5000/login',
                json={
                    'username': username,
                    'password': password
                }
            )
            response.raise_for_status()
            result = response.json()
            if result['success']:
                self.logged_in_user = username
                self.balance = result['balance']
                self.ledger = result['ledger']
                logging.info(f"User {username} logged in successfully.")
            else:
                logging.warning(f"Failed login attempt for username: {username}")
                raise Exception("Invalid username or password")
        except requests.RequestException as error:
            logging.error(f"Database error: {error}")
            raise Exception("Failed to connect to database")

    def logout(self):
        if self.logged_in_user:
            logging.info(f"User {self.logged_in_user} logged out.")
            self.logged_in_user = None
            self.balance = 0
            self.ledger = []
        else:
            raise Exception("No user is currently logged in.")

    def getBalance(self):
        return self.balance

def register_user(username, password, age, first_name, last_name, account_type, account_number, card_number, credit_score, email, phone_number, address):
    try:
        response = requests.post(
            'http://192.168.87.21:5000/register_user',
            json={
                'username': username,
                'password': password,
                'age': age,
                'first_name': first_name,
                'last_name': last_name,
                'account_type': account_type,
                'account_number': account_number,
                'card_number': card_number,
                'credit_score': credit_score,
                'email': email,
                'phone_number': phone_number,
                'address': address
            }
        )
        response.raise_for_status()
        result = response.json()
        if result['success']:
            logging.info(f"User {username} registered successfully.")
        else:
            raise Exception(result['message'])
    except requests.RequestException as error:
        logging.error(f"Database error: {error}")
        raise Exception("Failed to connect to database")


import sqlite3
import os
import logging

# Define the path to the database
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, 'SecureBankDB.db')

# Verify database and table
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        age INTEGER NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        account_type TEXT NOT NULL,
        account_number TEXT NOT NULL,
        card_number TEXT NOT NULL,
        credit_score INTEGER NOT NULL,
        email TEXT NOT NULL,
        phone_number TEXT NOT NULL,
        address TEXT NOT NULL,
        acctBalance REAL DEFAULT 0,
        acctLedger TEXT DEFAULT ''
    )
    ''')
    conn.commit()
    logging.info("Database and table verified successfully.")
except sqlite3.Error as error:
    logging.error(f"SQLite error during database verification: {error}")
finally:
    conn.close()

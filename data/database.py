import sqlite3
import os

# Ensure the data directory exists
if not os.path.exists('data'):
    os.makedirs('data')

# Connect to the database (this will create it if it doesn't exist)
conn = sqlite3.connect('data/cards.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Create a table for storing card information
cursor.execute('''
CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_number TEXT NOT NULL,
    expiration_date TEXT,
    cvv TEXT,
    cardholder_name TEXT,
    bin TEXT,
    issuer TEXT,
    card_type TEXT,
    country TEXT,
    import_date TEXT
)
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

print("cards.db has been created in the data/ directory with a 'cards' table.")
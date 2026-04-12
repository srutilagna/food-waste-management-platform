import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "food_waste.db")

conn = sqlite3.connect(db_path)

conn.execute('''
CREATE TABLE IF NOT EXISTS food_listings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    food_name TEXT,
    quantity TEXT,
    location TEXT,
    expiry_time TEXT,
    status TEXT,
    donor_name TEXT,
    donor_email TEXT,
    donor_phone TEXT
)
''')


conn.execute('''
CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    food_id INTEGER,
    receiver_name TEXT,
    receiver_email TEXT,
    status TEXT
)
''')

conn.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT
)
''')

conn.commit()
conn.close()

print("Database initialized successfully")
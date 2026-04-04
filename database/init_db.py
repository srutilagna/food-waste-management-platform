import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "../database/food_waste.db")

conn = sqlite3.connect(db_path)

conn.execute('''
CREATE TABLE IF NOT EXISTS food_listings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    food_name TEXT,
    quantity TEXT,
    location TEXT,
    expiry_time TEXT,
    status TEXT
)
''')

conn.commit()
conn.close()

print("Database created successfully")
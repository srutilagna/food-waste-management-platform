import sqlite3

conn = sqlite3.connect("food_waste.db")

conn.execute('''
CREATE TABLE food_listings (
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
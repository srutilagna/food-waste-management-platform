import sqlite3

def get_db():
    conn = sqlite3.connect("database/food_waste.db")
    conn.row_factory = sqlite3.Row
    return conn
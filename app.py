from flask import Flask, render_template, request, redirect
from database.db import get_db
import sqlite3
import os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/add", methods=["GET", "POST"])
def add_food():
    if request.method == "POST":
        food = request.form["food"]
        quantity = request.form["quantity"]
        location = request.form["location"]
        expiry = request.form["expiry"]

        db = get_db()
        db.execute(
            "INSERT INTO food_listings (food_name, quantity, location, expiry_time, status) VALUES (?, ?, ?, ?, ?)",
            (food, quantity, location, expiry, "Available")
        )
        db.commit()

        return redirect("/")

    return render_template("add_food.html")

@app.route("/list")
def list_food():
    location = request.args.get("location")

    db = get_db()

    if location:
        foods = db.execute(
            "SELECT * FROM food_listings WHERE location LIKE ? ORDER BY expiry_time ASC",
            ('%' + location + '%',)
        ).fetchall()
    else:
        foods = db.execute(
            "SELECT * FROM food_listings ORDER BY expiry_time ASC"
        ).fetchall()

    return render_template("listings.html", foods=foods)

@app.route("/request/<int:id>")
def request_food(id):
    db = get_db()
    db.execute("UPDATE food_listings SET status='Requested' WHERE id=?", (id,))
    db.commit()
    return redirect("/list")

@app.route("/complete/<int:id>")
def complete_food(id):
    db = get_db()
    db.execute(
        "UPDATE food_listings SET status = ? WHERE id = ?",
        ("Completed", id)
    )
    db.commit()
    return redirect("/list")


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "database", "food_waste.db")

def init_db():
    
    os.makedirs(os.path.join(BASE_DIR, "database"), exist_ok=True)

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
init_db()

if __name__ == "__main__":
    app.run()
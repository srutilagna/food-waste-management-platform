from flask import Flask, render_template, request, redirect
from database.db import get_db
import sqlite3
import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
import threading

load_dotenv()



app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "database", "food_waste.db")

# 🔹 Initialize DB
def init_db():
    os.makedirs(os.path.join(BASE_DIR, "database"), exist_ok=True)

    conn = sqlite3.connect(db_path)

    # Food table
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

    # Requests table
    conn.execute('''
    CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        food_id INTEGER,
        receiver_name TEXT,
        receiver_email TEXT,
        status TEXT
    )
    ''')

    conn.commit()
    conn.close()

init_db()

# 🔹 Routes

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
        donor_name = request.form["donor_name"]
        donor_email = request.form["donor_email"]
        donor_phone = request.form["donor_phone"]

        db = get_db()
        db.execute(
            """INSERT INTO food_listings 
            (food_name, quantity, location, expiry_time, status, donor_name, donor_email, donor_phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (food, quantity, location, expiry, "Available", donor_name, donor_email, donor_phone)
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


def send_email(to_email, subject, body):
    sender_email = os.environ.get("EMAIL_USER")
    sender_password = os.environ.get("EMAIL_PASS")


    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        print("✅ Email sent successfully")
    except Exception as e:
        print("❌ Email error:", e)

# 🔹 Request food
@app.route("/request/<int:id>", methods=["GET", "POST"])
def request_food(id):
    if request.method == "POST":
       name = request.form["receiver_name"]
       email = request.form["receiver_email"]

       db = get_db()

    
       db.execute( "INSERT INTO requests (food_id, receiver_name, receiver_email, status) VALUES (?, ?, ?, ?)",
        (id, name, email, "Pending"))
    
       db.commit()

       food = db.execute("SELECT * FROM food_listings WHERE id = ?", (id,)).fetchone()

       subject = f"Food Request Received from {food['donor_name']}"
    
       body = f"""
        Hello {food['donor_name']},

        You have a new request for your food listing:

        Food: {food['food_name']}
        Receiver Name: {name}
        Receiver Email: {email}

        Please log in to your dashboard to accept the request.

        Thank you!
        """

       threading.Thread(target=send_email,args=(food["donor_email"], subject, body)).start()

       return redirect("/list")

    return render_template("request_food.html")


@app.route("/complete/<int:food_id>")
def complete_food(food_id):
    db = get_db()

    # mark food as completed
    db.execute(
        "UPDATE food_listings SET status = ? WHERE id = ?",
        ("Completed", food_id)
    )

    # update all related requests
    db.execute(
        "UPDATE requests SET status = ? WHERE food_id = ?",
        ("Completed", food_id)
    )

    db.commit()

    return redirect("/donor")

@app.route("/donor")
def donor_dashboard():
    db = get_db()

    requests = db.execute('''
        SELECT requests.*, food_listings.food_name 
        FROM requests
        JOIN food_listings ON requests.food_id = food_listings.id
    ''').fetchall()

    return render_template("donor_dashboard.html", requests=requests)


@app.route("/accept/<int:req_id>/<int:food_id>")
def accept_request(req_id, food_id):
    db = get_db()

    # mark selected request as Accepted
    db.execute(
        "UPDATE requests SET status = ? WHERE id = ?",
        ("Accepted", req_id)
    )

    # update food status
    db.execute(
        "UPDATE food_listings SET status = ? WHERE id = ?",
        ("Accepted", food_id)
    )

    db.commit()

    return redirect("/donor")

if __name__ == "__main__":
    app.run()
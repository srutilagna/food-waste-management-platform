from flask import Flask, render_template, request, redirect
from database.db import get_db

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
    db = get_db()
    foods = db.execute("SELECT * FROM food_listings ORDER BY expiry_time").fetchall()
    return render_template("listings.html", foods=foods)

@app.route("/request/<int:id>")
def request_food(id):
    db = get_db()
    db.execute("UPDATE food_listings SET status='Requested' WHERE id=?", (id,))
    db.commit()
    return redirect("/list")

if __name__ == "__main__":
    app.run(debug=True)
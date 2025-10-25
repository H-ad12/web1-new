import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///users.db")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Validate inputs
        if not email:
            return "Please add a email"
        if not password:
            return "Please add a password"
        if password != confirmation:
            return "Passwords don't match"

        rows = db.execute("SELECT * FROM users WHERE email = ?", email)
        if len(rows) > 0:
            return "eamil already exists"

        password_hash = generate_password_hash(password)
        db.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", email, password_hash)

        user_id = db.execute("SELECT id FROM users WHERE email = ?", email)[0]["id"]
        session["user_id"] = user_id
        return render_template("/loged.html")
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email:
            return "Must provide email", 403
        if not password:
            return "Must provide password", 403

        rows = db.execute("SELECT * FROM users WHERE email = ?", email)

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return "Invalid email and/or password", 403

        session["user_id"] = rows[0]["id"]

        return redirect("/")
    else:
        return render_template("login.html")


@app.route("/loged", methods=["GET"])
def loged():
    return render_template("loged.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

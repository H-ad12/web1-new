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
db = SQL("sqlite:///translink.db")

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
@app.route("/find", methods=["GET"])
def find():
    name_or_lang_search = request.args.get("name_or_lang_search", "").strip().lower()
    price_max = request.args.get("price_max")
    min_rating = request.args.get("min_rating")
    availability = request.args.get("availability")
    language_filter = request.args.get("language_filter")
    sort_by = request.args.get("sort_by")

    query = "SELECT * FROM translators WHERE 1=1"
    params = []

    if name_or_lang_search:
        query += " AND (LOWER(full_name) LIKE ? OR LOWER(language) LIKE ?)"
        params.append(f"%{name_or_lang_search}%")
        params.append(f"%{name_or_lang_search}%")

    if price_max and price_max.isdigit():
        query += " AND price_per_hour <= ?"
        params.append(price_max)

    if min_rating and min_rating not in ["", "0"]:
        query += " AND rating >= ?"
        params.append(min_rating)

    if language_filter and language_filter.lower() != "all":
        query += " AND LOWER(language) = ?"
        params.append(language_filter.lower())

    if availability and availability != "all":
        if availability == "available_now":
            query += " AND is_available = 1"
        elif availability == "available_this_week":
            query += " AND (availability = 'available_this_week' OR is_available = 1)"

    if sort_by:
        if sort_by == "highest_rated":
            query += " ORDER BY rating DESC"
        elif sort_by == "price_asc":
            query += " ORDER BY price_per_hour ASC"
        elif sort_by == "price_desc":
            query += " ORDER BY price_per_hour DESC"
        elif sort_by == "most_experience":
            query += " ORDER BY experience DESC"
        else:
            query += " ORDER BY rating DESC, experience DESC"
    else:
        query += " ORDER BY rating DESC"

    translators = db.execute(query, *params)

    return render_template(
        "find.html",
        translators=translators,
        name_or_lang_search=name_or_lang_search,
        price_max=price_max,
        min_rating=min_rating,
        availability=availability,
        language_filter=language_filter,
        sort_by=sort_by
    )
@app.route("/translator/<int:translator_id>")
def translator_profile(translator_id):
    translator = db.execute("SELECT * FROM translators WHERE id = ?", translator_id)

    if not translator:
        return "Translator not found", 404

    translator = translator[0]

    return render_template("translator_profile.html", translator=translator)

from flask import Flask, redirect,render_template,url_for,request,jsonify,flash,session,send_from_directory
from db import get_db_connection
import requests
from dotenv import load_dotenv
import os
import math
import psycopg
from psycopg.errors import UniqueViolation
from werkzeug.security import check_password_hash,generate_password_hash
from werkzeug.utils import secure_filename
from db import get_db_connection
from datetime import datetime,date,timedelta
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

from requests.exceptions import RequestException
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
load_dotenv()
from flask_wtf.csrf import CSRFProtect,generate_csrf
from rate_limiting import limiter
GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"


app = Flask(__name__,template_folder="templates",static_folder="static")
retry_strategy = Retry(
    total=2,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)

google_session = requests.Session()

adapter = HTTPAdapter(max_retries=retry_strategy)

google_session.mount("https://", adapter)
app.config["SECRET_KEY"] = os.environ["FLASK_SECRET_KEY"]

limiter.init_app(app)
print("Rate-limit storage:", limiter._storage_uri)

app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)
#identifies your application's filesystem location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#identifies the React production build directory.
REACT_DIST = os.path.join(BASE_DIR,"frontend","dist")
csrf = CSRFProtect(app)
GOOGLE_BOOKS_API_KEY = os.environ["GOOGLE_BOOKS_API_KEY"]


def validate_password(password):
    if len(password) < 8 :
        return "Password should contain more than 8 characters."

    if not any(char.isupper() for char in password):
        return "Password needs atleast 1 Upper case character"

    if not any(char.islower() for char in password):
        return "Password needs atleast 1 lower case character"

    if not any(char.isdigit() for char in password):
        return "Password needs atleast 1 or more numeric digits"

    if not any(not char.isalnum() for char in password):
        return "password needs atleast one special character"

    return None


@app.route("/api/get-csrf",methods=["GET"])
def get_csrfToken():
    return jsonify({
        "csrf_token": generate_csrf()
    })



@app.route("/bookworm/login", methods=["GET", "POST"])
@limiter.limit("3 per minute", methods=["POST"])
def login():
    if request.method == 'POST':
        value = request.form.get('input_value', "").strip()
        password = request.form.get('password', '')
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("select * from users where username = %s or phone = %s or email = %s",(value,value,value,))
                user = cursor.fetchone()

                if user is None:
                    flash('INCORRECT LOGIN DETAILS','error')
                    return redirect(url_for('login'))

                if user and check_password_hash(user['password_hash'],password):
                    session["user_id"] = user["user_id"]
                    session["username"] = user["username"]
                    session.permanent = True
                    flash('login success!', 'success')
                    return redirect(url_for('home'))
                else:
                    flash('Incorrect username or password', 'error')
                    return redirect(url_for('login'))

    return render_template("login.html")

@app.route('/bookworm/home')
def home():
    if "user_id" not in session:
        flash("Please login again, session expired", "error")
        return redirect(url_for("login"))
#send_from_directory() allows Flask to serve those frontend files to the browser.
    return send_from_directory(REACT_DIST,"index.html")


#Serving React's JavaScript and CSS
@app.route("/assets/<path:filename>")
def react_assets(filename):
    return send_from_directory(os.path.join(REACT_DIST,"assets"),filename)


#Serving the favicon
@app.route('/favicon.svg')
def freact_favicon():
    return send_from_directory(REACT_DIST,"favicon.svg")


@app.route('/bookworm/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.errorhandler(429)
def handle_rate_limit(error):

    if request.path == "/bookworm/login" or request.path == "/bookworm/register":
        return render_template(
            "login.html",
            rate_limit_error="Too many  attempts. Please try again later."
        ), 429
    if request.path.startswith("/api/"):
        return jsonify({
            "error": "Too many requests. Please try again later."
        }), 429

    return error


@app.route("/bookworm/register", methods=["GET", "POST"])
@limiter.limit("2 per minute", methods=["POST"])
def register():
    if request.method == 'POST':
        fullname = request.form.get('fullname',"").strip()
        username = request.form.get('username', "").strip()
        email = request.form.get('email',"").strip().lower()
        phone = request.form.get('phone',"").strip()
        password = request.form.get('password',"")

        if not fullname or not username or not email or not phone or not password:
            flash("FILL ALL FIELDS !!", "error")
            return redirect(url_for("register"))

        password_Response = validate_password(password)
        if password_Response:
            flash(password_Response,'error')
            return redirect(url_for('register'))

        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("select * from users where username = %s or phone = %s or email = %s",(username,phone,email,))
                existing_user = cursor.fetchone()
                if existing_user:
                    flash("Username, email, or phone already exists.", "error")
                    return redirect(url_for("register"))
                password_hash = generate_password_hash(password)

                cursor.execute("INSERT INTO users(username,password_hash,fullname,email,phone) VALUES(%s,%s,%s,%s,%s)",(username,password_hash,fullname,email,phone))
                connection.commit()
                flash('account successfully created', 'success')

                return redirect(url_for('login'))


    return render_template("register.html")





@app.route("/api/discover", methods=["GET"])
@limiter.limit("20 per minute")
def discover():

    # 1. Authentication
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401

    user_id = session["user_id"]

    # 2. Query parameters from JavaScript
    search_q = request.args.get("search", "").strip()
    order_by = request.args.get("orderby", "relevance")

    if order_by not in ("relevance", "newest"):
        order_by = "relevance"

    if not search_q:
        return jsonify({
            "all_books": [],
            "mybooks": []
        }), 200

    # 3. Google Books parameters
    params = {
        "q": search_q,
        "key": GOOGLE_BOOKS_API_KEY,
        "orderBy": order_by,
        "maxResults": 20
    }

    # 4. Call Google Books API
    try:
        response = google_session.get(
            GOOGLE_BOOKS_URL,
            params=params,
            timeout=10
        )

        app.logger.info(
            "Google Books status: %s",
            response.status_code
        )

        response.raise_for_status()

        data = response.json()

    except (RequestException, ValueError) as error:
        app.logger.exception(
            "Google Books API failed: %s",
            error
        )

        return jsonify({
            "error": "Google Books is temporarily unavailable"
        }), 502

    # 5. Extract required book information
    all_books = []
    myShelf = []


    # 6. Fetch existing reading statuses
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("select * from user_book_details where user_id = %s",(user_id,))    
                mybooks = cursor.fetchall()
                myShelf = [book["google_book_id"] for book in mybooks]


                for item in data.get("items", []):
                    info = item.get("volumeInfo") or {}

                    google_id = item.get("id")

                    if not google_id:
                        continue

                    if google_id in myShelf:
                        shelfStatus = True;
                    else:
                        shelfStatus = False

                    book = {
                        "google_book_id": google_id,
                        "title": info.get("title") or "Unknown title",
                        "authors": info.get("authors") or [],
                        "description": info.get("description") or "",
                        "cover_url": (
                            (info.get("imageLinks") or {}).get("thumbnail")
                        ),
                        "published_date": info.get("publishedDate"),
                        "categories": info.get("categories") or [],
                        "shelfStatus": shelfStatus
                    }

                    all_books.append(book)
                

    except psycopg.Error:
        app.logger.exception("Failed to retrieve user books")

        return jsonify({
            "error": "Unable to retrieve saved book statuses"
        }), 500

    # 7. Return JSON to JavaScript
    return jsonify({
        "all_books": all_books,
        "mybooks": mybooks
    }), 200


@app.route("/api/discover/addtoMybooks", methods=["POST"])
def addtomybooks():

    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401

    user_id = session["user_id"]

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON data"}), 400

    google_book_id = data.get("google_book_id")
    title = data.get("title")
    summary = data.get("summary") or ""
    image_url = data.get("image_url") or "/static/images/NA.png"

    if not isinstance(google_book_id, str) or not google_book_id.strip():
        return jsonify({"error": "Book ID is required"}), 400

    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "Book title is required"}), 400

    if not isinstance(summary, str) or not isinstance(image_url, str):
        return jsonify({"error": "Invalid book information"}), 400

    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:

                # 1. Insert book if it doesn't already exist
                cursor.execute("""
                    INSERT INTO books (
                        google_book_id,
                        title,
                        summary,
                        image_url
                    )
                    VALUES (%s, %s, %s, %s)

                    ON CONFLICT (google_book_id)
                    DO NOTHING
                """, (
                    google_book_id,
                    title[:200],
                    summary,
                    image_url
                ))

                # 2. Get the internal book_id
                cursor.execute("""
                    SELECT book_id
                    FROM books
                    WHERE google_book_id = %s
                """, (google_book_id,))

                result = cursor.fetchone()

                book_id = result["book_id"]

                # 3. Associate the book with the user
                cursor.execute("""
                    INSERT INTO user_books (
                        user_id,
                        book_id,
                        google_book_id,
                        reading_status
                    )
                    VALUES (%s, %s, %s,%s)
                    ON CONFLICT (user_id, google_book_id)
                    DO NOTHING                    
                """, (
                    user_id,
                    book_id,
                    google_book_id,
                    "ON MY BOOKS"
                ))

        return jsonify({
            "message": "Book successfully added to My Books"
        }), 200

    except psycopg.Error:
        app.logger.exception("Failed to add book")

        return jsonify({
            "error": "Unable to save book"
        }), 500


@app.route('/api/mybooks')
def mybooks():
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401

    user_id = session["user_id"]
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("select * from user_book_details where user_id = %s order by user_book_id",(user_id,))
            mybooks = cursor.fetchall()

            if not mybooks:
                return jsonify({"status": False})
            else:
                return jsonify({
                    "status": True,
                    "mybooks": mybooks
                })

@app.route("/api/mybooks/remove",methods=["POST"])
def remove_from_mybooks():
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401

    user_id = session["user_id"]

    data = request.get_json()
    google_book_id = data["google_book_id"]
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("select * from user_books where user_id = %s and google_book_id = %s",(user_id,google_book_id))
            result = cursor.fetchone()
            if not result:
                return jsonify({"error": "such a record does not exist"})
            try:
                cursor.execute("DELETE FROM user_books where user_id = %s and google_book_id= %s",(user_id,google_book_id))
                connection.commit()
                return jsonify({"success": "removed book "})
            except psycopg.Error:
                app.logger.exception("Failed to remove book")

                return jsonify({
                    "error": "Unable to remove book"
                }), 500


@app.route("/api/mybooks/status_change",methods=["PATCH"])
def status_change():
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401

    user_id = session["user_id"]

    data = request.get_json()
    google_book_id = data["google_book_id"]
    old_status = data["reading_status"]
    new_status = data["new_status"]
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("select * from user_books where user_id = %s and google_book_id = %s",(user_id,google_book_id))
            result = cursor.fetchone()
            if result["reading_status"] == new_status or result["reading_status"] != old_status:
                return jsonify({"error": "such a status not matching"})
            elif result["reading_status"] == old_status:
                try:
                    cursor.execute("UPDATE user_books set reading_status = %s where user_id = %s and google_book_id = %s",(new_status,user_id,google_book_id))
                    connection.commit()
                    return jsonify({"success": "updated status  "})
                except psycopg.Error:
                    app.logger.exception("Failed to update status")

                    return jsonify({
                        "error": "Unable to update status"
                    }), 500



if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)



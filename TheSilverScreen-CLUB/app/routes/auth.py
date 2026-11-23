# app/routes/auth.py
from flask import Flask, Blueprint,redirect,render_template,url_for,request,jsonify,flash,session
from models import db,users,tblmovies,tbltv,screenProfiles
import math
import psycopg
from psycopg.errors import UniqueViolation
from datetime import date,datetime,timedelta
import requests
from sqlalchemy import and_,or_,any_
from sqlalchemy.exc import IntegrityError
from config import Config
from app.extensions import limiter

auth_bp = Blueprint("auth", __name__)


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


@auth_bp.route("/TSSclub/login", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def login():
    if request.method == "POST":
        value = request.form.get("input_value", "").strip()
        password = request.form.get("password", "")

        stmt = db.select(users).where(
            or_(
                users.username == value,
                users.email == value.lower(),
                users.phoneNo == value
            )
        )

        user = db.session.execute(stmt).scalar_one_or_none()

        if user is None or not user.check_password(password):
            flash("Incorrect login details", "error")
            return redirect(url_for("auth.login"))

        session.clear()
        session["user_id"] = user.user_id
        session["username"] = user.username
        session.permanent = True

        flash("Login successful!", "success")
        return redirect(url_for("main.home"))

    return render_template("login.html")


@auth_bp.route("/TSSclub/register", methods=["GET", "POST"])
@limiter.limit("3 per hour", methods=["POST"])
def register():
    if request.method == "POST":
        fullname = request.form.get("fullname", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")

        if not all([fullname, username, email, phone, password]):
            flash("Fill all fields!", "error")
            return redirect(url_for("auth.register"))

        password_response = validate_password(password)

        if password_response:
            flash(password_response, "error")
            return redirect(url_for("auth.register"))

        stmt = db.select(users).where(
            or_(
                users.username == username,
                users.email == email,
                users.phoneNo == phone
            )
        )

        existing_users = db.session.execute(stmt).scalars().all()

        for existing_user in existing_users:
            if existing_user.username == username:
                flash("Username already exists", "error")
            elif existing_user.email == email:
                flash("Email already exists", "error")
            else:
                flash("Phone number already exists", "error")

            return redirect(url_for("auth.register"))

        user = users(
            fullname=fullname,
            username=username,
            email=email,
            phoneNo=phone
        )

        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()

        except IntegrityError:
            db.session.rollback()
            flash("Username, email or phone already exists", "error")
            return redirect(url_for("auth.register"))

        flash("Registration successful! Please do proceed with filling the members form.", "success")
        session.clear()
        session["user_id"] = user.user_id
        session["username"] = user.username
        session.permanent = True
        return redirect(url_for("auth.createProfile"))

    return render_template("register.html")




@auth_bp.route('/TSSclub/createProfile', methods=["GET", "POST"])
def createProfile():

    if "user_id" not in session:
        flash("Please login first.", "error")
        return redirect(url_for("auth.login"))

    if request.method == "POST":

        # FAVOURITES
        comfort_watch = request.form.get("comfort_watch", "").strip()
        quote_movie = request.form.get("quote_movie", "").strip()
        erase_memory = request.form.get("erase_memory", "").strip()
        soundtrack = request.form.get("soundtrack", "").strip()
        fav_actor = request.form.get("fav_actor", "").strip()
        fav_actress = request.form.get("fav_actress", "").strip()
        fav_villian = request.form.get("villain", "").strip()
        fav_director = request.form.get("fav_director", "").strip()
        cinephile_origin = request.form.get("cinefile-movie", "").strip()

        # MULTIPLE CHECKBOXES
        genres = request.form.getlist("genres")

        # OPINIONS
        overrated = request.form.get("overrated", "").strip()
        underrated = request.form.get("underrated", "").strip()
        guilty_pleasure = request.form.get("guilty_pleasure", "").strip()

        # RADIO BUTTONS
        book_vs_movie = request.form.get("book_vs_movie", "")
        watch_style = request.form.get("watch_style", "")
        subtitles = request.form.get("subtitles", "")

        # SELECT DROPDOWNS
        theatre_seat = request.form.get("theatre_seat", "")
        snack = request.form.get("snack", "")

        # RANGE SLIDER
        spoiler_tolerance = request.form.get("spoiler_tolerance", type=int)

        # MORE OPINIONS
        cried = request.form.get("cried", "").strip()
        plot_twist = request.form.get("plot_twist", "").strip()
        recommend = request.form.get("recommend", "").strip()

        # CREATE PROFILE OBJECT
        profile = screenProfiles(
            user_id=session["user_id"],
            comfort_watch=comfort_watch,
            quote_movie=quote_movie,
            erase_memory=erase_memory,
            soundtrack=soundtrack,
            fav_actor=fav_actor,
            fav_actress=fav_actress,
            fav_villian=fav_villian,
            fav_director=fav_director,
            cinephile_origin=cinephile_origin,
            genres=genres,
            overrated=overrated,
            underrated=underrated,
            guilty_pleasure=guilty_pleasure,
            book_vs_movie=book_vs_movie,
            watch_style=watch_style,
            subtitles=subtitles,
            theatre_seat=theatre_seat,
            snack=snack,
            spoiler_tolerance=spoiler_tolerance,
            cried=cried,
            plot_twist=plot_twist,
            recommend=recommend
        )

        try:
            db.session.add(profile)
            db.session.commit()

        except IntegrityError:
            db.session.rollback()
            flash("Profile already exists or could not be saved.", "error")
            return redirect(url_for("auth.createProfile"))

        flash("Screen profile created successfully!", "success")
        return redirect(url_for("main.home"))

    return render_template("profileForm.html")


@auth_bp.route('/TSSclub/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

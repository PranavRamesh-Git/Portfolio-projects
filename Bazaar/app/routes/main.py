from flask import Flask, Blueprint,redirect,render_template,url_for,request,jsonify,flash,session
from db import get_db_connection
import math
import psycopg
from psycopg.errors import UniqueViolation
from datetime import date,datetime,timedelta


main_bp = Blueprint("main",__name__)


@main_bp.route('/bazaar/home', methods=['GET','POST'])
def home():
    if "user_id" not in session:
        flash("Please login again, session expired", "error")
        return redirect(url_for("auth.login"))
    user_id = session["user_id"]

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("select * from brands")
            brands = cursor.fetchall()
            cursor.execute("select * from categories")
            categories = cursor.fetchall()                 
    return render_template('home.html',brands=brands,categories=categories)
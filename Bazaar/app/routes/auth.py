# app/routes/auth.py

from flask import (
    Blueprint, request, render_template,
    redirect, url_for, flash, session
)

from db import get_db_connection
from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)

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


@auth_bp.route("/bazaar/login", methods=["GET", "POST"])
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
                    return redirect(url_for('auth.login'))

                if user and check_password_hash(user['password_hash'],password):
                    session.clear()

                    session["user_id"] = user["user_id"]
                    session["username"] = user["username"]
                    session.permanent = True

                    if user['account_status'] == 'CUSTOMER':
                        session['accounr_status'] = 'CUSTOMER'
                        flash("Login successful!", "success")
                        return redirect(url_for("main.home"))
                    elif user['account_status'] == 'ADMIN':
                        session['account_status'] = 'ADMIN'
                        flash(" Admin Login successful!", "success")
                        return redirect(url_for("admin.home"))                        

                
                else:
                    flash('Incorrect username or password', 'error')
                    return redirect(url_for('auth.login'))

    return render_template("login.html")

@auth_bp.route("/bazaar/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        fullname = request.form.get('fullname',"").strip()
        username = request.form.get('username', "").strip()
        email = request.form.get('email',"").strip().lower()
        phone = request.form.get('phone',"").strip()
        password = request.form.get('password',"")

        if not fullname or not username or not email or not phone or not password:
            flash("FILL ALL FIELDS !!", "error")
            return redirect(url_for("auth.register"))

        password_Response = validate_password(password)
        if password_Response:
            flash(password_Response,'error')
            return redirect(url_for('auth.register'))

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

                return redirect(url_for('auth.login'))


    return render_template("register.html")

@auth_bp.route('/bazaar/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

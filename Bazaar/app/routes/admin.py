from flask import Flask, Blueprint,redirect,render_template,url_for,request,jsonify,flash,session
from db import get_db_connection
import math
import psycopg
from psycopg.errors import UniqueViolation
from datetime import date,datetime,timedelta



admin_bp = Blueprint("admin", __name__)


@admin_bp.route('/bazaar/admin/home', methods=['GET','POST'])
def home():
    if "user_id" not in session:
        flash("Please login again, session expired", "error")
        return redirect(url_for("auth.login"))
    
    if session.get("account_status") != "ADMIN":
        return "Forbidden", 403

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("select * from brands")
            brands = cursor.fetchall()
            cursor.execute("select * from categories")
            categories = cursor.fetchall()                 
    return render_template('admin_home.html',brands=brands,categories=categories),200

@admin_bp.route('/bazaar/admin/outofStock',methods=['GET'])
def display_outofstock():
    if "user_id" not in session:
        flash("Please login again, session expired", "error")
        return redirect(url_for("auth.login"))
    
    if session.get("account_status") != "ADMIN":
        return "Forbidden", 403
    user_id = session["user_id"]

    page = request.args.get('page',1,type=int)
    per_page = 18
    page = max(page,1)
    OFFSET = (page - 1) * per_page

    with get_db_connection() as connection:        
        with connection.cursor() as cursor:
            cursor.execute("select COUNT(*) as total FROM view_product_details where quantity = %s ",(0,))
            ans = cursor.fetchone()
            total = ans["total"]
            has_more = total > (per_page) * page

            cursor.execute("select *  FROM view_product_details where quantity = %s ORDER BY id ASC LIMIT %s OFFSET %s",(0,per_page,OFFSET))
            products = cursor.fetchall()
            product_ids = [product["id"] for product in products]

            if product_ids:
                cursor.execute("SELECT * FROM reviews WHERE product_id = ANY(%s)", (product_ids,))
                reviews = cursor.fetchall()
            else:
                reviews = []

            return jsonify({
                'products': products,
                'reviews': reviews,
                'has_more': has_more,
                'page': page,
                'per_page': per_page,
                'total': total
            }),200



@admin_bp.route('/bazaar/admin/Expired',methods=['GET'])
def display_expired():
    if "user_id" not in session:
        flash("Please login again, session expired", "error")
        return redirect(url_for("auth.login"))
    
    if session.get("account_status") != "ADMIN":
        return "Forbidden", 403
    user_id = session["user_id"]

    page = request.args.get('page',1,type=int)
    per_page = 18
    page = max(page,1)
    OFFSET = (page - 1) * per_page

    with get_db_connection() as connection:        
        with connection.cursor() as cursor:
            cursor.execute("select COUNT(*) as total  FROM view_product_details where expiry_date IS NULL OR expiry_date < CURRENT_DATE")
            ans = cursor.fetchone()
            total = ans["total"]
            has_more = total > (per_page) * page

            cursor.execute("select * FROM view_product_details where  expiry_date < CURRENT_DATE ORDER BY id ASC LIMIT %s OFFSET %s",(per_page,OFFSET))
            products = cursor.fetchall()
            product_ids = [product["id"] for product in products]

            if product_ids:
                cursor.execute("SELECT * FROM reviews WHERE product_id = ANY(%s)", (product_ids,))
                reviews = cursor.fetchall()
            else:
                reviews = []

            return jsonify({
                'products': products,
                'reviews': reviews,
                'has_more': has_more,
                'page': page,
                'per_page': per_page,
                'total': total
            }),200


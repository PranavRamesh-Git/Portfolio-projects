from flask import Flask, Blueprint,redirect,render_template,url_for,request,jsonify,flash,session,current_app
from db import get_db_connection
import math
import psycopg
from psycopg.errors import UniqueViolation
from datetime import date,datetime,timedelta


wishlist_bp = Blueprint("wishlist",__name__)


@wishlist_bp.route('/api/wishlist')
def wishlist():
    if "user_id" not in session:
        flash("Please login again, session expired", "error")
        return jsonify({"error": "Unauthorized"}), 401
    user_id = session["user_id"]


    with get_db_connection() as connection:
        with connection.cursor() as cursor:   
            cursor.execute("select product_id from wishlist where user_id = %s",(user_id,))
            result= cursor.fetchall()
            wishlist_items = [row["product_id"] for row in result]

            cursor.execute("select * from view_product_details")
            products = cursor.fetchall()


            cursor.execute("SELECT * FROM view_wishlist_reviews WHERE user_id = %s", (user_id,))
            wishlist_reviews = cursor.fetchall()
            return jsonify({
                'wishlist_items': wishlist_items,
                'products':  products,
                'wishlist_reviews': wishlist_reviews
            })

@wishlist_bp.route('/api/wishlist/add', methods=["POST"])
def add_to_wishlist():
    if "user_id" not in session:
        flash("Please login again, session expired", "error")
        return jsonify({"error": "Unauthorized"}), 401
    user_id = session["user_id"]           

    data = request.get_json()
    product_id = data["id"]
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute("select * from wishlist where product_id = %s and user_id = %s",(product_id,user_id,))
                result = cursor.fetchone()
                if not result:
                    cursor.execute("INSERT INTO wishlist(user_id,product_id) VALUES(%s,%s)",(user_id,product_id))
                    connection.commit()
                    return jsonify({
                        "message": "Product added to wishlist",
                        "product_id": product_id
                    }), 201                    
                else:
                    return jsonify({"error": "already there in wishlist"}),209
            except psycopg.Error:
                current_app.logger.exception("Failed to add book")

                return jsonify({
                    "error": "Unable to add book"
                }), 500
                

@wishlist_bp.route('/api/wishlist/remove', methods=["DELETE"])
def remove_from_wishlist():
    if "user_id" not in session:
        flash("Please login again, session expired", "error")
        return jsonify({"error": "Unauthorized"}), 401
    user_id = session["user_id"]

    
    data = request.get_json()
    product_id = data["id"]
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute("select * from wishlist where product_id = %s and user_id = %s",(product_id,user_id,))
                result = cursor.fetchone()
                if result:
                    cursor.execute("DELETE FROM wishlist WHERE product_id = %s AND user_id = %s RETURNING product_id", (product_id, user_id))

                    deleted = cursor.fetchone()

                    connection.commit()

                    if not deleted:
                        return jsonify({
                            "error": "Product not in wishlist"
                        }), 404

                    return jsonify({
                        "message": "Product removed from wishlist",
                        "product_id": product_id
                    }), 200

                else:
                    return jsonify({"error": "product not in wishlist"})
            except psycopg.Error:
                current_app.logger.exception("Failed to remove book")

                return jsonify({
                    "error": "Unable to remove book"
                }), 500

from flask import Flask, Blueprint,redirect,render_template,url_for,request,jsonify,flash,session,current_app
from db import get_db_connection
import math
import psycopg
from psycopg.errors import UniqueViolation
from datetime import date,datetime,timedelta
from decimal import Decimal, ROUND_HALF_UP

cart_bp = Blueprint("cart",__name__)


@cart_bp.route('/api/cart')
def get_cart():
    if "user_id" not in session:
        flash("Please login again, session expired", "error")
        return jsonify({"error": "Unauthorized"}), 401
    user_id = session["user_id"]

    with get_db_connection() as connection:
        with connection.cursor() as cursor:              
            cursor.execute("select * from view_cart_details where user_id = %s",(user_id,))
            cart_items = cursor.fetchall()
            cursor.execute("""
                SELECT COALESCE(ROUND(SUM(total_price), 2), 0) AS grand_total
                FROM view_cart_details
                WHERE user_id = %s
            """,(user_id,))
            result = cursor.fetchone()
            total = result["grand_total"]
            return jsonify({
                "cart_items": cart_items,
                "grand_total": total
            })     
          


@cart_bp.route('/api/cart_add', methods=["POST"])
def add_cart():

    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session["user_id"]

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON body"}), 400

    product_id = data.get("product_id")
    quantity = data.get("selected")

    if type(product_id) is not int or product_id <= 0:
        return jsonify({"error": "Invalid product ID"}), 400

    if type(quantity) is not int or quantity <= 0:
        return jsonify({"error": "Invalid quantity"}), 400

    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:

                cursor.execute("""
                    SELECT price, discount_percent, quantity
                    FROM products
                    WHERE id = %s
                """, (product_id,))

                product = cursor.fetchone()

                if not product:
                    return jsonify({
                        "error": "Product not found"
                    }), 404

                if quantity > product["quantity"]:
                    return jsonify({
                        "error": "Insufficient stock"
                    }), 409

                cursor.execute("""
                    INSERT INTO cart_items(
                        user_id,
                        product_id,
                        quantity_selected,
                        price,
                        discount_percent
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (user_id, product_id)
                    DO NOTHING
                    RETURNING id
                """, (
                    user_id,
                    product_id,
                    quantity,
                    product["price"],
                    product["discount_percent"]
                ))

                inserted = cursor.fetchone()

                if not inserted:
                    return jsonify({
                        "error": "Product already exists in cart"
                    }), 409

        return jsonify({
            "message": "Product added to cart",
            "product_id": product_id,
            "quantity": quantity
        }), 201

    except psycopg.Error:
        current_app.logger.exception("Failed to add cart")
        return jsonify({
            "error": "Unable to add cart"
        }), 500

@cart_bp.route('/api/cart_remove', methods=["DELETE"])
def remove_cart():

    if "user_id" not in session:
        return jsonify({"error": "Please login first"}), 401

    user_id = session["user_id"]

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON body"}), 400

    product_id = data.get("product_id")

    if type(product_id) is not int or product_id <= 0:
        return jsonify({"error": "Invalid product ID"}), 400

    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:

                cursor.execute("""
                    DELETE FROM cart_items
                    WHERE user_id = %s
                      AND product_id = %s
                    RETURNING id
                """, (user_id, product_id))

                deleted_item = cursor.fetchone()

                if not deleted_item:
                    return jsonify({
                        "error": "Product not found in cart"
                    }), 404

        return jsonify({
            "message": "Product removed from cart"
        }), 200

    except psycopg.Error:
        current_app.logger.exception("Failed to remove cart item")
        return jsonify({
            "error": "Unable to remove product from cart"
        }), 500






@cart_bp.route("/api/cart_edit", methods=["PATCH"])
def edit_cart():

    if "user_id" not in session:
        return jsonify({"error": "Please login first"}), 401

    user_id = session["user_id"]

    data = request.get_json(silent=True) or {}

    product_id = data.get("product_id")
    new_quantity = data.get("new_quantity")

    if type(product_id) is not int or product_id <= 0:
        return jsonify({"error": "Invalid product ID"}), 400

    if type(new_quantity) is not int or new_quantity <= 0:
        return jsonify({"error": "Invalid quantity"}), 400

    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:

                cursor.execute("""
                    SELECT quantity_selected, quantity
                    FROM view_cart_details
                    WHERE product_id = %s AND user_id = %s
                """, (product_id, user_id))

                result = cursor.fetchone()

                if not result:
                    return jsonify({
                        "error": "Product not found in cart"
                    }), 404

                if new_quantity > result["quantity"]:
                    return jsonify({
                        "error": "Insufficient stock"
                    }), 409

                if new_quantity == result["quantity_selected"]:
                    return jsonify({
                        "message": "Quantity unchanged"
                    }), 200

                cursor.execute("""
                    UPDATE cart_items
                    SET quantity_selected = %s
                    WHERE product_id = %s AND user_id = %s
                """, (new_quantity, product_id, user_id))

        return jsonify({
            "message": "Cart updated successfully"
        }), 200

    except psycopg.Error:
        current_app.logger.exception("Failed to update cart")
        return jsonify({
            "error": "Unable to update cart"
        }), 500

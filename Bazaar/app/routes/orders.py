from flask import Flask, Blueprint,redirect,render_template,url_for,request,jsonify,flash,session,current_app
from db import get_db_connection
import math
import psycopg
from psycopg.errors import UniqueViolation
from datetime import date,datetime,timedelta
from decimal import Decimal
from collections import defaultdict


orders_bp = Blueprint("orders",__name__)

@orders_bp.route('/api/orders')
def get_orders():
    if "user_id" not in session:
        flash("Please login again, session expired", "error")
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session["user_id"]

    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("select * from view_order_details where user_id = %s order by order_id desc",(user_id,))
                result = cursor.fetchall()
                orders_dict = defaultdict(list)
                for item in result:
                    orders_dict[item["order_id"]].append(item)

                return jsonify({
                    "orders_dict": orders_dict
                })               
  
    except psycopg.Error:
        current_app.logger.exception("Failed to place order")

        return jsonify({
            "error": "Unable to place order"
        }), 500    



@orders_bp.route("/api/orderPlace", methods=["POST"])
def place_order():

    if "user_id" not in session:
        return jsonify({"error": "Please login first"}), 401

    user_id = session["user_id"]

    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:

                # 1. Lock user to prevent simultaneous checkouts
                cursor.execute("""
                    SELECT user_id
                    FROM users
                    WHERE user_id = %s
                    FOR UPDATE
                """, (user_id,))

                if not cursor.fetchone():
                    return jsonify({"error": "User not found"}), 404


                # 2. Lock cart items
                cursor.execute("""
                    SELECT product_id
                    FROM cart_items
                    WHERE user_id = %s
                    ORDER BY product_id
                    FOR UPDATE
                """, (user_id,))

                product_ids = [
                    row["product_id"]
                    for row in cursor.fetchall()
                ]

                if not product_ids:
                    return jsonify({"error": "Cart is empty"}), 400


                # Lock products to prevent concurrent inventory changes
                cursor.execute("""
                    SELECT id
                    FROM products
                    WHERE id = ANY(%s)
                    ORDER BY id
                    FOR UPDATE
                """, (product_ids,))

                locked_products = cursor.fetchall()

                if len(locked_products) != len(product_ids):
                    return jsonify({
                        "error": "Some products are no longer available. Please update your cart."
                    }), 409


                # Fetch cart details from your existing view
                cursor.execute("""
                    SELECT
                        product_id,
                        product_name,
                        quantity_selected,
                        price,
                        discount_percent,
                        total_price,
                        availability_status
                    FROM view_cart_details
                    WHERE user_id = %s
                    ORDER BY product_id
                """, (user_id,))

                items = cursor.fetchall()


                # Validate current availability
                if not items:
                    return jsonify({"error": "Cart is empty"}), 400

                for item in items:

                    if item["availability_status"] != "AVAILABLE":
                        current_app.logger.warning(
                            "Checkout rejected: user_id=%s product_id=%s status=%s",
                            user_id,
                            item["product_id"],
                            item["availability_status"]
                        )

                        return jsonify({
                            "error": (
                                f"{item['product_name']} is "
                                f"{item['availability_status']}. "
                                "Please update your cart."
                            )
                        }), 409


                # Calculate the total
                total = sum(
                    (item["total_price"] for item in items),
                    Decimal("0.00")
                )


                # Create order
                cursor.execute("""
                    INSERT INTO orders (user_id, total_amount)
                    VALUES (%s, %s)
                    RETURNING id
                """, (user_id, total))

                order_id = cursor.fetchone()["id"]


                #  Insert order items
                for item in items:

                    cursor.execute("""
                        INSERT INTO order_items (
                            order_id,
                            product_id,
                            product_name,
                            unit_price,
                            discount_percent,
                            quantity,
                            line_total
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        order_id,
                        item["product_id"],
                        item["product_name"],
                        item["price"],
                        item["discount_percent"],
                        item["quantity_selected"],
                        item["total_price"]
                    ))


                # PostgreSQL trigger deducts stock here


                # Clear cart after successful order insertion
                cursor.execute("""
                    DELETE FROM cart_items
                    WHERE user_id = %s
                """, (user_id,))

        current_app.logger.info(
            "Order placed successfully: order_id=%s user_id=%s",
            order_id,
            user_id
        )

        return jsonify({
            "message": "Order placed successfully",
            "order_id": order_id
        }), 201


    except psycopg.errors.RaiseException as error:

        if "insufficient stock" in str(error).lower():
            current_app.logger.warning(
                "Checkout rejected due to insufficient stock: user_id=%s",
                user_id
            )

            return jsonify({
                "error": "Insufficient stock. Please update your cart."
            }), 409

        current_app.logger.exception("Order placement failed")

        return jsonify({
            "error": "Unable to place order"
        }), 500


    except psycopg.Error:

        current_app.logger.exception(
            "Order placement database error for user_id=%s",
            user_id
        )

        return jsonify({
            "error": "Unable to place order"
        }), 500

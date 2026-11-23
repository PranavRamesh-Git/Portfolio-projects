from flask import Flask, Blueprint,redirect,render_template,url_for,request,jsonify,flash,session,current_app
from db import get_db_connection
import math
import psycopg
from psycopg.errors import UniqueViolation
from datetime import date,datetime,timedelta
from decimal import Decimal, ROUND_HALF_UP

reviews_bp = Blueprint("reviews",__name__)


@reviews_bp.route("/api/reviews", methods=["POST"])
def add_review():

    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session["user_id"]

    data = request.get_json(silent=True) or {}

    product_id = data.get("product_id")
    rating = data.get("rating")
    review_text = data.get("review_text")
    order_id = data.get("order_id")

    if type(product_id) is not int or product_id < 1:
        return jsonify({"error": "Invalid product"}), 400

    if type(rating) is not int or not 1 <= rating <= 5:
        return jsonify({"error": "Rating must be between 1 and 5"}), 400

    if not isinstance(review_text, str) or not review_text.strip():
        return jsonify({"error": "Review text is required"}), 400

    if len(review_text.strip()) > 2000:
        return jsonify({"error": "Review text is too long"}), 400

    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("select * from orders where id=%s and user_id=%s",(order_id,user_id,))
                result = cursor.fetchone()
                if(not result):
                    is_verified = False
                else:
                    is_verified = True
                cursor.execute("select fullname  from users where user_id=%s",(user_id,))
                result = cursor.fetchone()
                reviewer_name = result["fullname"]
                if(not result):
                    is_verified = False
                else:
                    is_verified = True
                cursor.execute("""
                    INSERT INTO reviews (
                        product_id,
                        is_verified,
                        reviewer_name,
                        rating,
                        review_text
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    product_id,
                    is_verified,
                    reviewer_name,
                    rating,
                    review_text.strip()
                ))

                review_id = cursor.fetchone()["id"]

                return jsonify({
                    "message": "Review submitted",
                    "review_id": review_id
                }), 201

    except psycopg.Error:
        current_app.logger.exception("Failed to add review")
        return jsonify({"error": "Unable to submit review"}), 500


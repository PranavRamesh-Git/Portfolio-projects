# app/routes/products.py

from flask import (
    Blueprint, request, jsonify, session,
    redirect, url_for,flash
)

from db import get_db_connection

products_bp = Blueprint("products", __name__)



@products_bp.route('/api/products')
def get_products():
    if "user_id" not in session:
        flash("Please login again, session expired", "error")
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session["user_id"]

    search = request.args.get('search','').strip()
    brands = request.args.getlist('brands')
    categories = request.args.getlist('categories')
    sorting = request.args.get('sortby','').strip()
    page = request.args.get('page', 1, type=int)

    # CHANGED: Always filter unavailable or expired products
    conditions = [
        "quantity > %s",
        "(expiry_date IS NULL OR expiry_date >= CURRENT_DATE)"
    ]
    params = [0]

    per_page = 12
    page = max(page, 1)
    offset = (page - 1) * per_page

    if search:
        conditions.append("""
            (name ILIKE %s OR
            brand_name ILIKE %s OR
            category_name ILIKE %s)
        """)
        search_value = f"%{search}%"
        params.extend([search_value,search_value,search_value])

    if brands:
        conditions.append("""
            brand_name = ANY(%s)
        """)
        params.append(brands)

    if categories:
        conditions.append("""
            category_name = ANY(%s)
        """)
        params.append(categories)

    order_clause = ""
    if sorting:
        if sorting == 'avg_rating':
            order_clause = "ORDER BY avg_rating DESC, id ASC"

        elif sorting == 'price':
            order_clause = "ORDER BY price ASC, id ASC"

        elif sorting == 'discount_percent':
            order_clause = "ORDER BY discount_percent DESC, id ASC"

    if not order_clause:
        order_clause = "ORDER BY id ASC"

    # CHANGED: WHERE is always valid
    where_clause = "WHERE " + " AND ".join(conditions)

    # CHANGED: Copy parameters for paginated query
    product_params = params.copy()
    product_params.extend([per_page, offset])

    with get_db_connection() as connection:
        with connection.cursor() as cursor:

            query = f"""
                SELECT COUNT(*) AS total
                FROM view_product_details
                {where_clause}
            """
            cursor.execute(query, params)
            ans = cursor.fetchone()
            total = ans["total"]

            has_more = total > page * per_page

            query = f"""
                SELECT *
                FROM view_product_details
                {where_clause}
                {order_clause}
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, product_params)
            products = cursor.fetchall()

            product_ids = [product["id"] for product in products]

            if product_ids:
                cursor.execute("""
                    SELECT *
                    FROM reviews
                    WHERE product_id = ANY(%s)
                """, (product_ids,))
                reviews = cursor.fetchall()
            else:
                reviews = []

            cursor.execute("""
                SELECT *
                FROM cart_items
                WHERE user_id = %s
            """, (user_id,))
            cart_items = cursor.fetchall()

            cursor.execute("""
                SELECT product_id
                FROM wishlist
                WHERE user_id = %s
            """, (user_id,))
            result = cursor.fetchall()
            wishlist_items = [row["product_id"] for row in result]

            # Keep this for now because your JS modal uses allproducts.
            # We'll optimize it in a later step.
            cursor.execute("""
                SELECT *
                FROM view_product_details
            """)
            allproducts = cursor.fetchall()

            return jsonify({
                'products': products,
                'allproducts': allproducts,
                'reviews': reviews,
                'has_more': has_more,
                'page': page,
                'cart_items': cart_items,
                'wishlist_items': wishlist_items,
                'per_page': per_page,
                'total': total
            })

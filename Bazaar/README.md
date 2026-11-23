# Bazaar — Inventory-Aware E-Commerce & Order Management System

Bazaar is a full-stack e-commerce application built using **Python, Flask, PostgreSQL, JavaScript, HTML, and CSS**. It provides customer shopping workflows and admin inventory monitoring, with a focus on backend validation, reliable order processing, and database consistency.

## Key Features

**Customer Features**
- Secure user registration and session-based login with password hashing.
- Product discovery with search, filtering, sorting, and pagination.
- Shopping cart with quantity management, discounts, and calculated totals.
- Wishlist management and product availability indicators.
- Order placement and order history.
- Product ratings, reviews, and verified-purchase validation.

**Inventory & Admin Features**
- Admin-only views for out-of-stock and expired products.
- Availability checks before checkout.
- PostgreSQL transactions and row-level locking during order placement.
- Trigger-based inventory deduction.
- Automatic transaction rollback when order processing fails.

## Tech Stack

- **Backend:** Python, Flask, psycopg 3
- **Database:** PostgreSQL, SQL, views, triggers, transactions
- **Frontend:** HTML, CSS, JavaScript, Jinja2
- **Security:** Session authentication, password hashing, CSRF protection
- **Testing:** pytest, Flask test client, unittest.mock

## Technical Highlights

Bazaar emphasizes backend correctness through server-side validation, transactional checkout, concurrency-aware inventory management, and structured HTTP API responses.

The application prevents unavailable products from being purchased while preserving existing cart and wishlist entries for visibility.


Built to demonstrate practical Python backend engineering, relational database design, API development, and transactional business workflows.

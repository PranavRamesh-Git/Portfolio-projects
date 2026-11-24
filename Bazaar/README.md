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

## OUTPUT SCREENSHOTS
<img width="2941" height="1769" alt="image" src="https://github.com/user-attachments/assets/6043a7ce-3056-4301-84ff-678dbefb7e1e" />

<img width="2940" height="1743" alt="image" src="https://github.com/user-attachments/assets/f377c8ac-1892-4f3c-9d7a-55d8c0772c6a" />

<img width="2940" height="1660" alt="image" src="https://github.com/user-attachments/assets/028279fa-e198-492c-bb58-bc166938e7ce" />

<img width="2940" height="1768" alt="image" src="https://github.com/user-attachments/assets/caa19a67-ca6e-47b4-a06a-86d0f9e290d0" />

<img width="2940" height="1659" alt="image" src="https://github.com/user-attachments/assets/094a37f7-cd73-4313-9f0e-c2dc330e3d8f" />

## ADMIN VIEW 

<img width="2940" height="1697" alt="image" src="https://github.com/user-attachments/assets/9008cd97-b883-43f3-bd83-cd95447d7e36" />

<img width="2940" height="1672" alt="image" src="https://github.com/user-attachments/assets/0eda2c5d-afcd-4338-8f78-4222d750b7c1" />

<img width="2940" height="1666" alt="image" src="https://github.com/user-attachments/assets/6a24a901-f2d8-49a4-b886-a76e22d42ddd" />





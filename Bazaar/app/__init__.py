from flask import Flask
from config import Config
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()
def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.products import products_bp
    from app.routes.wishlist import wishlist_bp
    from app.routes.cart import cart_bp
    from app.routes.orders import orders_bp
    from app.routes.reviews import reviews_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(wishlist_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(admin_bp)

    csrf.init_app(app)
    return app
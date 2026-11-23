
# app.py

from flask import Flask, jsonify,request, render_template,flash,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from requests.exceptions import RequestException

from config import Config
from flask_wtf.csrf import CSRFProtect
from app.extensions import limiter, cache

from models import db

migrate = Migrate()

csrf = CSRFProtect()
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.discover import discover_bp
    from app.routes.library import library_bp
    from app.routes.social import social_bp
    from app.routes.recommendations import recommendations_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(discover_bp)
    app.register_blueprint(library_bp)
    app.register_blueprint(social_bp)
    app.register_blueprint(recommendations_bp)

    limiter.init_app(app)
    cache.init_app(app)
    csrf.init_app(app)

    @app.errorhandler(429)
    def rate_limit_exceeded(error):

        if request.path.startswith("/api/"):
            return jsonify({
                "error": "Too many requests. Please try again later."
            }), 429

        return render_template(
            "login.html",
            error_message="Too many attempts. Please try again later."
        ), 429 
    return app


app = create_app()
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()
#Python class containing Flask configuration values.
class Config:
    SECRET_KEY = os.environ["FLASK_SECRET_KEY"]

    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
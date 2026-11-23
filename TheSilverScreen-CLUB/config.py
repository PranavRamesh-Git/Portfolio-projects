import os
import requests

from datetime import timedelta
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv()


class Config:
    SECRET_KEY = os.environ["FLASK_SECRET_KEY"]

    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Enable this in production with HTTPS
    SESSION_COOKIE_SECURE = False

    TMDB_TOKEN = os.environ["TMDB_TOKEN"]

    TMDB_BASE_URL = "https://api.themoviedb.org/3"

    HEADERS = {
        "Authorization": f"Bearer {TMDB_TOKEN}",
        "accept": "application/json"
    }

    params = {
        "include_adult": "false",
    }


    paramsTV = {
        "include_adult": "false",
        "include_null_first_air_dates": "false"
    } 
    REDIS_URL = os.environ.get("REDIS_URL","redis://localhost:6379/0")

    RATELIMIT_STORAGE_URI = REDIS_URL

    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = REDIS_URL
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_KEY_PREFIX = "tss:cache:"       
    tmdb_session = requests.Session()

    retry_strategy = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)

    tmdb_session.mount("https://", adapter)
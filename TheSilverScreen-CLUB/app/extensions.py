from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache

from flask import session

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per hour"],
    key_prefix="tss:limit"
)

def user_or_ip():
    user_id = session.get("user_id")

    if user_id is not None:
        return f"user:{user_id}"

    return f"ip:{get_remote_address()}"

cache = Cache()



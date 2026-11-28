from flask import Flask, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


def test_rate_limiting():

    # independent Flask app for testing
    test_app = Flask(__name__)

    test_app.config["TESTING"] = True

    # Use in-memory storage instead of Redis
    limiter = Limiter(
        key_func=get_remote_address,
        storage_uri="memory://",
        default_limits=[]
    )

    limiter.init_app(test_app)

    @test_app.route("/test-api", methods=["GET"])
    @limiter.limit("3 per minute")
    def test_api():
        return jsonify({"message": "success"})

    client = test_app.test_client()

    # First three requests  succeed
    for i in range(3):
        response = client.get("/test-api")
        assert response.status_code == 200

    # Fourth request  blocked
    response = client.get("/test-api")

    assert response.status_code == 429
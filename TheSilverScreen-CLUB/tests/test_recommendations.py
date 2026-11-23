def test_get_recommendations_without_login(client):

    response = client.get("/api/getRecommendation")

    assert response.status_code == 401

    data = response.get_json()

    assert data["error"] == "Please login first"


def test_send_recommendation_without_login(client):

    response = client.post("/api/sendRecommendation")

    assert response.status_code == 401

    data = response.get_json()

    assert data["error"] == "Please login first"


def test_recommendation_form_without_login(client):

    response = client.post(
        "/api/recommendationForm",
        json={
            "tmdb_id": 550,
            "media_type": "movie"
        }
    )

    assert response.status_code == 401

    data = response.get_json()

    assert data["error"] == "Please login first"


def test_invalid_recommendation_media_type(client):

    # Simulate a logged-in user
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    # Send invalid data
    response = client.post(
        "/api/recommendationForm",
        json={
            "tmdb_id": 550,
            "media_type": "invalid",
            "title": "Test Movie"
        }
    )

    # Validate HTTP response
    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Invalid media type"
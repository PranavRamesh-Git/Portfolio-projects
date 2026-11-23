def test_empty_review(client):

    with client.session_transaction() as sess:
        sess["user_id"] = 1

    response = client.post(
        "/api/reviews",
        json={
            "product_id": 10,
            "rating": 5,
            "review_text": "   ",
            "order_id": None
        }
    )

    assert response.status_code == 400

    assert response.get_json()["error"] == "Review text is required"
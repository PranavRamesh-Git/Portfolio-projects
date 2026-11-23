def test_invalid_quantity(client):

    with client.session_transaction() as sess:
        sess["user_id"] = 1

    response = client.post(
        "/api/cart_add",
        json={
            "product_id": 10,
            "selected": 0
        }
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid quantity"
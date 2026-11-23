def test_requires_login(client):

    response = client.get("/api/cart")

    assert response.status_code == 401

    data = response.get_json()

    assert data["error"] == "Unauthorized"
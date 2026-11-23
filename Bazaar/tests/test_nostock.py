from unittest.mock import MagicMock, patch
import app.routes.cart as cart_routes


def test_insufficient_stock(client):


    connection = MagicMock()
    cursor = MagicMock()

    connection.__enter__.return_value = connection
    connection.cursor.return_value.__enter__.return_value = cursor

    cursor.fetchone.return_value = {
        "price": 150,
        "discount_percent": 10,
        "quantity": 3
    }

    with client.session_transaction() as sess:
        sess["user_id"] = 1

    with patch.object(
        cart_routes,
        "get_db_connection",
        return_value=connection
    ):
        response = client.post(
            "/api/cart_add",
            json={
                "product_id": 10,
                "selected": 10
            }
        )


    assert response.status_code == 409
    assert response.get_json()["error"] == "Insufficient stock"
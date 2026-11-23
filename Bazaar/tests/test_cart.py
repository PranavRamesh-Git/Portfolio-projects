from unittest.mock import patch,MagicMock
import app.routes.cart as cart_routes


def test_insufficient_stock(client, mock_db):

    connection, cursor = mock_db

    cursor.fetchone.return_value = {
        "id": 10,
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
            json={"product_id": 10, "selected": 10}
        )

    assert response.status_code == 409
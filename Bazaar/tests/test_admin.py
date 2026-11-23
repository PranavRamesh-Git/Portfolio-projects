def test_normal_user_cannot_access_admin(client):

    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["account_status"] = "USER"

    response = client.get(
        "/bazaar/admin/outofStock"
    )

    assert response.status_code == 403
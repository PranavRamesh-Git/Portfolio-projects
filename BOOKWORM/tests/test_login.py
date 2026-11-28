def test_login(client):
    response = client.get('/bookworm/home')
    assert response.status_code == 302

def test_login_user(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    response = client.get('/bookworm/home')
    assert response.status_code == 200


